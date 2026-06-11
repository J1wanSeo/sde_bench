# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.8991`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.7517 | column_similarity=0.8081, pairwise_similarity=0.6954, columns_compared=24, pairs_compared=28 |
| clinical_task_utility | 1.0000 | target_population_rate=1.0000 |
| privacy | 0.6104 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.2207, records_compared=300 |
| equity | 0.9500 | sensitive_columns=sex,ethnicity, sensitive_distribution_similarity=0.9000, group_target_parity=1.0000 |
| medical_diversity | 0.9225 | category_coverage=0.8500, entropy_ratio=0.9174, unique_record_ratio=1.0000, categorical_columns=20 |
| clinical_groundedness | 1.0000 | source_attribution_rate=1.0000, evidence_support_score=1.0000, evidence_support_n=300 |
| clinical_validity | 1.0000 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, icd10_format_validity=1.0000, procedure_completeness=1.0000, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | 0.9583 | omop_domain_coverage=0.8333, standard_vocabulary_rate=1.0000, temporal_traceability=1.0000, relational_integrity=1.0000 |
