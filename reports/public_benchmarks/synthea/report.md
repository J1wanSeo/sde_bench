# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.8226`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.3033 | column_similarity=0.5054, pairwise_similarity=0.1011, columns_compared=16, pairs_compared=28 |
| clinical_task_utility | 0.9898 | target_population_rate=0.9898 |
| privacy | 0.7521 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.5042, records_compared=586 |
| equity | 0.7254 | sensitive_columns=sex,race,ethnicity, sensitive_distribution_similarity=0.9752, group_target_parity=0.4755 |
| medical_diversity | 0.8123 | category_coverage=0.4575, entropy_ratio=0.9793, unique_record_ratio=1.0000, categorical_columns=15 |
| clinical_groundedness | 1.0000 | source_attribution_rate=1.0000, evidence_support_score=1.0000, evidence_support_n=586 |
| clinical_validity | 0.9978 | age_validity=1.0000, non_empty_diagnosis_rate=0.9898, icd10_format_validity=1.0000, procedure_completeness=0.9949, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | 1.0000 | omop_domain_coverage=1.0000, standard_vocabulary_rate=1.0000, temporal_traceability=1.0000, relational_integrity=1.0000 |
