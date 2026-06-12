# Manuscript Logic for SDE-Bench

This document defines the defensible manuscript logic for presenting SDE-Bench
as a medical-domain benchmark for synthetic healthcare datasets.

For the literature-backed weakness candidates that justify the SDE-Bench axes,
see `docs/literature_gap_candidates.md`.

## 1. Core Position

The paper should not claim that every prior dataset was evaluated under every
other dataset paper's original metric. Many original metrics are tied to a
specific data format or task, so `not_applicable` is an expected result rather
than a failed experiment.

The safer and stronger claim is:

> We reviewed evaluation protocols used in prior synthetic medical dataset
> studies, abstracted their recurring evidence dimensions, and designed
> SDE-Bench as a medical-domain common benchmark. We then evaluated available
> public synthetic medical datasets under this shared framework, reporting both
> axis-level scores and applicability coverage.

Korean manuscript framing:

> 본 연구는 기존 합성 의료 데이터셋 논문들이 사용한 자기평가 지표를
> 분석하고, 이를 의료 도메인 요구사항에 맞게 재구성하여 SDE-Bench를
> 설계하였다. 이후 공개적으로 이용 가능한 합성 의료 데이터셋들을 동일한
> SDE-Bench 축에서 평가하되, 각 축의 적용 가능성과 결측 사유를 함께
> 보고하였다.

## 2. Why Prior Original Metrics Cannot Be the Same-Axis Comparison

Prior synthetic medical datasets were built for different tasks:

- MedSynth: dialogue-to-note and note-to-dialogue generation utility.
- SimSUM: respiratory symptom extraction F1.
- Synthea: structured EHR generation and standards-based interoperability.
- HealthGymART: longitudinal HIV/ART realism and disclosure-risk evaluation.
- DE-SynPUF: Medicare-style claims public-use compatibility.
- KMUC: patient lay text to department/doctor matching.

These are not interchangeable benchmark tasks. A dataset without dialogue-note
pairs cannot fairly run MedSynth's original task. A dataset without respiratory
symptom labels cannot fairly run SimSUM's symptom F1. A text-only dataset cannot
be judged as an EHR/claims standard-format release without adding a separate
adapter or export layer.

Therefore, prior-paper metrics should be used as a design source and
applicability crosswalk, not as the primary same-axis comparison table.

## 3. Three-Stage Evaluation Logic

### Stage A: Original Evaluation Protocol Crosswalk

Purpose:

- Show how each prior dataset paper evaluated its own dataset.
- Extract the native task, metric formula, required inputs, and portability
conditions.
- Mark whether the metric is `computed`, `paper_reported`,
`requires_adapter`, `requires_labels`, `sde_proxy`, or `not_applicable`.

Interpretation:

- Stage A justifies SDE-Bench design by grounding it in existing literature.
- Stage A does not prove same-axis superiority across all datasets.
- `not_applicable` is reported because some original metrics require task
signals that other datasets do not contain.

Safe claim:

> Stage A summarizes and operationalizes prior datasets' native evaluation
> protocols as benchmark families.

Unsafe claim:

> Stage A evaluates all datasets on the same original-paper benchmark.

### Stage B: Common SDE-Bench Axis Evaluation

Purpose:

- Evaluate all available public synthetic medical datasets under the same
SDE-Bench axes.
- Provide the actual same-axis comparison layer.
- Report skipped or unavailable axes rather than imputing scores.

Common axes:

- medical fidelity
- clinical task utility
- privacy
- equity
- medical diversity
- clinical scope breadth
- clinical groundedness
- clinical validity
- medical interoperability

Interpretation:

- Stage B is the main benchmark result.
- The paper should emphasize axis-level profiles, not a single scalar rank.
- `overall_score` is an available-axis mean and should be used only as a compact
summary or sorting aid.

Safe claim:

> Public synthetic medical datasets were evaluated under the same SDE-Bench
> axis definitions, with axis applicability and missingness explicitly reported.

Unsafe claim:

> The highest overall score proves the best synthetic dataset.

### Stage C: Comparability Coverage

Purpose:

- Make comparability itself measurable.
- Prevent reviewers from arguing that `n/a` axes were hidden.
- Show which datasets are broadly benchmarkable and which are strong only for a
specific format or task.

