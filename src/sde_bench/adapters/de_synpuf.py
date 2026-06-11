from __future__ import annotations

from typing import Any

Record = dict[str, Any]


def export_de_synpuf_records(
    beneficiary_rows: list[Record],
    inpatient_rows: list[Record],
    *,
    split_fraction: float = 0.5,
    limit: int | None = None,
) -> dict[str, list[Record]]:
    """Convert CMS DE-SynPUF beneficiary and inpatient claims into records."""
    beneficiaries = {str(row.get("DESYNPUF_ID", "")).strip(): row for row in beneficiary_rows}
    selected = inpatient_rows[:limit] if limit else inpatient_rows
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}
    split_at = max(1, min(len(selected) - 1, int(len(selected) * split_fraction)))
    reference_rows = [_row(row, beneficiaries) for row in selected[:split_at]]
    synthetic_rows = [_row(row, beneficiaries, source_id=_source_id(row)) for row in selected[split_at:]]
    source_rows = [_row(row, beneficiaries, source_id=_source_id(row)) for row in selected[split_at:]]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _row(row: Record, beneficiaries: dict[str, Record], *, source_id: str | None = None) -> Record:
    patient_id = _text(row, "DESYNPUF_ID")
    claim_id = _text(row, "CLM_ID")
    beneficiary = beneficiaries.get(patient_id, {})
    diagnosis_codes = _codes(row, "ICD9_DGNS_CD_", 10)
    procedures = _codes(row, "ICD9_PRCDR_CD_", 6)
    primary_diagnosis = diagnosis_codes[0] if diagnosis_codes else _text(row, "ADMTNG_ICD9_DGNS_CD")
    claim_start = _date(_text(row, "CLM_FROM_DT"))
    out: Record = {
        "case_id": f"DESYNPUF-{claim_id}",
        "patient_id": patient_id,
        "sex": _text(beneficiary, "BENE_SEX_IDENT_CD"),
        "race": _text(beneficiary, "BENE_RACE_CD"),
        "state": _text(beneficiary, "SP_STATE_CODE"),
        "esrd": _text(beneficiary, "BENE_ESRD_IND"),
        "age": _age(_text(beneficiary, "BENE_BIRTH_DT"), _text(row, "CLM_FROM_DT")),
        "diagnosis": primary_diagnosis,
        "diagnosis_group": primary_diagnosis[:3] if primary_diagnosis else "",
        "icd9_codes": "|".join(diagnosis_codes),
        "admitting_diagnosis": _text(row, "ADMTNG_ICD9_DGNS_CD"),
        "procedures": "|".join(procedures),
        "drg": _text(row, "CLM_DRG_CD"),
        "claim_payment_amount": _number(row.get("CLM_PMT_AMT")),
        "utilization_days": _number(row.get("CLM_UTLZTN_DAY_CNT")),
        "encounter_start": claim_start,
        "encounter_end": _date(_text(row, "CLM_THRU_DT")),
        "condition_start": claim_start,
        "omop_domains": "person,visit_occurrence,condition_occurrence,procedure_occurrence",
        "standard_vocabularies": "ICD9-CM",
        "claim": _claim_text(patient_id, claim_id, primary_diagnosis),
        "evidence": _claim_text(patient_id, claim_id, primary_diagnosis),
        "expected_diagnosis_group": primary_diagnosis[:3] if primary_diagnosis else "",
    }
    chronic = _chronic_flags(beneficiary)
    if chronic:
        out["chronic_conditions"] = "|".join(chronic)
    if source_id:
        out["source_id"] = source_id
    return out


def _source_id(row: Record) -> str:
    return f"DESYNPUF-{_text(row, 'CLM_ID')}"


def _text(row: Record, key: str) -> str:
    value = row.get(key)
    if value in (None, ""):
        return ""
    return str(value).strip()


def _codes(row: Record, prefix: str, count: int) -> list[str]:
    values = []
    for index in range(1, count + 1):
        value = _text(row, f"{prefix}{index}")
        if value:
            values.append(value)
    return values


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


def _date(value: str) -> str:
    if len(value) != 8 or not value.isdigit():
        return value
    return f"{value[:4]}-{value[4:6]}-{value[6:]}"


def _age(birth_date: str, claim_date: str) -> int | str:
    if len(birth_date) != 8 or len(claim_date) != 8:
        return ""
    try:
        birth_year = int(birth_date[:4])
        claim_year = int(claim_date[:4])
        before_birthday = claim_date[4:] < birth_date[4:]
    except ValueError:
        return ""
    age = claim_year - birth_year - int(before_birthday)
    return age if 0 <= age <= 120 else ""


def _chronic_flags(row: Record) -> list[str]:
    names = {
        "SP_ALZHDMTA": "alzheimers",
        "SP_CHF": "heart_failure",
        "SP_CHRNKIDN": "chronic_kidney_disease",
        "SP_CNCR": "cancer",
        "SP_COPD": "copd",
        "SP_DEPRESSN": "depression",
        "SP_DIABETES": "diabetes",
        "SP_ISCHMCHT": "ischemic_heart_disease",
        "SP_OSTEOPRS": "osteoporosis",
        "SP_RA_OA": "rheumatoid_or_osteoarthritis",
        "SP_STRKETIA": "stroke",
    }
    return [name for key, name in names.items() if _text(row, key) == "1"]


def _claim_text(patient_id: str, claim_id: str, diagnosis: str) -> str:
    return f"Inpatient claim {claim_id} for beneficiary {patient_id} with ICD-9 diagnosis {diagnosis}."
