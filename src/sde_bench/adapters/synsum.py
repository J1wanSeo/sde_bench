from __future__ import annotations

from typing import Any

Record = dict[str, Any]

SYMPTOM_COLUMNS = ("dysp", "cough", "pain", "fever", "nasal")
CONDITION_COLUMNS = ("asthma", "smoking", "COPD", "hay_fever")


def export_synsum_records(rows: list[Record], *, split_fraction: float = 0.5, limit: int | None = None) -> dict[str, list[Record]]:
    """Convert SynSUM CSV rows into SDE-Bench reference/source/synthetic records.

    SynSUM is fully synthetic. We use an internal split: the first partition is
    the reference distribution, and the second partition is the synthetic set
    being scored. The synthetic claim is `advanced_text`; its evidence is the
    full `text` note from the same patient record.
    """
    selected = rows[:limit] if limit else rows
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}
    split_at = max(1, min(len(selected) - 1, int(len(selected) * split_fraction)))
    reference_rows = [_row(row, idx, claim_field="text") for idx, row in enumerate(selected[:split_at])]
    synthetic_rows = [
        _row(row, idx + split_at, claim_field="advanced_text", source_id=f"SYNSUM-{idx + split_at:05d}")
        for idx, row in enumerate(selected[split_at:])
    ]
    source_rows = [
        _row(row, idx + split_at, claim_field="text", source_id=f"SYNSUM-{idx + split_at:05d}")
        for idx, row in enumerate(selected[split_at:])
    ]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _row(row: Record, idx: int, *, claim_field: str, source_id: str | None = None) -> Record:
    record_id = f"SYNSUM-{idx:05d}"
    diagnosis = _diagnosis(row)
    symptoms = [col for col in SYMPTOM_COLUMNS if _truthy(row.get(col))]
    conditions = [col for col in CONDITION_COLUMNS if _truthy(row.get(col))]
    out: Record = {
        "case_id": record_id,
        "diagnosis": diagnosis,
        "diagnosis_group": diagnosis,
        "symptoms": "|".join(symptoms),
        "conditions": "|".join(conditions),
        "dyspnea": _int_bool(row.get("dysp")),
        "cough": _int_bool(row.get("cough")),
        "pain": _int_bool(row.get("pain")),
        "fever": _int_bool(row.get("fever")),
        "nasal": _int_bool(row.get("nasal")),
        "asthma": _int_bool(row.get("asthma")),
        "smoking": _int_bool(row.get("smoking")),
        "copd": _int_bool(row.get("COPD")),
        "hay_fever": _int_bool(row.get("hay_fever")),
        "antibiotics": _int_bool(row.get("antibiotics")),
        "season": str(row.get("season", "")),
        "days_at_home": _number(row.get("days_at_home")),
        "claim": str(row.get(claim_field) or row.get("text") or ""),
        "evidence": str(row.get("text") or ""),
        "expected_diagnosis_group": diagnosis,
    }
    if source_id:
        out["source_id"] = source_id
    return out


def _diagnosis(row: Record) -> str:
    if _truthy(row.get("pneu")):
        return "pneumonia"
    if _truthy(row.get("cold")) or _truthy(row.get("common_cold")):
        return "common_cold"
    return "none"


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "1.0", "true", "yes", "y"}


def _int_bool(value: Any) -> int:
    return 1 if _truthy(value) else 0


def _number(value: Any) -> int | float | str:
    if value in (None, ""):
        return ""
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return str(value)
    if as_float.is_integer():
        return int(as_float)
    return as_float
