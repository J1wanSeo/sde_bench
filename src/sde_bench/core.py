from __future__ import annotations

import math
import re
import statistics
from collections import Counter, OrderedDict
from itertools import combinations
from typing import Any

from .config import load_config

Record = dict[str, Any]

AXIS_ORDER = [
    "medical_fidelity",
    "clinical_task_utility",
    "privacy",
    "equity",
    "medical_diversity",
    "clinical_groundedness",
    "clinical_validity",
    "medical_interoperability",
]

ID_COLUMNS = {
    "id",
    "case_id",
    "record_id",
    "source_id",
    "claim",
    "evidence",
    "predicted_label",
    "expected_label",
    "predicted_dept",
    "expected_dept",
}
DEFAULT_SENSITIVE_COLUMNS = ("sex", "gender", "race", "ethnicity", "age_group")
ICD10_RE = re.compile(r"^[A-TV-Z][0-9][0-9A-Z]?(?:\.?[0-9A-Z]{1,4})?$")
VALID_ACUITY = {"routine", "elective", "urgent", "emergency"}
VALID_LATERALITY = {"left", "right", "bilateral", "none", "midline", "unknown"}
OMOP_CORE_DOMAINS = {
    "person",
    "visit_occurrence",
    "condition_occurrence",
    "procedure_occurrence",
    "drug_exposure",
    "measurement",
}
STANDARD_VOCABULARIES = {
    "ICD10",
    "ICD10CM",
    "SNOMED",
    "SNOMEDCT",
    "SNOMED-CT",
    "LOINC",
    "RXNORM",
    "CPT",
    "HCPCS",
}
EVENT_DATE_FIELDS = (
    "encounter_start",
    "visit_start",
    "condition_start",
    "procedure_date",
    "drug_start",
    "measurement_date",
)


