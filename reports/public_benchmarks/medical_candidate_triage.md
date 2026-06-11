# Medical Public Synthetic Dataset Triage

This triage keeps the next SDE-Bench expansion medical-first. Science datasets
remain useful later, but they should not displace the medical evidence tier.

## Current Evaluated Medical Baseline

| Dataset ID | Native Form | Current Report |
|---|---|---|
| `kmuc_patient_cases_lay` | JSONL + KMUC retrieval predictions | `reports/kmuc_sde_report.md` |
| `medsynth_dialogue_note` | dialogue-note CSV | `reports/public_benchmarks/medsynth/report.md` |
| `simsum_respiratory` | semicolon respiratory CSV | `reports/public_benchmarks/simsum/report.md` |
| `synthea_ehr_sample` | Synthea CSV tables | `reports/public_benchmarks/synthea/report.md` |
| `health_gym_art_hiv` | longitudinal monthly CSV | `reports/public_benchmarks/health_gym/report.md` |

## Candidate Triage

| Candidate | Medical Fit | Public Artifact Status | Native/Paper Metric | SDE-Bench Mapping | Decision |
|---|---|---|---|---|---|
| Health Gym ICU: acute hypotension and sepsis | Strong: synthetic ICU longitudinal EHR from MIMIC-III cohorts | PhysioNet project exists, but file access is restricted to credentialed users who sign the DUA | Realism/distribution checks, no-copy Euclidean distance, disclosure risk, RL action/state utility | Flatten patient-time records with vitals, labs, actions, `patient_id`, timestep, diagnosis group, and sepsis/hypotension target | Best scientific next target if credentials are available; not suitable for fully automatic unauthenticated benchmark download |
| CMS DE-SynPUF claims | Strong: CMS synthetic Medicare claims format | CMS landing page is public, but current page exposes documentation more clearly than direct bulk claim files | Claims-format familiarity, privacy-preserving synthetic public use, limited inferential value | Join beneficiary, inpatient/outpatient/carrier/prescription claim tables into encounter records | Good next claims-domain target after confirming active file URLs or mirroring policy |
| SM3-Text-to-Query | Medium: Synthea-derived medical database and query benchmark | Paper describes multi-model dataset; public artifact must be located before adapter work | SQL/MQL/Cypher/SPARQL execution accuracy on 40K query pairs | Separate patient tables from query pairs; keep text-to-query as original-benchmark family | Defer until artifact is confirmed; native metric is task benchmark, not dataset-quality benchmark |
| MedSyn Russian clinical notes | Medium-high: LLM-generated medical notes with ICD-10 labels | Paper reports 41K open-source Russian clinical notes; artifact location still needs confirmation | ICD code prediction improvement from synthetic notes | Map note text to `claim`, ICD label to `icd10_codes`/`diagnosis_group`; multilingual grounding must be treated carefully | Promising LLM-text comparator after locating dataset release |

## Recommendation

1. Treat Health Gym ICU as the strongest medical-scientific next evaluation if
   PhysioNet credentials are available.
2. Treat CMS DE-SynPUF as the best open claims-format target after direct file
   URLs are confirmed.
3. Keep SM3 and MedSyn as candidate rows until their downloadable artifacts are
   located and license terms are explicit.
4. Do not start science-domain adapters until the medical candidate queue has at
   least one more evaluated public dataset beyond the current five.

## Evidence URLs

- CMS DE-SynPUF landing page: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files
- Health Gym GitHub overview: https://github.com/NicKuo-ResearchStuff/Health_Gym_AI
- Health Gym ICU PhysioNet project: https://physionet.org/content/synthetic-mimic-iii-health-gym/1.0.0/
- SM3 arXiv record: https://arxiv.org/abs/2411.05521
- MedSyn arXiv record: https://arxiv.org/abs/2408.02056
