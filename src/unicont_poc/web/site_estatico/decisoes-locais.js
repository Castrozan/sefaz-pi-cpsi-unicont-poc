const STORAGE_KEY = "unicont-poc.decisoes.v1";
const EVENT_TYPE = "decisao_do_analista";

export const REVIEW_LABELS = { aprovado: "Aprovado pelo analista", devolvido: "Devolvido pelo analista" };

export class DecisionRejected extends Error {}

export function loadDecisions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? [];
  } catch {
    return [];
  }
}

export function clearDecisions() {
  localStorage.removeItem(STORAGE_KEY);
}

export function decisionFor(processNumber) {
  return loadDecisions().find((decision) => decision.process_number === processNumber);
}

async function sha256Hex(text) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function canonicalJson(value) {
  return JSON.stringify(value, Object.keys(value).sort());
}

function entryHash(previousHash, processNumber, payload) {
  return sha256Hex(`${previousHash}|${EVENT_TYPE}|${processNumber}|${canonicalJson(payload)}`);
}

function rejectInvalidDecision({ processNumber, analystName, approve, finalOpinion, note }) {
  if (decisionFor(processNumber)) throw new DecisionRejected("Processo já decidido.");
  if (!analystName.trim()) throw new DecisionRejected("A decisão exige a identificação do analista.");
  if (approve && !finalOpinion.trim()) throw new DecisionRejected("A aprovação exige o texto do parecer.");
  if (!approve && !note.trim()) throw new DecisionRejected("A devolução exige justificativa.");
}

async function simulatedProtocol(process, payload) {
  const opinion = { ...payload, process_number: process.processNumber, checks: process.checks };
  return `SIMULADO-${(await sha256Hex(canonicalJson(opinion))).slice(0, 12).toUpperCase()}`;
}

export async function decide(process) {
  rejectInvalidDecision(process);
  const decisions = loadDecisions();
  const payload = {
    analysis_id: process.analysisId,
    analyst_name: process.analystName.trim(),
    decision: process.approve ? "aprovado" : "devolvido",
    note: process.note.trim(),
    edited_opinion: process.finalOpinion.trim() !== process.draft.trim(),
    final_opinion: process.finalOpinion,
    decided_at: new Date().toISOString(),
  };
  const previousHash = decisions.at(-1)?.entry_hash ?? process.ledgerHead;
  const decision = {
    sequence: process.ledgerEntryCount + decisions.length + 1,
    process_number: process.processNumber,
    nucleus_code: process.nucleusCode,
    previous_hash: previousHash,
    entry_hash: await entryHash(previousHash, process.processNumber, payload),
    protocol: process.approve ? await simulatedProtocol(process, payload) : null,
    payload,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...decisions, decision]));
  return decision;
}

export async function localChainIsIntact(ledgerHead) {
  let previousHash = ledgerHead;
  for (const decision of loadDecisions()) {
    const expectedHash = await entryHash(previousHash, decision.process_number, decision.payload);
    if (decision.previous_hash !== previousHash || decision.entry_hash !== expectedHash) return false;
    previousHash = decision.entry_hash;
  }
  return true;
}