Recommended coverage formula:

```text
axis_coverage(dataset) =
    count(measured SDE-Bench axes for dataset) / count(total SDE-Bench axes)
```

Optional stricter formula:

```text
core_axis_coverage(dataset) =
    count(measured core medical axes for dataset) / count(core medical axes)
```

Interpretation:

- A dataset can score high on measured axes but have low coverage.
- A high score with narrow coverage should be described as strong but narrow.
- A broad medical benchmark should report both performance and coverage.

## 4. Recommended Manuscript Claim Hierarchy

Use this hierarchy to avoid overclaiming:

| Claim Level | Defensible Claim | Current Role |
|---|---|---|
| Literature basis | Prior synthetic medical dataset papers used heterogeneous self-evaluation protocols. | Motivation |
| Benchmark design | SDE-Bench abstracts recurring synthetic-data criteria and adds medical-domain axes. | Main method contribution |
| Same-axis evaluation | Available public synthetic medical datasets were evaluated under common SDE-Bench axes. | Main empirical result |
| Applicability coverage | Missing axes and `not_applicable` cases were explicitly reported. | Fairness and transparency guard |
| Original-metric crosswalk | Prior original metrics were represented as benchmark families with required inputs and portability rules. | Supplementary evidence |
| Full cross-application | Every dataset was evaluated under every prior paper's original metric. | Not currently supported |
| Independent reproduction | Every prior original benchmark was rerun from raw data/code. | Not currently supported |

## 5. Recommended Abstract / Introduction Wording

English:

> Existing synthetic medical datasets are usually evaluated using
> dataset-specific protocols, such as downstream generation utility, symptom
> extraction performance, format compatibility, privacy risk, or longitudinal
> realism. These metrics are valuable but difficult to compare directly because
> they depend on different clinical tasks and data schemas. We therefore designed
> SDE-Bench, a medical-domain benchmark that consolidates conventional synthetic
> data criteria and adds clinically relevant axes including groundedness,
> clinical validity, scope breadth, and interoperability. We evaluated available
> public synthetic medical datasets using this shared benchmark and report both
> axis-level performance and applicability coverage.

Korean:

> 기존 합성 의료 데이터셋은 주로 데이터셋별 목적에 맞춘 자기평가
> 프로토콜로 검증되어 왔다. 이러한 지표들은 유용하지만, 임상 과제와
> 데이터 스키마가 서로 달라 직접 비교가 어렵다. 본 연구는 기존 평가
> 축을 체계적으로 분석하고 의료 도메인에서 필요한 groundedness,
> clinical validity, scope breadth, interoperability를 포함한 공통
> 벤치마크인 SDE-Bench를 설계하였다. 이후 공개 합성 의료 데이터셋들을
> 동일한 SDE-Bench 축에서 평가하고, 축별 성능과 적용 가능 범위를 함께
> 보고하였다.

## 6. Reviewer-Safe Interpretation

The final paper should make three separate points:

1. Prior work motivates the benchmark axes.
   - Existing papers show what synthetic medical datasets have historically
     reported.
   - SDE-Bench uses that evidence to define a broader medical benchmark.

2. SDE-Bench is the common comparison layer.
   - Same-axis comparison happens through SDE-Bench axes, not through every
     prior paper's native task.
   - Dataset heterogeneity is handled through explicit applicability reporting.

3. KMUC should be argued by axis strengths, not by a universal scalar.
   - KMUC is strong on broad multi-specialty scope and patient-facing matching
     utility.
   - Other datasets may remain stronger on structured interoperability,
     longitudinal realism, or claims-format compatibility.
   - This supports a nuanced contribution claim rather than an overbroad
     "best dataset" claim.

## 7. Required Next Changes

To align the repository with this logic, update future reports so that:

1. Stage A is labeled `Original Evaluation Protocol Crosswalk`, not the primary
   same-axis benchmark.
2. Stage B is labeled as the `Common SDE-Bench Axis Evaluation`.
3. A coverage table is added for measured axes, skipped axes, and not-applicable
   axes.
4. `overall_score` is never used as the primary superiority claim.
5. Manuscript wording distinguishes:
   - native-protocol evidence
   - common-axis SDE-Bench evaluation
   - full cross-application equivalence
   - independent reproduction
