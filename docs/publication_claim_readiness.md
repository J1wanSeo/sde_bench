# Publication Claim Readiness

This document defines the minimum evidence needed before SDE-Bench can be
described in a JMIR-style manuscript as comparable to the self-evaluation
benchmarks used by prior synthetic medical dataset papers.

## 1. Claim Ladder

| Level | Claim | Required Evidence |
|---|---|---|
| L0 | Exploratory metric prototype | Axis formulas and runnable code exist. |
| L1 | Executable SDE-Bench profile | JSON/JSONL/CSV inputs run through documented axes with skipped metrics reported. |
| L2 | Original-metric crosswalk | Prior-paper benchmark families list formula, required inputs, portability, and applicability state. |
| L3 | Paper-equivalent benchmark evidence | A cell is `computed` from the same required inputs or `paper_reported` from the original study. |
| L4 | Full paper-equivalent benchmark matrix | Every intended comparison cell is L3, with no `requires_adapter`, `requires_labels`, or `sde_proxy` cells used as original-paper evidence. |

The current repository is at **L2 with selected L3 cells**. It is not yet L4.

## 2. Status Semantics

| Status | Counts as paper-equivalent evidence? | Meaning |
|---|---:|---|
| `computed` | yes | SDE-Bench recomputed the original metric from required inputs. |
| `paper_reported` | yes | The original paper's reported result is preserved as baseline evidence. |
| `sde_proxy` | no | SDE-Bench computed a compatible proxy, not the paper's original metric. |
| `requires_adapter` | no | The metric may be possible but needs an executable adapter. |
| `requires_labels` | no | The metric may be possible but needs additional labels or span annotations. |
| `not_applicable` | no | The dataset does not expose the required task or field type. |

`sde_proxy` must never be merged with `computed` or `paper_reported` in the
paper-equivalent evidence count.

## 3. Conservative Manuscript Claim

Safe current wording:

> SDE-Bench provides an executable axis-level profile and an original-metric
> crosswalk for heterogeneous synthetic medical datasets. It reaches
> paper-equivalent evidence for cells where the original metric is recomputed or
> faithfully paper-reported, while remaining adapter, label, and proxy cells
> define the validation work still needed for a full paper-equivalent benchmark
> matrix.

Unsafe current wording:

> SDE-Bench has already evaluated every prior dataset at the same level as each
> dataset's original paper benchmark.

That wording requires L4 evidence and is not supported while any intended
comparison remains `requires_adapter`, `requires_labels`, or `sde_proxy`.

## 4. Practical Acceptance Gate

Before a manuscript claims full equivalence, the generated cross-benchmark
report must satisfy all gates:

1. Every benchmark family has a formula, required inputs, and applicability rule.
2. At least one target dataset has a `computed` original-metric result.
3. Prior baselines are preserved as `paper_reported` where recomputation is not
   possible.
4. `sde_proxy` cells are reported separately and excluded from paper-equivalent
   evidence.
5. No intended comparison cell remains `requires_adapter` or `requires_labels`.
6. The manuscript reports skipped axes and does not use `overall_score` as the
   primary superiority claim.

The `publication_readiness` section in `cross_benchmark_matrix.json` implements
this gate.
