from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


Record = dict[str, Any]


def _coerce(value: str) -> Any:
    text = value.strip()
    if text == "":
        return ""
    lowered = text.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if len(text) > 1 and text[0] == "0" and text[1].isdigit():
        return text
    try:
        value_int = int(text)
    except ValueError:
        pass
    else:
        return value_int
    try:
        return float(text)
    except ValueError:
        return text


def load_records(path: str | Path) -> list[Record]:
    """Load CSV, JSON, or JSONL records with light type inference."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        with source.open(encoding="utf-8-sig", newline="") as handle:
            return [{k: _coerce(v or "") for k, v in row.items()} for row in csv.DictReader(handle)]
    if suffix == ".jsonl":
        rows: list[Record] = []
        with source.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    if suffix == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("records", "rows", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
        raise ValueError(f"JSON file must contain a list of records: {source}")
    raise ValueError(f"Unsupported record format: {source}")


def load_source(path: str | Path | None) -> dict[str, Record] | None:
    if path is None:
        return None
    rows = load_records(path)
    mapping: dict[str, Record] = {}
    for row in rows:
        source_id = row.get("source_id") or row.get("case_id") or row.get("id")
        if source_id is not None:
            mapping[str(source_id)] = row
    return mapping


def write_json(report: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def markdown_report(report: dict[str, Any]) -> str:
    lines = ["# SDE-Bench Report", ""]
    if "name" in report:
        lines.append(f"- dataset: `{report['name']}`")
    lines.append(f"- overall_score: `{report.get('overall_score', 0):.4f}`")
    lines.append("")
    lines.append("| Axis | Score | Key metrics |")
    lines.append("|---|---:|---|")
    for axis, axis_report in report.get("axes", {}).items():
        metrics = axis_report.get("metrics", {})
        rendered = ", ".join(f"{k}={_fmt(v)}" for k, v in metrics.items() if isinstance(v, int | float | str | bool))
        lines.append(f"| {axis} | {_fmt(axis_report.get('score'))} | {rendered} |")
    lines.append("")
    skipped = report.get("skipped") or []
    if skipped:
        lines.append("## Skipped")
        lines.extend(f"- {item}" for item in skipped)
        lines.append("")
    return "\n".join(lines)


def write_markdown(report: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown_report(report), encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
