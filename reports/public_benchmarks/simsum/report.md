# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.7021`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.9531 | column_similarity=0.9705, pairwise_similarity=0.9357, columns_compared=17, pairs_compared=15 |
| clinical_task_utility | 1.0000 | target_population_rate=1.0000 |
| privacy | 0.1340 | exact_duplicate_rate=0.7320, median_distance_to_reference=0.0000, records_compared=1000, distance_synthetic_records=1000, distance_reference_records=1000, distance_sampled=False |
| equity | n/a | skipped=no_sensitive_columns |
| medical_diversity | 0.7648 | category_coverage=1.0000, entropy_ratio=0.9364, unique_record_ratio=0.3580, categorical_columns=6 |
| clinical_scope_breadth | 0.2086 | department_scope=0.0000, department_unique=0, diagnosis_scope=0.3764, diagnosis_unique=3, procedure_scope=0.0000, procedure_unique=0, demographic_scope=0.0000, age_group_unique=0, sex_or_gender_unique=0, scenario_scope=0.0000, scenario_unique=0, task_scope=0.8750, task_signal_unique=3 |
| clinical_groundedness | 0.8540 | source_attribution_rate=1.0000, evidence_support_score=0.7079, evidence_support_n=964 |
| clinical_validity | 1.0000 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, procedure_completeness=1.0000, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | n/a | skipped=no_interoperability_fields |

## Skipped
- equity.group_metrics: provide sensitive columns such as sex/gender/race
- medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields
