# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.7613`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.4916 | column_similarity=0.5850, pairwise_similarity=0.3982, columns_compared=8, pairs_compared=6 |
| clinical_task_utility | 1.0000 | target_population_rate=1.0000 |
| privacy | 0.6687 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.3374, records_compared=23, distance_synthetic_records=23, distance_reference_records=22, distance_sampled=False |
| equity | n/a | skipped=no_sensitive_columns |
| medical_diversity | 0.8847 | category_coverage=0.7401, entropy_ratio=0.9140, unique_record_ratio=1.0000, categorical_columns=4 |

## Skipped
- equity.group_metrics: provide sensitive columns such as sex/gender/race
- medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields
