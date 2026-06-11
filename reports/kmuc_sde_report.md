# SDE-Bench Report

- dataset: `synthetic_lay`
- overall_score: `0.8092`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 1.0000 | column_similarity=1.0000, pairwise_similarity=1.0000, columns_compared=8, pairs_compared=21 |
| clinical_task_utility | 0.8733 | label_accuracy=0.7467, label_support=150, target_population_rate=1.0000 |
| privacy | 0.5000 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.0000, records_compared=750 |
| equity | 0.8474 | sensitive_columns=sex, sensitive_distribution_similarity=1.0000, group_target_parity=0.6949 |
| medical_diversity | 1.0000 | category_coverage=1.0000, entropy_ratio=1.0000, unique_record_ratio=1.0000, categorical_columns=7 |
| clinical_groundedness | 0.5028 | source_attribution_rate=1.0000, evidence_support_score=0.0056, evidence_support_n=750 |
| clinical_validity | 0.9408 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, icd10_format_validity=1.0000, procedure_completeness=0.5267, acuity_validity=1.0000, laterality_validity=1.0000, dept_consistency=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | n/a | skipped=no_interoperability_fields |

## Skipped
- medical_interoperability: provide OMOP/FHIR/CSV-derived interoperability fields
