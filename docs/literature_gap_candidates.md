# Literature-Backed Gap Candidates for SDE-Bench

This document identifies defensible weakness candidates in existing synthetic
medical dataset evaluation practice and maps each gap to a quantifiable
SDE-Bench axis or extension.

Status: working manuscript evidence note, checked against public paper pages on
2026-06-12.

## 1. Evidence Base

The current claim should be built from three evidence groups:

1. General synthetic-health evaluation frameworks.
   - Yan et al. introduce a multifaceted synthetic EHR benchmark focused on
     utility and privacy, and emphasize that no generation method is best across
     all criteria or use cases.
   - The 2024 primer on synthetic health data notes unresolved questions about
     how to consistently evaluate similarity, predictive utility, and privacy
     risk, and notes that governance issues remain under-addressed.

2. Public synthetic medical dataset papers.
   - MedSynth evaluates synthetic dialogue-note pairs mainly through
     Dial-2-Note and Note-2-Dial utility.
   - SimSUM evaluates a controlled respiratory benchmark linking structured
     background variables, notes, and symptom annotations, and explicitly states
     it is for reproducible research in a simplified setting rather than
     production-grade clinical decision support.
   - Synthea emphasizes standards-based synthetic EHR availability, FHIR/C-CDA
     output, and nonclinical secondary uses, while also acknowledging limits for
     clinical research and biomedical discovery.
   - Health Gym validates distributions, statistical tests, correlations over
     time, disclosure risk, and RL action utility for longitudinal datasets.
   - CMS DE-SynPUF provides claims-format public-use data, but its purpose is
     software development and training rather than clinical inferential
     validity.

3. Recent critiques of synthetic clinical data evaluation.
   - Fairness studies report that synthetic health data can have different
     fairness properties from real data and is not bias-free.
   - Recent synthetic clinical text evaluation reports that narrow similarity or
     utility checks miss factuality problems such as context misinterpretation,
     temporal confusion, measurement errors, and fabricated claims.
   - A 2026 structured-EMR evaluation preprint argues that statistical
     similarity and predictive performance can overestimate synthetic data
     quality when clinical validity, subgroup structure, effect estimates, and
     dependency structure are distorted.

## 2. Gap Matrix

| Gap Candidate | Literature Signal | Why Existing Benchmarks Miss It | Quantitative SDE-Bench Interpretation | Priority |
|---|---|---|---|---|
| Context-dependent utility | Yan et al. emphasize utility/privacy tradeoffs and context-specific assessment. MedSynth reports task-specific Dial-2-Note/Note-2-Dial utility. | A single downstream task does not establish utility for other clinical workflows. | Report task-specific utility only when expected/predicted labels exist; add task coverage and native-task mapping. | High |
| Clinical validity beyond statistical fidelity | Synthea notes superficial validation and limited validity assessment in prior SDG literature; recent structured-EMR work argues fidelity can mask poor clinical validity. | Marginal/pairwise similarity can preserve distributions while allowing clinically incoherent records. | `clinical_validity = mean(age_validity, diagnosis completeness, ICD format validity, procedure completeness, acuity/laterality validity, source consistency)`. | High |
| Factual groundedness for LLM/RAG-generated data | Synthetic clinical-note evaluation reports factuality failures including fabricated claims and temporal/context errors. | BLEU/ROUGE, note similarity, or downstream task utility do not verify that each generated claim is supported by source evidence. | `clinical_groundedness = mean(source_attribution_rate, evidence_support_score)`; extension: semantic entailment or clinician review. | High |
| Clinical scope breadth | SimSUM is intentionally respiratory and simplified; HealthGymART is strong but disease/workflow-specific; MedSynth is dialogue-note specific. | Diversity within one disease/workflow can be mistaken for broad medical-domain coverage. | `clinical_scope_breadth = mean(department, diagnosis, procedure, demographic, scenario, task scope)`. | High |
| Applicability coverage | Prior metrics are task/schema-specific; many cells are legitimately `not_applicable`. | Tables can hide that a dataset was evaluated only on axes its schema supports. | `axis_coverage = measured_axes / total_axes`; report skipped, label-missing, adapter-missing, and not-applicable counts. | High |
| Interoperability / reusable schema readiness | Synthea's central contribution is standards-based FHIR/C-CDA availability; claims datasets require CMS-like structure. | Text-generation metrics do not measure whether data can enter OMOP/FHIR/claims analytics pipelines. | `medical_interoperability = mean(OMOP domain coverage, standard vocabulary rate, temporal traceability, relational integrity)`. | High |
| Equity and subgroup representativeness | Fairness papers show synthetic healthcare data can differ from real data in fairness properties; MedEqualizer reports subgroup under/overrepresentation. | Global fidelity can look strong while protected subgroups are distorted. | `equity = mean(sensitive_distribution_similarity, group_target_parity)`; extension: subgroup coverage and disparity ratios. | High |
| Privacy threat-model specificity | Yan et al. and Health Gym evaluate privacy/disclosure risk, but privacy is use-case and threat-model dependent. | Nearest-neighbor distance alone is not enough; privacy can differ for source-linked transformations vs de novo generation. | Report exact duplicates and nearest-reference distance as a screen; extension: membership inference, attribute disclosure, source-linked vs de novo privacy labels. | Medium-High |
| Longitudinal and temporal coherence | Health Gym explicitly validates correlations and trends over time; recent clinical-text work reports temporal confusion. | Static tabular fidelity does not test time ordering, disease progression, or temporal consistency. | Extension axis: `temporal_coherence = mean(valid_event_order_rate, trend_similarity, transition_validity)`. | Medium-High |
| Causal / inferential validity | Recent structured-EMR critique argues models can distort effect estimates and dependency structure despite good fidelity. | Predictive utility does not prove that synthetic data support valid clinical or scientific conclusions. | Extension axis: compare dependency graph, effect estimate preservation, calibration, and subgroup effect consistency. | Medium-High |
| Reproducibility of evaluation | Synthea background highlights incomplete documentation as a barrier to validation and reuse; prior dataset metrics vary by task. | Paper-reported metrics alone are not independent reproduction. | Track `computed`, `paper_reported`, `requires_adapter`, `requires_labels`, and `not_applicable`; report recomputed-vs-reported evidence split. | Medium |
| Domain-specific clinical rule coverage | Synthea uses disease modules and care maps; SimSUM uses expert Bayesian structure. | Generic syntactic validity does not prove specialty-specific correctness. | Extension: rule-pack coverage by specialty, contraindication checks, disease-procedure consistency, guideline consistency. | Medium |

## 3. Quantitative Prior-Paper Coverage Coding

This section converts the qualitative literature gaps into a conservative
coverage score. The goal is not to rank prior papers. The goal is to show which
medical synthetic-data evidence dimensions are repeatedly under-covered by
dataset-specific evaluations.

Coding rule:

```text
Direct (D) = 1.0
Partial or proxy (P) = 0.5
Missing or not reported as an evaluation axis (M) = 0.0

weighted_coverage(axis) =
    sum(score(paper, axis) for paper in reviewed_dataset_papers)
    / count(reviewed_dataset_papers)

gap_score(axis) = 1 - weighted_coverage(axis)
```

Reviewed dataset/self-evaluation sources:

- MedSynth
- SimSUM
- Synthea
- Health Gym
- CMS DE-SynPUF

CSV companion: `docs/literature_gap_coverage.csv`.

### 3.1 Dataset-Paper Coverage Matrix

| Evidence Dimension | MedSynth | SimSUM | Synthea | Health Gym | DE-SynPUF | Weighted Coverage | Gap Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Task utility | D | D | P | D | P | 0.80 | 0.20 |
| Statistical fidelity / realism | P | P | P | D | P | 0.60 | 0.40 |
| Privacy / disclosure risk | M | M | P | D | P | 0.40 | 0.60 |
| Interoperability / format readiness | M | P | D | P | D | 0.60 | 0.40 |
| Clinical validity | P | P | P | P | M | 0.40 | 0.60 |
| Source groundedness / factuality | M | D | M | M | M | 0.20 | 0.80 |
| Clinical scope breadth | P | M | P | M | P | 0.30 | 0.70 |
| Equity / subgroup representativeness | M | M | M | M | M | 0.00 | 1.00 |
| Applicability / missingness coverage | M | M | M | M | M | 0.00 | 1.00 |

