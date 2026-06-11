# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.5075`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.4916 | column_similarity=0.5850, pairwise_similarity=0.3982, columns_compared=8, pairs_compared=6 |
| clinical_task_utility | n/a | target_population_rate=1.0000 |
| privacy | 0.6687 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.3374, records_compared=23, distance_synthetic_records=23, distance_reference_records=22, distance_sampled=False |
| equity | n/a | skipped=no_sensitive_columns |
| medical_diversity | 0.8847 | category_coverage=0.7401, entropy_ratio=0.9140, unique_record_ratio=1.0000, categorical_columns=4 |
| clinical_scope_breadth | 0.0000 | department_scope=0.0000, department_unique=0, diagnosis_scope=0.0000, diagnosis_unique=0, procedure_scope=0.0000, procedure_unique=0, demographic_scope=0.0000, age_group_unique=0, sex_or_gender_unique=0, scenario_scope=0.0000, scenario_unique=0, task_scope=0.0000, task_signal_unique=0 |
| clinical_groundedness | 1.0000 | source_attribution_rate=1.0000, evidence_support_n=0 |
| clinical_validity | 0.0000 | non_empty_diagnosis_rate=0.0000 |
| medical_interoperability | n/a | skipped=no_interoperability_fields |

## Skipped
- equity.group_metrics: provide sensitive columns such as sex/gender/race
- clinical_groundedness.source_validation: provide --source for source_id validation
- clinical_validity.source_field_checks: provide --source
- medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields
