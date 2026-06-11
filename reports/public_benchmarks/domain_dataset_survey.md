# Public Synthetic Dataset Survey

This report expands SDE-Bench beyond the currently evaluated medical datasets while keeping medical evidence as the primary tier.

## Selection Policy

1. Keep medical datasets as the primary evidence tier.
2. Add finance and science datasets only when the native files can be mapped to JSON/JSONL/CSV records.
3. Preserve each original paper benchmark separately from SDE-Bench common-axis evaluation.
4. Report candidate cells as not_applicable or requires_adapter until an adapter and command exist.

## Domain Coverage

| Domain | Count |
|---|---:|
| finance | `3` |
| medical | `7` |
| science | `3` |

## Evaluated Baseline

| Dataset ID | Domain | Dataset | Current Report |
|---|---|---|---|
| `kmuc_patient_cases_lay` | medical | KMUC synthetic lay cases | reports/kmuc_sde_report.md |
| `medsynth_dialogue_note` | medical | MedSynth | reports/public_benchmarks/medsynth/report.md |
| `simsum_respiratory` | medical | SimSUM | reports/public_benchmarks/simsum/report.md |
| `synthea_ehr_sample` | medical | Synthea sample EHR | reports/public_benchmarks/synthea/report.md |

## Candidate Datasets

| Dataset ID | Domain | Priority | Status | Dataset | Native Format | Original Metric | SDE-Bench Plan | Adapter Work |
|---|---|---|---|---|---|---|---|---|
| `health_gym_icu` | medical | `P0` | `next_batch` | [Health Gym ICU/HIV synthetic health datasets](https://github.com/NicKuo-ResearchStuff/Health_Gym_AI) | longitudinal tabular time series | offline RL task utility, distribution/correlation similarity, disclosure risk | map patient trajectories to per-visit records; evaluate fidelity, privacy, diversity, validity, and structured temporal traceability | flatten ICU/HIV trajectories into JSONL with patient_id, time, vitals/labs/actions/outcomes |
| `de_synpuf_claims` | medical | `P1` | `candidate` | [CMS DE-SynPUF claims](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) | claims tables | claims analytic usefulness and privacy-preserving public release | map beneficiary, diagnosis, procedure, and claim tables to encounter records | claims parser plus ICD/procedure field normalization |
| `sm3_text_to_query` | medical | `P1` | `candidate` | [SM3-Text-to-Query](https://arxiv.org/abs/2411.05521) | synthetic Synthea-derived database plus natural-language query pairs | text-to-query execution accuracy across SQL, MQL, Cypher, and SPARQL | evaluate generated patient records separately from query-pair utility | extract patient tables from database dumps; keep query-pair task as original-benchmark family |
| `fifar_fraud_l2d` | finance | `P0` | `next_batch` | [FiFAR financial fraud alert review dataset](https://github.com/feedzai/fifar-dataset) | tabular fraud alerts plus synthetic analyst predictions | learning-to-defer assignment utility under capacity constraints | evaluate tabular fidelity/diversity/privacy with fraud label utility; report domain as finance | generic CSV/Parquet loader plus target=is_fraud and optional sensitive/workload columns |
| `synthaml_transactions` | finance | `P1` | `candidate` | [Synthetic AML transaction datasets](https://arxiv.org/abs/2306.16424) | transaction graph/table | AML detection utility and transaction realism | evaluate transaction-level fidelity/diversity/privacy and label utility; add graph metrics later | sample transaction tables; normalize account, amount, timestamp, label, and typology fields |
| `transxion_aml` | finance | `P2` | `candidate` | [TransXion AML benchmark](https://github.com/chaos-max/TransXion) | transaction graph with entity profiles | AML detection performance plus graph/profile realism | evaluate only sampled tabular projections until graph-specific axes exist | graph-to-record projection and network metric extension |
| `syntren_gene_expression` | science | `P0` | `next_batch` | [SynTReN synthetic gene expression generator](https://doi.org/10.1186/1471-2105-7-43) | gene expression matrices with known regulatory structure | network structure recovery and expression realism | treat genes as numeric features and pathways/classes as labels when available | matrix-to-record converter with sample_id, gene_* numeric columns, and optional class/condition label |
| `synthetic_spectra` | science | `P1` | `candidate` | [Universal synthetic spectroscopic dataset](https://arxiv.org/abs/2206.06031) | synthetic spectra and class labels | spectra classification accuracy across model families | evaluate numeric vector fidelity/diversity/privacy and class-label utility | spectra vector loader; optionally downsample peaks to fixed-width JSONL features |
| `superbench_sciml` | science | `P2` | `candidate` | [SuperBench scientific ML super-resolution datasets](https://arxiv.org/abs/2306.14070) | large spatiotemporal simulation arrays | super-resolution quality and physics-preservation metrics | out of current JSONL/tabular scope except metadata-level sampling | requires array/image adapter and physics-specific axes |

## Next Evaluation Batch

| Order | Dataset ID | Domain | Why Next |
|---:|---|---|---|
| 1 | `health_gym_icu` | medical | closest medical addition after Synthea because it is public, synthetic, longitudinal, and benchmark-oriented. |
| 2 | `fifar_fraud_l2d` | finance | small enough to adapt and useful as a non-medical, high-stakes synthetic decision dataset. |
| 3 | `syntren_gene_expression` | science | classic synthetic science dataset where ground-truth structure is part of the benchmark value. |
