# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.6956`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.2289 | column_similarity=0.3764, pairwise_similarity=0.0814, columns_compared=5, pairs_compared=6 |
| clinical_task_utility | 1.0000 | target_population_rate=1.0000 |
| privacy | 0.7249 | exact_duplicate_rate=0.0012, median_distance_to_reference=0.4511, records_compared=5120, distance_synthetic_records=1000, distance_reference_records=1000, distance_sampled=True |
| equity | n/a | skipped=no_sensitive_columns |
| medical_diversity | 0.7198 | category_coverage=0.3117, entropy_ratio=1.0000, unique_record_ratio=0.8477, categorical_columns=4 |
| clinical_scope_generalizability | 0.3827 | department_scope=0.0000, department_unique=0, diagnosis_scope=1.0000, diagnosis_unique=505, procedure_scope=0.0000, procedure_unique=0, demographic_scope=0.4210, age_group_unique=5, sex_or_gender_unique=0, scenario_scope=0.0000, scenario_unique=0, task_scope=0.8750, task_signal_unique=3 |
| clinical_groundedness | 0.8128 | source_attribution_rate=1.0000, evidence_support_score=0.6256, evidence_support_n=5118 |
| clinical_validity | 1.0000 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, icd10_format_validity=1.0000, procedure_completeness=1.0000, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | n/a | skipped=no_interoperability_fields |

## Skipped
- equity.group_metrics: provide sensitive columns such as sex/gender/race
- medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields
