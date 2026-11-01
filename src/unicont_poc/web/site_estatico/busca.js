const RESULT_LIMIT = 50;
const SEARCH_DATABASE = "busca.sqlite.gz";
const FIELD_NAMES = ["texto", "tipo", "cnpj", "processo", "minimo", "maximo"];
const RESULT_HEADERS = ["Processo", "Documento", "Tipo", "Valor", "CNPJ", "Trecho"];

function ftsQuery(text) {
  const terms = text.match(/[\p{L}\p{N}_]+/gu) ?? [];
  return terms.map((term) => `"${term}"`).join(" ");
}

function parseAmount(text) {
  const cleaned = text.trim().replaceAll(".", "").replace(",", ".");
  const amount = Number(cleaned);
  return cleaned && !Number.isNaN(amount) ? amount : null;
}

function buildStatement(fields) {
  const clauses = [];
  const parameters = [];
  let source = "indexed_documents d";
  let snippet = "''";
  if (fields.texto.trim()) {
    source += " JOIN page_text p ON p.document_id = d.document_id";
    clauses.push("page_text MATCH ?");
    parameters.push(ftsQuery(fields.texto));
    snippet = "snippet(page_text, 2, '[[', ']]', ' … ', 18)";
  }
  for (const [column, value] of [
    ["d.document_type", fields.tipo],
    ["d.cnpj", fields.cnpj.trim()],
    ["d.process_number", fields.processo.trim()],
  ]) {
    if (value) {
      clauses.push(`${column} = ?`);
      parameters.push(value);
    }
  }
  for (const [comparison, value] of [
    ["d.amount >= ?", parseAmount(fields.minimo)],
    ["d.amount <= ?", parseAmount(fields.maximo)],
  ]) {
    if (value !== null) {
      clauses.push(comparison);
      parameters.push(value);
    }
  }
  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  const sql = `SELECT d.document_id, d.process_number, d.label, d.cnpj, d.amount, ${snippet} FROM ${source} ${where} LIMIT ?`;
  return { sql, bind: [...parameters, RESULT_LIMIT] };
}

async function downloadDatabase(assetDirectory) {
  const response = await fetch(`${assetDirectory}/${SEARCH_DATABASE}`);
  if (!response.ok) throw new Error(`índice indisponível: ${response.status}`);
  const decompressed = response.body.pipeThrough(new DecompressionStream("gzip"));
  return new Uint8Array(await new Response(decompressed).arrayBuffer());
}

async function openDatabase(bytes) {
  const { default: sqlite3InitModule } = await import("./vendor/sqlite-wasm-3.54.1/index.mjs");
  const sqlite3 = await sqlite3InitModule();
  const database = new sqlite3.oo1.DB();
  const pointer = sqlite3.wasm.allocFromTypedArray(bytes);
  const flags = sqlite3.capi.SQLITE_DESERIALIZE_FREEONCLOSE | sqlite3.capi.SQLITE_DESERIALIZE_RESIZEABLE;
  database.checkRc(
    sqlite3.capi.sqlite3_deserialize(database.pointer, "main", pointer, bytes.byteLength, bytes.byteLength, flags),
  );
  return database;
}

function moneyLabel(amount) {
  if (amount === null) return "—";
  const [whole, cents] = amount.toFixed(2).split(".");
  return `R$ ${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ".")},${cents}`;
}

function linkCell(text, href) {
  const cell = document.createElement("td");
  const link = document.createElement("a");
  link.href = href;
  link.textContent = text;
  cell.append(link);
  return cell;
}

function textCell(text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  return cell;
}

function snippetCell(snippet) {
  const cell = document.createElement("td");
  const small = document.createElement("small");
  snippet.split(/\[\[|\]\]/).forEach((piece, index) => {
    if (index % 2 === 0) {
      small.append(piece);
    } else {
      const mark = document.createElement("mark");
      mark.textContent = piece;
      small.append(mark);
    }
  });
  cell.append(small);
  return cell;
}

function resultRow([documentId, processNumber, label, cnpj, amount, snippet], base) {
  const row = document.createElement("tr");
  row.append(
    linkCell(processNumber, `${base}/processo/${processNumber.replace("/", "-")}/`),
    linkCell(documentId.slice(-3), `${base}/documento/${documentId}/`),
    textCell(label),
    textCell(moneyLabel(amount)),
    textCell(cnpj ?? "—"),
    snippetCell(snippet),
  );
  return row;
}

function resultTable(rows, base) {
  const table = document.createElement("table");
  const headerRow = table.createTHead().insertRow();
  for (const title of RESULT_HEADERS) {
    const header = document.createElement("th");
    header.textContent = title;
    headerRow.append(header);
  }
  const body = table.createTBody();
  rows.forEach((row) => body.append(resultRow(row, base)));
  return table;
}

function fillForm(form, fields) {
  for (const name of FIELD_NAMES) form.elements[name].value = fields[name];
}

function readFields() {
  const parameters = new URLSearchParams(location.search);
  return Object.fromEntries(FIELD_NAMES.map((name) => [name, parameters.get(name) ?? ""]));
}

export async function runSearchScreen() {
  const form = document.querySelector("form.busca");
  const status = document.getElementById("situacao-da-busca");
  const output = document.getElementById("resultados-da-busca");
  const base = document.body.dataset.base;
  const fields = readFields();
  if (!Object.values(fields).some(Boolean)) return;
  fillForm(form, fields);
  status.textContent = "Carregando o índice neste navegador…";
  try {
    const database = await openDatabase(await downloadDatabase(`${base}/estatico/site`));
    const started = performance.now();
    const rows = database.exec({ ...buildStatement(fields), rowMode: "array", returnValue: "resultRows" });
    const elapsed = (performance.now() - started).toFixed(1).replace(".", ",");
    status.textContent = `${rows.length} resultado(s) exibido(s) em ${elapsed} ms neste navegador`;
    output.replaceChildren(resultTable(rows, base));
  } catch (error) {
    console.error(error);
    status.textContent = "Não foi possível executar a busca. Use ao menos uma palavra na palavra-chave.";
  }
}
