from __future__ import annotations

import re
from typing import Any

Record = dict[str, Any]
AGE_RE = re.compile(r"\b(\d{1,3})[- ]year[- ]old\b", re.IGNORECASE)


def export_medsynth_records(rows: list[Record], *, split_fraction: float = 0.5, limit: int | None = None) -> dict[str, list[Record]]:
    """Convert MedSynth dialogue-note rows into SDE-Bench records."""
    selected = rows[:limit] if limit else rows
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}
    split_at = max(1, min(len(selected) - 1, int(len(selected) * split_fraction)))
    reference_rows = [_row(row, idx, claim_field=" Note") for idx, row in enumerate(selected[:split_at])]
    synthetic_rows = [
        _row(row, idx + split_at, claim_field=" Note", source_id=f"MEDSYNTH-{idx + split_at:05d}")
        for idx, row in enumerate(selected[split_at:])
    ]
    source_rows = [
        _source_row(row, idx + split_at, source_id=f"MEDSYNTH-{idx + split_at:05d}") for idx, row in enumerate(selected[split_at:])
    ]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _row(row: Record, idx: int, *, claim_field: str, source_id: str | None = None) -> Record:
    note = str(row.get(claim_field) or row.get("Note") or "")
    dialogue = str(row.get("Dialogue") or "")
    icd10 = _icd10(row)
    out: Record = {
        "case_id": f"MEDSYNTH-{idx:05d}",
        "age": _age(note + " " + dialogue),
        "diagnosis": str(row.get("ICD10_desc") or "").strip(),
        "diagnosis_group": icd10[:3] if icd10 else "",
        "icd10_codes": icd10,
        "claim": note,
        "evidence": dialogue,
        "expected_diagnosis_group": icd10[:3] if icd10 else "",
    }
    if source_id:
        out["source_id"] = source_id
    return out


def _source_row(row: Record, idx: int, *, source_id: str) -> Record:
    base = _row(row, idx, claim_field="Dialogue")
    base["source_id"] = source_id
    base["case_id"] = source_id
    base["claim"] = str(row.get("Dialogue") or "")
    base["evidence"] = str(row.get("Dialogue") or "")
    return base


def _icd10(row: Record) -> str:
    return str(row.get("ICD10") or row.get("icd10") or "").strip().upper()


def _age(text: str) -> int | str:
    match = AGE_RE.search(text)
    if not match:
        return ""
    age = int(match.group(1))
    return age if 0 <= age <= 120 else ""