Interpretation:

- Prior dataset papers usually provide strong evidence for their native task or
  format.
- The largest repeat gaps are equity/subgroup representativeness,
  applicability coverage, source groundedness/factuality, clinical scope
  breadth, clinical validity, and privacy threat-model specificity.
- These high-gap dimensions justify SDE-Bench's medical-domain additions more
  strongly than a generic fidelity/utility/privacy benchmark alone.

### 3.2 Conservative Coding Rationale

| Evidence Dimension | Coding Rationale |
|---|---|
| Task utility | Direct when the paper reports downstream generation, extraction, RL action, or software-development utility; partial when utility is implied for nonclinical development or training. |
| Statistical fidelity / realism | Direct only when real-vs-synthetic distributions, moments, or correlations are explicitly validated; partial when realism is supported by simulation design, disease distributions, or public statistics but not a full validation metric. |
| Privacy / disclosure risk | Direct when disclosure risk is quantitatively assessed; partial when privacy protection is argued from fully synthetic generation or claims-public-use design without a full attack metric. |
| Interoperability / format readiness | Direct when standard formats or claims-compatible schemas are central; partial when records are structured but not mapped to healthcare interoperability standards. |
| Clinical validity | Direct would require explicit clinical-rule or structural-validity scoring; current reviewed dataset papers are at most partial, using care maps, expert Bayesian structures, or plausibility-oriented design. |
| Source groundedness / factuality | Direct when generated text is explicitly linked to structured evidence or annotated spans; missing when fluency, task utility, or format validity is reported without claim-level support checks. |
| Clinical scope breadth | Partial when a dataset reports broad code, condition, or claims coverage; missing when it is intentionally disease-, task-, or workflow-specific without a breadth metric. |
| Equity / subgroup representativeness | Direct would require protected-attribute subgroup preservation or downstream fairness metrics; none of the reviewed dataset self-evaluations make this a primary benchmark axis. |
| Applicability / missingness coverage | Direct would require reporting which common benchmark axes could or could not be measured for each dataset; reviewed papers are single-dataset evaluations and do not report cross-dataset applicability coverage. |

## 4. Original Benchmark to SDE-Bench Axis Crosswalk

This table asks a different question from Section 3: for each benchmark or
evaluation protocol used by existing synthetic medical dataset papers, which
SDE-Bench axes does it cover?

Legend:

- `O`: directly covered by the original benchmark.
- `P`: partially or indirectly covered.
- `X`: not covered as an explicit benchmark dimension.

CSV companion: `docs/original_benchmark_axis_crosswalk.csv`.

### 4.1 의료 합성 데이터를 위한 SDE-Bench 축 정의

| SDE-Bench 축 | 무엇을 보는가 | 의료 합성 데이터에서 왜 중요한가 | 기존 평가에서 빠지기 쉬운 지점 |
|---|---|---|---|
| Fidelity (충실도) | 합성 데이터가 기준 데이터의 분포, 변수별 특성, 변수 간 관계를 얼마나 보존하는지 본다. | 합성 환자군이 실제 또는 기준 환자군과 너무 다르면 모델 학습, 검증, 시뮬레이션 결과를 신뢰하기 어렵다. | 전체 분포가 비슷해 보여도 개별 레코드의 의학적 모순이나 근거 없는 서술은 놓칠 수 있다. |
| Utility (활용성) | 합성 데이터가 진단, 분류, 검색, 추출, 예측 같은 downstream clinical task에 실제로 도움이 되는지 본다. | 의료 데이터셋은 단순히 그럴듯한 것보다 임상 태스크에 필요한 신호를 보존해야 한다. | 기존 논문은 자기 데이터셋의 native task 성능은 잘 보이지만, 다른 임상 워크플로우로 일반화되는지는 약하다. |
| Privacy (프라이버시) | 원본 환자나 레코드를 그대로 외우거나, 원본과 과도하게 가까운 샘플을 만드는지 본다. | 의료 데이터는 재식별과 민감정보 노출 위험이 크기 때문에 합성 데이터라도 privacy screen이 필요하다. | 합성 생성이라는 이유만으로 안전하다고 가정하거나, 데이터셋별 제한적인 disclosure check에 머무르는 경우가 많다. |
| Equity (형평성) | 성별, 연령, 인종, 보험 유형, 질환군 등 subgroup의 분포와 target pattern이 왜곡되지 않았는지 본다. | 합성 데이터가 특정 집단을 과소대표하거나 편향을 증폭하면, 그 데이터로 학습한 의료 모델도 불공정해질 수 있다. | 전체 평균 성능이나 전체 분포만 보고 subgroup fairness를 별도 축으로 평가하지 않는 경우가 많다. |
| Diversity (다양성) | 데이터 내부의 반복, mode collapse, 범주 coverage, entropy 보존 정도를 본다. | 반복적이고 좁은 합성 데이터는 겉보기 성능을 높일 수 있지만 실제 임상 variation을 충분히 반영하지 못한다. | 단순 샘플 수, 코드 수, 질환 수를 보고하지만 support 보존이나 collapse 여부를 직접 측정하지 않는 경우가 있다. |
| Scope (범위) | 진료과, 질환, 처치, 인구통계, 시나리오, task signal이 얼마나 넓게 포함되는지 본다. | 범용 의료 합성 데이터셋이라면 특정 질환이나 단일 workflow 내부의 다양성뿐 아니라 여러 임상 영역으로 재사용 가능한지가 중요하다. | HIV, 호흡기, claims, dialogue-note처럼 유용하지만 좁은 데이터셋이 broad medical benchmark처럼 해석될 위험이 있다. |
| Groundedness (근거성) | 생성된 clinical claim이 source evidence에 연결되고, 그 evidence로 실제 지지되는지 본다. | LLM/RAG 기반 합성 데이터는 문장이 자연스럽고 task 성능이 좋아도 진단, 시간관계, 처치 근거를 hallucinate할 수 있다. | BLEU/ROUGE, extraction F1, realism, utility만으로는 claim-level evidence support를 보장하지 못한다. |
| Validity (임상 타당성) | 나이, 진단, ICD code, 처치, 중증도, laterality, 진료과, source consistency 등 개별 레코드가 의학적으로 말이 되는지 본다. | 분포가 맞아도 개별 환자 기록이 임상적으로 불가능하거나 구조적으로 틀리면 의료 데이터셋으로 쓰기 어렵다. | 기존 평가는 전역 분포나 task 성능을 보면서 clinical-rule 기반의 record-level validity를 생략하기 쉽다. |
| Interoperability (상호운용성) | OMOP, FHIR, claims, EHR-style 분석에 필요한 표준 domain, vocabulary, 날짜, 관계형 link가 있는지 본다. | 의료 데이터는 연구용 표뿐 아니라 실제 분석 파이프라인과 표준 용어체계에 연결될 수 있어야 재사용성이 높다. | 텍스트 중심 또는 task-specific 데이터셋은 schema readiness, standard vocabulary, relational integrity를 평가하지 않는 경우가 많다. |
| Applicability (적용가능성) | 각 axis가 해당 데이터셋에서 실제 측정 가능한지, label/schema/adapter 부족으로 빠지는지, 또는 본질적으로 해당 없는지를 명시한다. | 여러 데이터셋을 비교할 때 일부 축만 측정된 높은 점수와 모든 축에서 측정된 점수를 같은 의미로 해석하면 안 된다. | 단일 데이터셋 논문은 자신에게 가능한 metric만 보고하며, cross-dataset comparability 자체를 수치화하지 않는 경우가 많다. |

### 4.2 Original Benchmark Coverage Table

| Existing Dataset / Benchmark Used | Fidelity | Utility | Privacy | Equity | Diversity | Scope | Groundedness | Validity | Interop | Applicability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MedSynth Dial-2-Note / Note-2-Dial utility | P | O | X | X | P | P | X | P | X | X |
| SimSUM symptom extraction F1 / span annotations | P | O | X | X | P | X | O | P | P | X |
| Synthea standards-based EHR availability | P | P | P | X | P | P | X | P | O | X |
| Health Gym realism, disclosure risk, RL utility | O | O | O | X | O | X | X | P | P | X |
| CMS DE-SynPUF claims format compatibility | P | P | P | X | P | P | X | X | O | X |

Axis coverage score:

```text
O = 1.0
P = 0.5
X = 0.0

benchmark_axis_coverage(row) =
    sum(axis scores for row) / count(SDE-Bench axes)
```

| Existing Dataset / Benchmark Used | Covered Axes Score | Missing Axes Score | Main Missing SDE-Bench Axes |
|---|---:|---:|---|
| MedSynth Dial-2-Note / Note-2-Dial utility | 0.30 | 0.70 | privacy, equity, groundedness, interoperability, applicability |
| SimSUM symptom extraction F1 / span annotations | 0.40 | 0.60 | privacy, equity, scope breadth, applicability |
| Synthea standards-based EHR availability | 0.40 | 0.60 | equity, groundedness, applicability |
| Health Gym realism, disclosure risk, RL utility | 0.50 | 0.50 | equity, scope breadth, groundedness, applicability |
| CMS DE-SynPUF claims format compatibility | 0.35 | 0.65 | equity, groundedness, clinical validity, applicability |

Interpretation:

- Existing benchmarks cover their own intended contribution well.
- None of the reviewed original benchmarks covers all SDE-Bench axes.
- The most consistently missing axes are equity, source groundedness, and
  applicability coverage.
- This gives a quantitative rationale for SDE-Bench as a broader medical-domain
  benchmark rather than just another original-metric aggregation.

## 5. Highest-Value SDE-Bench Justification Candidates

These are the strongest axes to emphasize in a JMIR-style paper because they are
both literature-motivated and quantifiable in the current SDE-Bench direction.

### 5.1 Applicability Coverage

Problem:

Existing original metrics are not universally applicable. A benchmark table with
many `not_applicable` cells is not a same-axis comparison.

Metric:

```text
axis_coverage(dataset) =
    count(axis status == measured) / count(all SDE-Bench axes)
```

Recommended additional fields:

```text
missing_label_rate = count(axis status == requires_labels) / count(all axes)
adapter_gap_rate = count(axis status == requires_adapter) / count(all axes)
not_applicable_rate = count(axis status == not_applicable) / count(all axes)
```

Manuscript use:

> We report performance and coverage separately so a high score over a narrow
> subset of axes is not interpreted as broad medical benchmark superiority.

### 5.2 Clinical Validity

Problem:

Synthetic EHRs can match distributions while containing clinically implausible
or structurally invalid records.

Current SDE-Bench metric:

```text
clinical_validity =
    mean(age_validity,
         non_empty_diagnosis_rate,
         icd10_format_validity,
         icd9_format_validity,
         procedure_completeness,
         acuity_validity,
         laterality_validity,
         dept_consistency,
         diagnosis_source_overlap)
```

Manuscript use:

> We separate clinical validity from statistical fidelity because distributional
> similarity does not guarantee medically coherent individual records.

### 5.3 Clinical Groundedness

Problem:

LLM/RAG-generated synthetic records require evidence traceability. Similarity
metrics or downstream utility can miss hallucinated or unsupported claims.

Current SDE-Bench metric:

```text
clinical_groundedness =
    mean(source_attribution_rate, evidence_support_score)
```

Near-term extension:

```text
semantic_groundedness =
    mean(clinician_or_llm_entailment(claim, source_evidence))
```

Manuscript use:

> For RAG-derived synthetic datasets, we evaluate whether generated clinical
> claims remain traceable to source evidence, rather than treating fluent
> clinical text as sufficient.

### 5.4 Clinical Scope Breadth

Problem:

Internal diversity within one condition or workflow is not the same as broad
medical-domain coverage.

Current SDE-Bench metric:

```text
clinical_scope_breadth =
    mean(department_scope,
         diagnosis_scope,
         procedure_scope,
         demographic_scope,
         scenario_scope,
         task_scope)
```

Manuscript use:

> We distinguish medical diversity from clinical scope breadth so that a narrow
> but high-quality longitudinal dataset is not mistaken for a broad
> multi-specialty clinical benchmark.

### 5.5 Equity / Subgroup Representativeness

Problem:

Synthetic health data can preserve global distributions while shifting subgroup
representation or downstream fairness.

Current SDE-Bench metric:

```text
equity =
    mean(sensitive_distribution_similarity, group_target_parity)
```

Extension:

```text
subgroup_representation_error =
    mean_g abs(P_synthetic(g) - P_reference(g))
```

Manuscript use:

> We include subgroup representativeness because synthetic medical data are not
> automatically bias-free and global fidelity is insufficient for clinical
> fairness claims.

## 6. Candidate Contribution Statement

Recommended wording:

> Prior synthetic medical dataset studies usually validate datasets using
> task-specific or format-specific evidence, such as downstream generation
> utility, symptom extraction F1, statistical fidelity, disclosure risk, or
> standards-based availability. These evaluations are valuable but do not
> jointly quantify clinical validity, source groundedness, medical scope
> breadth, equity, interoperability, and benchmark applicability coverage.
> SDE-Bench addresses this gap by turning these under-evaluated dimensions into
> explicit, reportable axes and by distinguishing measured scores from skipped
> or non-applicable axes.

Korean version:

> 기존 합성 의료 데이터셋 연구들은 주로 각 데이터셋의 목적에 맞는
> downstream utility, symptom extraction F1, 통계적 유사도, disclosure risk,
> 표준 포맷 제공 여부 등을 중심으로 평가해 왔다. 그러나 이러한 평가는
> clinical validity, source groundedness, medical scope breadth, equity,
> interoperability, benchmark applicability coverage를 동시에 정량화하지
> 못한다. SDE-Bench는 이 누락된 의료 도메인 요구사항을 별도의 평가축으로
> 정의하고, 측정 가능한 축과 적용 불가능한 축을 분리하여 보고한다.

## 7. Source Notes

- Yan et al., "A Multifaceted Benchmarking of Synthetic Electronic Health Record
  Generation Models": https://arxiv.org/abs/2208.01230
- Walonoski et al., "Synthea: An approach, method, and software mechanism for
  generating synthetic patients and the synthetic electronic health care
  record": https://academic.oup.com/jamia/article/25/3/230/4098271
- Kuo et al., "The Health Gym: synthetic health-related datasets for the
  development of reinforcement learning algorithms":
  https://www.nature.com/articles/s41597-022-01784-7
- Mianroodi et al., "MedSynth: Realistic, Synthetic Medical Dialogue-Note
  Pairs": https://arxiv.org/abs/2508.01401
- Rabaey et al., "SimSUM: Simulated Benchmark with Structured and Unstructured
  Medical Records": https://arxiv.org/abs/2409.08936
- Liu et al., "Systematic Evaluation of the Quality of Synthetic Clinical Notes
  Rephrased by LLMs at Million-Note Scale": https://arxiv.org/abs/2605.17775
- Bhanot et al., "Downstream Fairness Caveats with Synthetic Healthcare Data":
  https://arxiv.org/abs/2203.04462
- Salarian et al., "MedEqualizer: A Framework Investigating Bias in Synthetic
  Medical Data and Mitigation via Augmentation": https://arxiv.org/abs/2511.01054
- Bartell et al., "A primer on synthetic health data":
  https://arxiv.org/abs/2401.17653
- Kuo et al., "Synthetic but Not Realistic: The Evaluation Challenge in
  Generative Modelling for Structured Electronic Medical Records":
  https://arxiv.org/abs/2606.08903
