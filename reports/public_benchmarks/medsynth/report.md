# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.7811`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.2289 | column_similarity=0.3764, pairwise_similarity=0.0814, columns_compared=5, pairs_compared=6 |
| clinical_task_utility | 1.0000 | target_population_rate=1.0000 |
| privacy | 0.7061 | exact_duplicate_rate=0.0012, median_distance_to_reference=0.4133, records_compared=5120 |
| equity | 1.0000 | skipped=no_sensitive_columns |
| medical_diversity | 0.7198 | category_coverage=0.3117, entropy_ratio=1.0000, unique_record_ratio=0.8477, categorical_columns=4 |
| clinical_groundedness | 0.8128 | source_attribution_rate=1.0000, evidence_support_score=0.6256, evidence_support_n=5118 |
| clinical_validity | 1.0000 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, icd10_format_validity=1.0000, procedure_completeness=1.0000, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |

## Skipped
- equity.group_metrics: provide sensitive columns such as sex/gender/race
