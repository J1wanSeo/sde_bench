from __future__ import annotations

import re
from typing import Any

Record = dict[str, Any]

AGE_SEX_RE = re.compile(r"\(([MF])\s*/\s*(\d{1,3})\)")


def export_kmuc_records(
    enriched_cases: list[Record],
    *,
    lay_variants: list[Record] | None = None,
    per_case_predictions: list[Record] | None = None,
) -> dict[str, list[Record]]:
    """Convert KMUC patient-case JSONL records into SDE-Bench flat records."""
    by_case = {row["case_id"]: row for row in enriched_cases}
    predictions = _prediction_lookup(per_case_predictions or [])
    reference = [_reference_row(row) for row in enriched_cases]
    source = [{**row, "source_id": row["case_id"]} for row in reference]

    synthetic: list[Record]
    if lay_variants:
        synthetic = [
            _lay_row(row, by_case.get(row["case_id"], {}), predictions)
            for row in lay_variants
            if row.get("case_id") in by_case
        ]
    else:
        synthetic = [
            {**_reference_row(row), "source_id": row["case_id"], "claim": _claim_from_enriched(row), "evidence": row.get("raw_chart", "")}
            for row in enriched_cases
        ]

    return {"reference": reference, "source": source, "synthetic": synthetic}


def _reference_row(row: Record) -> Record:
    extraction = row.get("extraction") or {}
    labels = row.get("labels") or {}
    sex, age = _age_sex(row.get("raw_chart", ""))
    dept = labels.get("expected_department") or _first(extraction.get("dept_hint")) or ""
    diagnosis = extraction.get("current_diagnosis") or ""
    return {
        "case_id": row.get("case_id", ""),
        "age": age,
        "sex": sex,
        "dept": dept,
        "diagnosis": diagnosis,
        "icd10_codes": _join(extraction.get("icd10_candidates") or labels.get("icd10_candidates")),
        "procedures": _join(extraction.get("procedure_candidates") or labels.get("procedure_candidates")),
        "acuity": extraction.get("acuity") or labels.get("acuity") or "",
        "laterality": extraction.get("laterality") or labels.get("laterality") or "",
        "claim": _claim_from_enriched(row),
        "evidence": row.get("raw_chart", ""),
        "expected_dept": dept,
    }


def _lay_row(row: Record, source: Record, predictions: dict[tuple[str, int], str]) -> Record:
    base = _reference_row(source)
    variant_id = int(row.get("variant_id", 0))
    case_id = row.get("case_id", "")
    expected = row.get("expected_dept") or base.get("expected_dept") or base.get("dept")
    return {
        **base,
        "case_id": f"{case_id}::lay::{variant_id}",
        "source_id": case_id,
        "claim": row.get("lay_text", ""),
        "evidence": row.get("original_emr") or base.get("evidence", ""),
        "tone": row.get("tone", ""),
        "expected_dept": expected,
        "predicted_dept": predictions.get((case_id, variant_id), ""),
    }


def _prediction_lookup(rows: list[Record]) -> dict[tuple[str, int], str]:
    out: dict[tuple[str, int], str] = {}
    for row in rows:
        if "variant_id" not in row:
            continue
        top_depts = row.get("top_depts") or []
        if top_depts:
            out[(str(row.get("case_id")), int(row.get("variant_id")))] = str(top_depts[0])
    return out


def _age_sex(text: str) -> tuple[str, int | str]:
    match = AGE_SEX_RE.search(text or "")
    if not match:
        return "", ""
    return match.group(1), int(match.group(2))


def _claim_from_enriched(row: Record) -> str:
    extraction = row.get("extraction") or {}
    return " | ".join(
        str(part)
        for part in [
            extraction.get("chief_complaint"),
            extraction.get("current_diagnosis"),
            extraction.get("planned_procedure"),
        ]
        if part
    )


def _join(values: Any) -> str:
    if values is None:
        return ""
    if isinstance(values, list):
        return ",".join(str(v) for v in values if v)
    return str(values)


def _first(values: Any) -> str:
    if isinstance(values, list) and values:
        return str(values[0])
    return str(values or "")
