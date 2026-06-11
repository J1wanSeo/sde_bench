from __future__ import annotations

from datetime import date
from typing import Any

Record = dict[str, Any]


def export_health_gym_art_records(
    rows: list[Record], *, split_fraction: float = 0.5, limit: int | None = None
) -> dict[str, list[Record]]:
    """Convert Health Gym ART-for-HIV monthly records into SDE-Bench records.

    The dataset is fully synthetic and longitudinal. We split by patient ID
    instead of by row so one patient's trajectory cannot appear in both the
    reference and synthetic partitions.
    """
    selected = rows[:limit] if limit else rows
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}
    patient_ids = sorted({_patient_id(row) for row in selected}, key=_patient_sort_key)
    split_at = max(1, min(len(patient_ids) - 1, int(len(patient_ids) * split_fraction)))
    reference_patients = set(patient_ids[:split_at])
    synthetic_patients = set(patient_ids[split_at:])

    reference_rows = [_row(row) for row in selected if _patient_id(row) in reference_patients]
    synthetic_rows = [
        _row(row, source_id=_source_id(row))
        for row in selected
        if _patient_id(row) in synthetic_patients
    ]
    source_rows = [
        _row(row, source_id=_source_id(row), source_record=True)
        for row in selected
        if _patient_id(row) in synthetic_patients
    ]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _row(row: Record, *, source_id: str | None = None, source_record: bool = False) -> Record:
    patient_id = _patient_id(row)
    timestep = _int(row.get("Timestep"))
    case_id = _case_id(patient_id, timestep)
    event_date = _month_date(timestep)
    out: Record = {
        "case_id": case_id,
        "patient_id": patient_id,
        "encounter_id": case_id,
        "month": timestep,
        "condition_start": event_date,
        "measurement_date": event_date,
        "procedure_date": event_date,
        "diagnosis": "HIV antiretroviral therapy",
        "diagnosis_group": "HIV",
        "sex": _category(row.get("Gender")),
        "ethnicity": _category(row.get("Ethnic")),
        "viral_load": _number(row.get("VL")),
        "cd4_count": _number(row.get("CD4")),
        "relative_cd4": _number(row.get("Rel CD4")),
        "base_drug_combo": _category(row.get("Base Drug Combo")),
        "comp_ini": _category(row.get("Comp. INI")),
        "comp_nnrti": _category(row.get("Comp. NNRTI")),
        "extra_pi": _category(row.get("Extra PI")),
        "extra_pk_en": _category(row.get("Extra pk-En")),
        "viral_load_missing": _category(row.get("VL (M)")),
        "cd4_missing": _category(row.get("CD4 (M)")),
        "drug_missing": _category(row.get("Drug (M)")),
        "claim": _claim(row),
        "evidence": _claim(row),
        "expected_diagnosis_group": "HIV",
        "omop_domains": "person,visit_occurrence,condition_occurrence,drug_exposure,measurement",
        "standard_vocabularies": "LOINC|RxNorm|SNOMED-CT",
    }
    if source_id:
        out["source_id"] = source_id
    if source_record:
        out["case_id"] = source_id or case_id
    return out


def _claim(row: Record) -> str:
    return (
        f"Monthly HIV ART record with viral load {_number(row.get('VL'))}, "
        f"CD4 {_number(row.get('CD4'))}, and drug missing flag {_category(row.get('Drug (M)'))}."
    )


def _case_id(patient_id: str, timestep: int) -> str:
    return f"HEALTHGYM-ART-{patient_id}-T{timestep}"


def _source_id(row: Record) -> str:
    return _case_id(_patient_id(row), _int(row.get("Timestep")))


def _patient_id(row: Record) -> str:
    return str(row.get("PatientID", "")).strip()


def _month_date(timestep: int) -> str:
    month_index = max(timestep, 0)
    year = 2023 + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1).isoformat()


def _patient_sort_key(value: str) -> tuple[int, str]:
    try:
        return (0, f"{int(value):012d}")
    except ValueError:
        return (1, value)


def _category(value: Any) -> str:
    if value in (None, ""):
        return ""
    as_number = _number(value)
    if isinstance(as_number, int):
        return str(as_number)
    return str(value).strip()


def _int(value: Any) -> int:
    number = _number(value)
    return number if isinstance(number, int) else 0


def _number(value: Any) -> int | float | str:
    if value in (None, ""):
        return ""
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return str(value).strip()
    if as_float.is_integer():
        return int(as_float)
    return as_float
