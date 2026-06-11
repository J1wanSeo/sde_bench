from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from ..io import load_records

Record = dict[str, Any]


def export_synthea_records(
    csv_dir: str | Path,
    *,
    split_fraction: float = 0.5,
    limit: int | None = None,
    reference_date: date = date(2026, 1, 1),
) -> dict[str, list[Record]]:
    """Convert Synthea CSV exports into patient-level SDE-Bench records."""
    root = Path(csv_dir)
    patients = _load_optional(root / "patients.csv")
    selected = patients[:limit] if limit else patients
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}

    conditions = _by_patient(_load_optional(root / "conditions.csv"))
    procedures = _by_patient(_load_optional(root / "procedures.csv"))
    encounters = _by_patient(_load_optional(root / "encounters.csv"))
    medications = _by_patient(_load_optional(root / "medications.csv"))
    observations = _by_patient(_load_optional(root / "observations.csv"))

    records = [
        _patient_record(
            patient,
            conditions=conditions.get(str(patient.get("Id") or patient.get("ID") or patient.get("id")), []),
            procedures=procedures.get(str(patient.get("Id") or patient.get("ID") or patient.get("id")), []),
            encounters=encounters.get(str(patient.get("Id") or patient.get("ID") or patient.get("id")), []),
            medications=medications.get(str(patient.get("Id") or patient.get("ID") or patient.get("id")), []),
            observations=observations.get(str(patient.get("Id") or patient.get("ID") or patient.get("id")), []),
            reference_date=reference_date,
        )
        for patient in selected
    ]
    split_at = max(1, min(len(records) - 1, int(len(records) * split_fraction)))
    reference_rows = records[:split_at]
    synthetic_rows = [{**record, "source_id": record["case_id"]} for record in records[split_at:]]
    source_rows = [{**record, "source_id": record["case_id"]} for record in records[split_at:]]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _load_optional(path: Path) -> list[Record]:
    return load_records(path) if path.exists() else []


def _by_patient(rows: list[Record]) -> dict[str, list[Record]]:
    grouped: dict[str, list[Record]] = {}
    for row in rows:
        patient_id = row.get("PATIENT") or row.get("patient") or row.get("Patient")
        if patient_id not in (None, ""):
            grouped.setdefault(str(patient_id), []).append(row)
    return grouped


def _patient_record(
    patient: Record,
    *,
    conditions: list[Record],
    procedures: list[Record],
    encounters: list[Record],
    medications: list[Record],
    observations: list[Record],
    reference_date: date,
) -> Record:
    patient_id = str(patient.get("Id") or patient.get("ID") or patient.get("id"))
    diagnosis = _join_descriptions(conditions)
    procedure_text = _join_descriptions(procedures)
    domains = ["person"]
    if encounters:
        domains.append("visit_occurrence")
    if conditions:
        domains.append("condition_occurrence")
    if procedures:
        domains.append("procedure_occurrence")
    if medications:
        domains.append("drug_exposure")
    if observations:
        domains.append("measurement")

    condition_codes = _join_codes(conditions)
    procedure_codes = _join_codes(procedures)
    medication_codes = _join_codes(medications)
    observation_codes = _join_codes(observations)
    clinical_codes = ",".join(code for code in (condition_codes, procedure_codes, medication_codes, observation_codes) if code)
    vocabularies = _vocabularies(
        has_snomed=bool(conditions or procedures or encounters),
        has_rxnorm=bool(medications),
        has_loinc=bool(observations),
    )
    evidence_parts = [
        f"conditions: {diagnosis}" if diagnosis else "",
        f"procedures: {procedure_text}" if procedure_text else "",
        f"encounters: {_join_descriptions(encounters)}" if encounters else "",
    ]
    evidence = "; ".join(part for part in evidence_parts if part)
    first_condition = conditions[0] if conditions else {}
    first_procedure = procedures[0] if procedures else {}
    first_encounter = encounters[0] if encounters else {}

    return {
        "case_id": f"SYNTHEA-{patient_id}",
        "patient_id": patient_id,
        "age": _age(patient.get("BIRTHDATE") or patient.get("birthdate"), reference_date),
        "sex": patient.get("GENDER") or patient.get("gender") or "",
        "race": patient.get("RACE") or patient.get("race") or "",
        "ethnicity": patient.get("ETHNICITY") or patient.get("ethnicity") or "",
        "diagnosis": diagnosis,
        "diagnosis_group": str(first_condition.get("CODE") or "")[:6],
        "procedures": procedure_text,
        "clinical_codes": clinical_codes,
        "omop_domains": ",".join(domains),
        "standard_vocabularies": ",".join(vocabularies),
        "encounter_id": first_encounter.get("Id") or first_condition.get("ENCOUNTER") or first_procedure.get("ENCOUNTER") or "",
        "encounter_start": first_encounter.get("START") or "",
        "condition_start": first_condition.get("START") or "",
        "procedure_date": first_procedure.get("DATE") or first_procedure.get("START") or "",
        "claim": evidence or diagnosis or procedure_text,
        "evidence": evidence or diagnosis or procedure_text,
        "expected_diagnosis_group": str(first_condition.get("CODE") or "")[:6],
    }


def _join_descriptions(rows: list[Record]) -> str:
    values = []
    for row in rows[:5]:
        value = row.get("DESCRIPTION") or row.get("description") or row.get("REASONDESCRIPTION") or ""
        if value not in (None, ""):
            values.append(str(value))
    return "; ".join(values)


def _join_codes(rows: list[Record]) -> str:
    values = []
    for row in rows[:10]:
        value = row.get("CODE") or row.get("code") or ""
        if value not in (None, ""):
            values.append(str(value))
    return ",".join(values)


def _vocabularies(*, has_snomed: bool, has_rxnorm: bool, has_loinc: bool) -> list[str]:
    values = []
    if has_snomed:
        values.append("SNOMED-CT")
    if has_rxnorm:
        values.append("RxNorm")
    if has_loinc:
        values.append("LOINC")
    return values


def _age(birthdate: Any, reference_date: date) -> int | str:
    if birthdate in (None, ""):
        return ""
    try:
        born = date.fromisoformat(str(birthdate)[:10])
    except ValueError:
        return ""
    age = reference_date.year - born.year - ((reference_date.month, reference_date.day) < (born.month, born.day))
    return age if 0 <= age <= 120 else ""
