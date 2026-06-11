# SDE-Bench Report

- dataset: `synthetic_good`
- overall_score: `0.8277`

| Axis | Score | Key metrics |
|---|---:|---|
| fidelity | 0.9583 | column_similarity=0.9167, pairwise_similarity=1.0000, columns_compared=4, pairs_compared=3 |
| utility | 0.8333 | label_accuracy=0.6667, label_support=3, target_population_rate=1.0000 |
| privacy | 0.5022 | exact_duplicate_rate=0.0000, median_distance_to_reference=0.0045, records_compared=3 |
| fairness | 0.5000 | sensitive_columns=sex, sensitive_distribution_similarity=1.0000, group_target_parity=0.0000 |
| diversity | 1.0000 | category_coverage=1.0000, entropy_ratio=1.0000, unique_record_ratio=1.0000, categorical_columns=3 |
| groundedness | 1.0000 | source_attribution_rate=1.0000, evidence_support_score=1.0000, evidence_support_n=3 |
| domain_consistency | 1.0000 | age_validity=1.0000, non_empty_diagnosis_rate=1.0000, dept_consistency=1.0000, diagnosis_source_overlap=1.0000 |
