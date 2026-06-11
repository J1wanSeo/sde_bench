# SDE-Bench Report

- dataset: `synthetic`
- overall_score: `0.8817`

| Axis | Score | Key metrics |
|---|---:|---|
| medical_fidelity | 0.5969 | column_similarity=0.8346, pairwise_similarity=0.3593, columns_compared=21, pairs_compared=28 |
| clinical_task_utility | 0.9992 | target_population_rate=0.9992 |
| privacy | 0.7538 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.5075, records_compared=33387, distance_synthetic_records=1000, distance_reference_records=1000, distance_sampled=True |
| equity | 0.9201 | sensitive_columns=sex,race, sensitive_distribution_similarity=0.9916, group_target_parity=0.8485 |
| medical_diversity | 0.9279 | category_coverage=0.7850, entropy_ratio=0.9986, unique_record_ratio=1.0000, categorical_columns=18 |
| clinical_groundedness | 1.0000 | source_attribution_rate=1.0000, evidence_support_score=1.0000, evidence_support_n=33387 |
| clinical_validity | 0.9393 | age_validity=1.0000, non_empty_diagnosis_rate=0.9992, icd9_format_validity=1.0000, procedure_completeness=0.5762, acuity_validity=1.0000, laterality_validity=1.0000, diagnosis_source_overlap=1.0000 |
| medical_interoperability | 0.9165 | omop_domain_coverage=0.6667, standard_vocabulary_rate=1.0000, temporal_traceability=0.9992, relational_integrity=1.0000 |