def evaluate(
    *,
    real: list[Record],
    synthetic: list[Record],
    source: dict[str, Record] | None = None,
    target: str | None = None,
    sensitive_columns: list[str] | None = None,
    config: str | dict[str, Any] | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Evaluate one synthetic medical dataset against a reference dataset."""
    if not real:
        raise ValueError("real must contain at least one record")
    if not synthetic:
        raise ValueError("synthetic must contain at least one record")

    eval_config = load_config(config)
    enabled_axes = set(eval_config["axes"])
    sensitive = sensitive_columns or [c for c in DEFAULT_SENSITIVE_COLUMNS if _has_column(real + synthetic, c)]
    all_axes = OrderedDict(
        [
            ("medical_fidelity", _fidelity(real, synthetic)),
            ("clinical_task_utility", _utility(synthetic, target)),
            ("privacy", _privacy(real, synthetic)),
            ("equity", _fairness(real, synthetic, target, sensitive)),
            ("medical_diversity", _diversity(real, synthetic)),
            ("clinical_groundedness", _groundedness(synthetic, source)),
            ("clinical_validity", _clinical_validity(synthetic, source)),
            ("medical_interoperability", _medical_interoperability(synthetic)),
        ]
    )
    axes = OrderedDict((axis, result) for axis, result in all_axes.items() if axis in enabled_axes)
    skipped = _skipped(real, synthetic, source, target, sensitive)
    report: dict[str, Any] = {
        "schema_version": "0.1.0",
        "records": {"real": len(real), "synthetic": len(synthetic)},
        "config": eval_config.get("name", "custom"),
        "axes": axes,
        "overall_score": _mean(axis["score"] for axis in axes.values()),
        "skipped": skipped,
    }
    if name:
        report["name"] = name
    return report


def benchmark(
    *,
    real: list[Record],
    synthetic_sets: dict[str, list[Record]],
    source: dict[str, Record] | None = None,
    target: str | None = None,
    sensitive_columns: list[str] | None = None,
    config: str | dict[str, Any] | None = None,
    rank_strategy: str = "linear",
) -> dict[str, Any]:
    """Evaluate and rank several synthetic datasets.

    The current ranking uses the mean axis score. The `rank_strategy` field is
    retained in the report so later versions can add SynthEval-like linear,
    normal, and quantile rank transforms without changing the output shape.
    """
    reports = {
        name: evaluate(
            real=real,
            synthetic=records,
            source=source,
            target=target,
            sensitive_columns=sensitive_columns,
            config=config,
            name=name,
        )
        for name, records in synthetic_sets.items()
    }
    ranking = sorted(
        (
            {"name": name, "overall_score": report["overall_score"]}
            for name, report in reports.items()
        ),
        key=lambda row: (-row["overall_score"], row["name"]),
    )
    for idx, row in enumerate(ranking, start=1):
        row["rank"] = idx
    return {
        "schema_version": "0.1.0",
        "rank_strategy": rank_strategy,
        "ranking": ranking,
        "reports": reports,
    }


def _fidelity(real: list[Record], synthetic: list[Record]) -> dict[str, Any]:
    cols = _common_metric_columns(real, synthetic)
    column_scores = [_column_similarity(real, synthetic, col) for col in cols]
    pair_cols = [col for col in cols if not _is_numeric_column(real + synthetic, col)]
    pair_scores = [_pair_similarity(real, synthetic, a, b) for a, b in combinations(pair_cols[:8], 2)]
    metrics = {
        "column_similarity": _mean(column_scores),
        "pairwise_similarity": _mean(pair_scores) if pair_scores else None,
        "columns_compared": len(cols),
        "pairs_compared": len(pair_scores),
    }
    score = _mean(v for v in (metrics["column_similarity"], metrics["pairwise_similarity"]) if v is not None)
    return {"score": score, "metrics": metrics}


def _utility(synthetic: list[Record], target: str | None) -> dict[str, Any]:
    expected = _first_present(synthetic, ["expected_label", f"expected_{target}" if target else "", "expected_dept"])
    predicted = _first_present(synthetic, ["predicted_label", f"predicted_{target}" if target else "", "predicted_dept"])
    metrics: dict[str, Any] = {}
    if expected and predicted:
        labeled_rows = [row for row in synthetic if row.get(expected) not in (None, "") and row.get(predicted) not in (None, "")]
        total = len(labeled_rows)
        correct = sum(1 for row in labeled_rows if row.get(expected) == row.get(predicted))
        metrics["label_accuracy"] = correct / total if total else None
        metrics["label_support"] = total
    if target:
        metrics["target_population_rate"] = _population_rate(synthetic, target)
    score_values = [metrics[key] for key in ("label_accuracy", "target_population_rate") if isinstance(metrics.get(key), int | float)]
    return {"score": _mean(score_values), "metrics": metrics}


def _privacy(real: list[Record], synthetic: list[Record]) -> dict[str, Any]:
    real_fingerprints = {_fingerprint(row) for row in real}
    exact_duplicates = sum(1 for row in synthetic if _fingerprint(row) in real_fingerprints)
    duplicate_rate = exact_duplicates / len(synthetic)
    distances = [_closest_distance(row, real) for row in synthetic]
    median_distance = statistics.median(distances) if distances else 0.0
    metrics = {
        "exact_duplicate_rate": duplicate_rate,
        "median_distance_to_reference": median_distance,
        "records_compared": len(synthetic),
    }
    score = _clamp((1.0 - duplicate_rate + median_distance) / 2.0)
    return {"score": score, "metrics": metrics}


def _fairness(
    real: list[Record],
    synthetic: list[Record],
    target: str | None,
    sensitive_columns: list[str],
) -> dict[str, Any]:
    if not sensitive_columns:
        return {"score": None, "metrics": {"skipped": "no_sensitive_columns"}}
    scores = []
    for col in sensitive_columns:
        scores.append(1.0 - _categorical_tv(_values(real, col), _values(synthetic, col)))
    metrics: dict[str, Any] = {
        "sensitive_columns": ",".join(sensitive_columns),
        "sensitive_distribution_similarity": _mean(scores),
    }
    if target:
        metrics["group_target_parity"] = _group_target_parity(synthetic, target, sensitive_columns)
    return {"score": _mean(v for v in metrics.values() if isinstance(v, int | float)), "metrics": metrics}


def _diversity(real: list[Record], synthetic: list[Record]) -> dict[str, Any]:
    cols = _common_metric_columns(real, synthetic)
    categorical_cols = [col for col in cols if not _is_numeric_column(real + synthetic, col)]
    coverage_scores = []
    entropy_scores = []
    for col in categorical_cols:
        real_unique = {v for v in _values(real, col) if v not in (None, "")}
        synthetic_unique = {v for v in _values(synthetic, col) if v not in (None, "")}
        coverage_scores.append(len(real_unique & synthetic_unique) / len(real_unique) if real_unique else 1.0)
        entropy_scores.append(_entropy_ratio(_values(real, col), _values(synthetic, col)))
    fingerprints = [_fingerprint(row) for row in synthetic]
    metrics = {
        "category_coverage": _mean(coverage_scores) if coverage_scores else None,
        "entropy_ratio": _mean(entropy_scores) if entropy_scores else None,
        "unique_record_ratio": len(set(fingerprints)) / len(fingerprints),
        "categorical_columns": len(categorical_cols),
    }
    score_values = [metrics[key] for key in ("category_coverage", "entropy_ratio", "unique_record_ratio") if isinstance(metrics.get(key), int | float)]
    return {"score": _mean(score_values), "metrics": metrics}


def _groundedness(synthetic: list[Record], source: dict[str, Record] | None) -> dict[str, Any]:
    with_source = [row for row in synthetic if row.get("source_id") not in (None, "")]
    if source:
        attributed = [row for row in with_source if str(row.get("source_id")) in source]
    else:
        attributed = with_source
    evidence_rows = [row for row in synthetic if row.get("claim") and row.get("evidence")]
    support_scores = [_token_support(str(row.get("claim", "")), str(row.get("evidence", ""))) for row in evidence_rows]
    metrics = {
        "source_attribution_rate": len(attributed) / len(synthetic),
        "evidence_support_score": _mean(support_scores) if support_scores else None,
        "evidence_support_n": len(evidence_rows),
    }
    score_values = [metrics[key] for key in ("source_attribution_rate", "evidence_support_score") if isinstance(metrics.get(key), int | float)]
    return {"score": _mean(score_values), "metrics": metrics}


def _clinical_validity(synthetic: list[Record], source: dict[str, Record] | None) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "age_validity": _valid_rate(synthetic, lambda row: not isinstance(row.get("age"), int | float) or 0 <= row["age"] <= 120),
        "non_empty_diagnosis_rate": _valid_rate(synthetic, lambda row: row.get("diagnosis") not in (None, "")),
        "icd10_format_validity": _medical_code_validity(synthetic, "icd10_codes", ICD10_RE),
        "procedure_completeness": _field_completeness(synthetic, "procedures"),
        "acuity_validity": _choice_validity(synthetic, "acuity", VALID_ACUITY),
        "laterality_validity": _choice_validity(synthetic, "laterality", VALID_LATERALITY),
    }
    if source:
        source_linked = [row for row in synthetic if str(row.get("source_id")) in source]
        dept_rows = [row for row in source_linked if source[str(row.get("source_id"))].get("dept") not in (None, "")]
        if dept_rows:
            metrics["dept_consistency"] = sum(
                1
                for row in dept_rows
                if row.get("dept") == source[str(row.get("source_id"))].get("dept")
                or row.get("expected_dept") == source[str(row.get("source_id"))].get("dept")
            ) / len(dept_rows)
        dx_rows = [row for row in source_linked if source[str(row.get("source_id"))].get("diagnosis") not in (None, "")]
        if dx_rows:
            metrics["diagnosis_source_overlap"] = _mean(
                _token_support(str(row.get("diagnosis", "")), str(source[str(row.get("source_id"))].get("diagnosis", "")))
                for row in dx_rows
            )
    return {"score": _mean(v for v in metrics.values() if isinstance(v, int | float)), "metrics": metrics}


def _medical_interoperability(synthetic: list[Record]) -> dict[str, Any]:
    has_fields = any(
        row.get("omop_domains") not in (None, "")
        or row.get("standard_vocabularies") not in (None, "")
        or any(row.get(field) not in (None, "") for field in EVENT_DATE_FIELDS)
        or row.get("encounter_id") not in (None, "")
        or row.get("visit_id") not in (None, "")
        for row in synthetic
    )
    if not has_fields:
        return {"score": None, "metrics": {"skipped": "no_interoperability_fields"}}

    domains = {
        domain
        for row in synthetic
        for domain in _normalized_values(row.get("omop_domains"))
        if domain in OMOP_CORE_DOMAINS
    }
    vocabulary_rows = [row for row in synthetic if row.get("standard_vocabularies") not in (None, "")]
    temporal_rows = [row for row in synthetic if any(field in row for field in EVENT_DATE_FIELDS)]
    relational_rows = [
        row
        for row in synthetic
        if row.get("encounter_id") not in (None, "") or row.get("visit_id") not in (None, "") or row.get("source_id") not in (None, "")
    ]
    metrics = {
        "omop_domain_coverage": len(domains) / len(OMOP_CORE_DOMAINS),
        "standard_vocabulary_rate": _standard_vocabulary_rate(vocabulary_rows),
        "temporal_traceability": _valid_rate(
            temporal_rows,
            lambda row: any(_looks_like_date(row.get(field)) for field in EVENT_DATE_FIELDS),
        )
        if temporal_rows
        else None,
        "relational_integrity": _valid_rate(
            relational_rows,
            lambda row: row.get("case_id") not in (None, "")
            and (
                row.get("encounter_id") not in (None, "")
                or row.get("visit_id") not in (None, "")
                or row.get("source_id") not in (None, "")
            ),
        )
        if relational_rows
        else None,
    }
    return {"score": _mean(v for v in metrics.values() if isinstance(v, int | float)), "metrics": metrics}


def _standard_vocabulary_rate(rows: list[Record]) -> float | None:
    if not rows:
        return None
    valid = 0
    for row in rows:
        values = _normalized_values(row.get("standard_vocabularies"))
        if values and all(value.upper() in STANDARD_VOCABULARIES for value in values):
            valid += 1
    return valid / len(rows)


def _field_completeness(rows: list[Record], field: str) -> float:
    applicable = [row for row in rows if field in row]
    if not applicable:
        return 1.0
    return sum(1 for row in applicable if _split_values(row.get(field))) / len(applicable)


def _choice_validity(rows: list[Record], field: str, valid_values: set[str]) -> float:
    applicable = [row for row in rows if row.get(field) not in (None, "")]
    if not applicable:
        return 1.0
    return sum(1 for row in applicable if str(row.get(field)).strip().lower() in valid_values) / len(applicable)


def _medical_code_validity(rows: list[Record], field: str, pattern: re.Pattern[str]) -> float:
    applicable = [row for row in rows if row.get(field) not in (None, "")]
    if not applicable:
        return 1.0
    valid_rows = 0
    for row in applicable:
        codes = _split_values(row.get(field))
        if codes and all(pattern.match(code.strip().upper()) for code in codes):
            valid_rows += 1
    return valid_rows / len(applicable)


def _split_values(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list | tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in re.split(r"[,;|]", str(value)) if part.strip()]


def _normalized_values(value: Any) -> list[str]:
    return [part.strip().lower() for part in _split_values(value)]


def _looks_like_date(value: Any) -> bool:
    if value in (None, ""):
        return False
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}", str(value).strip()))


def _skipped(
    real: list[Record],
    synthetic: list[Record],
    source: dict[str, Record] | None,
    target: str | None,
    sensitive: list[str],
) -> list[str]:
    skipped = []
    if not target:
        skipped.append("clinical_task_utility.target_population_rate: provide --target")
    if not _first_present(synthetic, ["expected_label", f"expected_{target}" if target else "", "expected_dept"]):
        skipped.append("clinical_task_utility.label_accuracy: provide expected_* and predicted_* columns")
    if not sensitive:
        skipped.append("equity.group_metrics: provide sensitive columns such as sex/gender/race")
    if not source:
        skipped.append("clinical_groundedness.source_validation: provide --source for source_id validation")
        skipped.append("clinical_validity.source_field_checks: provide --source")
    if not any(
        row.get("omop_domains") not in (None, "")
        or row.get("standard_vocabularies") not in (None, "")
        or any(row.get(field) not in (None, "") for field in EVENT_DATE_FIELDS)
        for row in synthetic
    ):
        skipped.append("medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields")
    return skipped


def _common_metric_columns(real: list[Record], synthetic: list[Record]) -> list[str]:
    real_cols = set().union(*(row.keys() for row in real))
    synthetic_cols = set().union(*(row.keys() for row in synthetic))
    return sorted((real_cols & synthetic_cols) - ID_COLUMNS)


def _column_similarity(real: list[Record], synthetic: list[Record], col: str) -> float:
    if _is_numeric_column(real + synthetic, col):
        return 1.0 - _ks_distance([float(v) for v in _values(real, col)], [float(v) for v in _values(synthetic, col)])
    return 1.0 - _categorical_tv(_values(real, col), _values(synthetic, col))


def _pair_similarity(real: list[Record], synthetic: list[Record], left: str, right: str) -> float:
    real_pairs = [f"{row.get(left)}::{row.get(right)}" for row in real]
    synthetic_pairs = [f"{row.get(left)}::{row.get(right)}" for row in synthetic]
    return 1.0 - _categorical_tv(real_pairs, synthetic_pairs)


def _values(rows: list[Record], col: str) -> list[Any]:
    return [row[col] for row in rows if row.get(col) not in (None, "")]


def _is_numeric_column(rows: list[Record], col: str) -> bool:
    values = _values(rows, col)
    return bool(values) and all(isinstance(v, int | float) and not isinstance(v, bool) for v in values)


def _categorical_tv(left: list[Any], right: list[Any]) -> float:
    if not left or not right:
        return 0.0
    left_counts = Counter(left)
    right_counts = Counter(right)
    keys = set(left_counts) | set(right_counts)
    return 0.5 * sum(abs(left_counts[k] / len(left) - right_counts[k] / len(right)) for k in keys)


def _ks_distance(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    values = sorted(set(left) | set(right))
    max_diff = 0.0
    for value in values:
        l_cdf = sum(1 for x in left if x <= value) / len(left)
        r_cdf = sum(1 for x in right if x <= value) / len(right)
        max_diff = max(max_diff, abs(l_cdf - r_cdf))
    return max_diff


def _fingerprint(row: Record) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in row.items() if k not in ID_COLUMNS))


def _closest_distance(row: Record, candidates: list[Record]) -> float:
    return min((_mixed_distance(row, candidate) for candidate in candidates), default=1.0)


def _mixed_distance(left: Record, right: Record) -> float:
    cols = sorted((set(left) & set(right)) - ID_COLUMNS)
    if not cols:
        return 1.0
    distances = []
    for col in cols:
        lv, rv = left.get(col), right.get(col)
        if isinstance(lv, int | float) and isinstance(rv, int | float) and not isinstance(lv, bool) and not isinstance(rv, bool):
            denom = max(abs(float(lv)), abs(float(rv)), 1.0)
            distances.append(min(abs(float(lv) - float(rv)) / denom, 1.0))
        else:
            distances.append(0.0 if lv == rv else 1.0)
    return _mean(distances)


def _entropy_ratio(real_values: list[Any], synthetic_values: list[Any]) -> float:
    real_entropy = _entropy(real_values)
    synthetic_entropy = _entropy(synthetic_values)
    if real_entropy == 0:
        return 1.0 if synthetic_entropy == 0 else 0.0
    return _clamp(synthetic_entropy / real_entropy)


def _entropy(values: list[Any]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    return -sum((count / len(values)) * math.log2(count / len(values)) for count in counts.values())


def _population_rate(rows: list[Record], col: str) -> float | None:
    values = _values(rows, col)
    return len(values) / len(rows) if rows else None


def _group_target_parity(rows: list[Record], target: str, sensitive_columns: list[str]) -> float | None:
    scores = []
    for sensitive in sensitive_columns:
        groups: dict[Any, list[Any]] = {}
        for row in rows:
            if row.get(sensitive) not in (None, "") and row.get(target) not in (None, ""):
                groups.setdefault(row[sensitive], []).append(row[target])
        if len(groups) < 2:
            continue
        distributions = list(groups.values())
        base = distributions[0]
        scores.extend(1.0 - _categorical_tv(base, other) for other in distributions[1:])
    return _mean(scores) if scores else None


def _token_support(claim: str, evidence: str) -> float:
    claim_tokens = _tokens(claim)
    evidence_tokens = _tokens(evidence)
    if not claim_tokens:
        return 1.0
    return len(claim_tokens & evidence_tokens) / len(claim_tokens)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in "".join(ch if ch.isalnum() else " " for ch in text).split() if len(token) > 1}


def _valid_rate(rows: list[Record], predicate) -> float:
    return sum(1 for row in rows if predicate(row)) / len(rows) if rows else 0.0


def _first_present(rows: list[Record], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate and any(candidate in row for row in rows):
            return candidate
    return None


def _has_column(rows: list[Record], col: str) -> bool:
    return any(col in row for row in rows)


def _mean(values) -> float:
    cleaned = [float(v) for v in values if isinstance(v, int | float) and not isinstance(v, bool)]
    return _clamp(sum(cleaned) / len(cleaned)) if cleaned else 0.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
