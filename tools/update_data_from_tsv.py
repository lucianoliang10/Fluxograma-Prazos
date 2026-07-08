#!/usr/bin/env python3
"""Importa a planilha TSV de prazos para o array DATA em index.html.

Uso:
  python3 tools/update_data_from_tsv.py dados.tsv
  python3 tools/update_data_from_tsv.py dados.tsv --html index.html --updated-at 08/07/2026

O script aceita o TSV colado da planilha, remove uma repetição acidental do cabeçalho
quando ela aparece no meio do arquivo e preserva as colunas operacionais no JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

FIELD_MAP = {
    "Caso": "caso",
    "ID": "id",
    "Etapa": "etapa",
    "Origem": "origem",
    "Clube": "clube",
    "Série": "serie",
    "Ordem Etapa": "ordemLabel",
    "Objeto": "objeto",
    "Data de envio": "dataEnvio",
    "Prazo final": "prazoFinal",
    "Data de entrega": "dataEntrega",
    "Observação": "observacao",
    "Status Etapa": "statusEtapa",
    "Status Caso": "statusCaso",
    "Sanção": "sancao",
    "Doc": "doc",
    "Email responsável": "emailResponsavel",
    "Alertas enviados": "alertasEnviados",
    "Último alerta enviado em": "ultimoAlertaEnviadoEm",
    "ID Evento Agenda": "idEventoAgenda",
    "Evento criado em": "eventoCriadoEm",
    "Turma": "turma",
    "Data da decisão": "dataDecisao",
}
REQUIRED_COLUMNS = list(FIELD_MAP)
DATA_RE = re.compile(r"(?:const DATA|window\.DATA) = (\[.*?\n\]);", re.S)


def normalize_newlines(text: str) -> str:
    return text.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")


def read_tsv(path: Path) -> list[dict[str, str]]:
    text = normalize_newlines(path.read_text(encoding="utf-8-sig"))
    rows = list(csv.reader(text.splitlines(), delimiter="\t"))
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise SystemExit("TSV vazio.")
    header = [cell.strip() for cell in rows[0]]
    missing = [col for col in REQUIRED_COLUMNS if col not in header]
    if missing:
        raise SystemExit(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
    records = []
    for raw in rows[1:]:
        if [cell.strip() for cell in raw] == header:
            continue
        padded = raw + [""] * (len(header) - len(raw))
        records.append(dict(zip(header, padded[: len(header)])))
    return records


def caso_raiz(caso: str) -> str:
    return str(caso or "").replace(",", ".").split(".")[0]


def parse_ordem(value: str) -> int | None:
    value = str(value or "").strip()
    if not value:
        return None
    try:
        return int(float(value.replace(",", ".")))
    except ValueError:
        return None


def build_data(records: list[dict[str, str]]) -> list[dict[str, object]]:
    data = []
    for idx, record in enumerate(records, start=2):
        item: dict[str, object] = {"row": idx}
        for source, target in FIELD_MAP.items():
            item[target] = str(record.get(source, "")).strip()
        item["caso"] = str(item["caso"]).replace(",", ".")
        item["casoRaiz"] = caso_raiz(str(item["caso"]))
        item["semId"] = not bool(str(item["id"]).strip())
        item["ordem"] = parse_ordem(str(item["ordemLabel"]))
        data.append(item)
    return data


def replace_data(text: str, data: list[dict[str, object]], *, global_name: str = "window.DATA") -> str:
    replacement = global_name + " = " + json.dumps(data, ensure_ascii=False, indent=2) + ";"
    if not DATA_RE.search(text):
        raise SystemExit("Não encontrei `window.DATA = [...]` ou `const DATA = [...]` no arquivo de dados.")
    return DATA_RE.sub(replacement, text, count=1)


def replace_updated_at(html: str, updated_at: str | None) -> str:
    if not updated_at:
        return html
    return re.sub(
        r"Base: Prazos ANRESF\(3\)\.xlsx(?: · Atualizado em \d{2}/\d{2}/\d{4})?",
        f"Base: Prazos ANRESF(3).xlsx · Atualizado em {updated_at}",
        html,
        count=1,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Atualiza o window.DATA do data.js a partir de um TSV.")
    parser.add_argument("tsv", type=Path, help="Arquivo TSV exportado/colado da planilha.")
    parser.add_argument("--html", type=Path, default=Path("index.html"), help="Caminho do HTML a atualizar.")
    parser.add_argument("--data-js", type=Path, default=Path("data.js"), help="Caminho do arquivo JavaScript com window.DATA.")
    parser.add_argument("--updated-at", help="Data exibida no topo, ex.: 08/07/2026.")
    args = parser.parse_args()

    records = read_tsv(args.tsv)
    data = build_data(records)
    data_js = args.data_js.read_text(encoding="utf-8")
    data_js = replace_data(data_js, data)
    args.data_js.write_text(data_js, encoding="utf-8")

    html = args.html.read_text(encoding="utf-8")
    html = replace_updated_at(html, args.updated_at)
    args.html.write_text(html, encoding="utf-8")
    print(f"Importados {len(data)} registros para {args.data_js}.")


if __name__ == "__main__":
    main()
