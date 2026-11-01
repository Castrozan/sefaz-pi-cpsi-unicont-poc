import {
  clearDecisions,
  decide,
  decisionFor,
  DecisionRejected,
  loadDecisions,
  localChainIsIntact,
  REVIEW_LABELS,
} from "./decisoes-locais.js";

const QUEUE_FILTERS = { nucleo: "nucleo", risco: "risco", situacao: "situacao" };

function showClearButton() {
  const button = document.getElementById("limpar-decisoes");
  const count = loadDecisions().length;
  if (!count) return;
  button.textContent = `Limpar ${count} decisão(ões) simulada(s) neste navegador`;
  button.hidden = false;
  button.addEventListener("click", () => {
    clearDecisions();
    location.reload();
  });
}

function applyDecisionsToQueue(decisions) {
  const counter = document.querySelector("[data-contador-aguardando]");
  counter.textContent = Number(counter.textContent) - decisions.length;
  for (const row of document.querySelectorAll("tr[data-processo]")) {
    const decision = decisions.find((candidate) => candidate.process_number === row.dataset.processo);
    if (!decision) continue;
    row.dataset.situacao = decision.payload.decision;
    row.querySelector("[data-celula-situacao]").textContent = REVIEW_LABELS[decision.payload.decision];
  }
}

function filterQueue() {
  const parameters = new URLSearchParams(location.search);
  const form = document.querySelector("form.filtros");
  const rows = [...document.querySelectorAll("tr[data-processo]")];
  for (const name of Object.keys(QUEUE_FILTERS)) form.elements[name].value = parameters.get(name) ?? "";
  for (const row of rows) {
    row.hidden = Object.keys(QUEUE_FILTERS).some((name) => {
      const expected = parameters.get(name);
      return expected && row.dataset[name] !== expected;
    });
  }
  const visibleCount = rows.filter((row) => !row.hidden).length;
  form.querySelector(".contagem").textContent = `${visibleCount} processo(s)`;
}

function showQueueScreen() {
  applyDecisionsToQueue(loadDecisions());
  filterQueue();
}

function showDashboardScreen() {
  for (const decision of loadDecisions()) {
    const cell = document.querySelector(`[data-aguardando-nucleo="${CSS.escape(decision.nucleus_code)}"]`);
    if (cell) cell.textContent = Number(cell.textContent) - 1;
  }
}

function decisionSentence(decision) {
  const { analyst_name: analystName, decision: state, note } = decision.payload;
  const quotedNote = note ? `, “${note}”` : "";
  const protocol = decision.protocol ? ` Protocolo simulado ${decision.protocol}.` : "";
  return `${REVIEW_LABELS[state]} neste navegador: ${analystName}${quotedNote}.${protocol}`;
}

function showRecordedDecision(form, decision) {
  const sentence = document.getElementById("decisao-registrada");
  sentence.textContent = decisionSentence(decision);
  sentence.hidden = false;
  form.hidden = true;
}

function processFromForm(form, submitter) {
  const { dataset } = form;
  const codes = dataset.criterios.split(" ");
  const statuses = dataset.situacoes.split(" ");
  return {
    processNumber: form.elements.numero.value,
    analysisId: dataset.identificadorDaAnalise,
    nucleusCode: dataset.nucleo,
    ledgerHead: dataset.hashDaCadeia,
    ledgerEntryCount: Number(dataset.entradasDaCadeia),
    checks: codes.map((code, index) => ({ code, status: statuses[index] })),
    draft: form.elements.parecer.defaultValue,
    analystName: form.elements.analista.value,
    approve: submitter.value === "aprovar",
    finalOpinion: form.elements.parecer.value,
    note: form.elements.justificativa.value,
  };
}

async function submitDecision(form, submitter) {
  const failure = document.getElementById("erro-da-decisao");
  const success = document.getElementById("sucesso-da-decisao");
  failure.hidden = true;
  try {
    const decision = await decide(processFromForm(form, submitter));
    if (decision.protocol) {
      success.textContent = `Parecer aprovado neste navegador. Envio ao SINCIN+ simulado: nada saiu daqui. Protocolo ${decision.protocol}.`;
      success.hidden = false;
    }
    showRecordedDecision(form, decision);
    showClearButton();
  } catch (error) {
    if (!(error instanceof DecisionRejected)) throw error;
    failure.textContent = error.message;
    failure.hidden = false;
  }
}

function showProcessScreen() {
  const form = document.getElementById("formulario-de-decisao");
  const recorded = decisionFor(form.elements.numero.value);
  if (recorded) showRecordedDecision(form, recorded);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitDecision(form, event.submitter);
  });
}

function escapedPattern(text) {
  return new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "iu");
}

function highlightQuote(paragraph, quote) {
  const textNode = paragraph.firstChild;
  const match = textNode?.nodeValue.match(escapedPattern(quote));
  if (!match) return false;
  const quotedText = textNode.splitText(match.index);
  quotedText.splitText(match[0].length);
  const mark = document.createElement("mark");
  quotedText.replaceWith(mark);
  mark.append(quotedText);
  mark.id = "citacao";
  return true;
}

function showDocumentScreen() {
  const quote = new URLSearchParams(location.search).get("trecho");
  if (!quote) return;
  const found = [...document.querySelectorAll(".pagina p")].some((paragraph) => highlightQuote(paragraph, quote));
  if (found) document.getElementById("citacao").scrollIntoView();
}

function descriptionRow(list, term, description) {
  const termElement = document.createElement("dt");
  const descriptionElement = document.createElement("dd");
  termElement.textContent = term;
  descriptionElement.textContent = description;
  list.append(termElement, descriptionElement);
}

function localLedgerEntry(decision, isIntact) {
  const article = document.createElement("article");
  const title = document.createElement("h2");
  const list = document.createElement("dl");
  article.className = "pagina";
  title.textContent = `#${decision.sequence} Decisão do analista, simulada neste navegador`;
  descriptionRow(list, "Analista", decision.payload.analyst_name);
  descriptionRow(list, "Decisão", REVIEW_LABELS[decision.payload.decision]);
  descriptionRow(list, "Parecer editado", decision.payload.edited_opinion ? "Sim" : "Não");
  descriptionRow(list, "Hash da entrada", decision.entry_hash);
  descriptionRow(list, "Cadeia local", isIntact ? "Íntegra" : "VIOLADA");
  article.append(title, list);
  return article;
}

async function showAuditScreen() {
  const container = document.getElementById("registro-local");
  const decision = decisionFor(container.dataset.processo);
  if (!decision) return;
  const isIntact = await localChainIsIntact(container.dataset.hashDaCadeia);
  container.replaceChildren(localLedgerEntry(decision, isIntact));
}

async function showSearchScreen() {
  const { runSearchScreen } = await import("./busca.js");
  await runSearchScreen();
}

const SCREENS = {
  fila: showQueueScreen,
  painel: showDashboardScreen,
  processo: showProcessScreen,
  documento: showDocumentScreen,
  auditoria: showAuditScreen,
  busca: showSearchScreen,
};

showClearButton();
await SCREENS[document.body.dataset.tela]?.();
