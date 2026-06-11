from __future__ import annotations

from typing import Any

Report = dict[str, Any]


def evaluate_kmuc_matching_original(summary: Report, *, source_report: str | None = None) -> Report:
    """Evaluate the KMUC original department-retrieval benchmark protocol."""
    per_case = summary.get("per_case") if isinstance(summary.get("per_case"), list) else []
    top_k = int(summary.get("top_k") or _infer_top_k(per_case) or 5)
    metrics: Report = {}
    provenance: dict[str, str] = {}

    if per_case:
        dept_metrics = _department_retrieval_metrics(per_case, top_k=top_k)
        metrics.update(dept_metrics)
        provenance.update({key: "recomputed_from_per_case_top_depts" for key in dept_metrics})

    for key in ("dept_top1", f"dept_hit@{top_k}", "mrr_dept"):
        value = summary.get(key)
        if isinstance(value, int | float) and not isinstance(value, bool):
            metrics[key] = value
            provenance[key] = "reported_by_input_summary"

    for key in ("proc_coverage@5", "proc_coverage_n", "icd_coverage@5", "icd_coverage_n"):
        value = summary.get(key)
        if isinstance(value, int | float) and not isinstance(value, bool):
            metrics[key] = value
            provenance[key] = "reported_by_input_summary"

    missing = [
        key
        for key in ("dept_top1", f"dept_hit@{top_k}", "mrr_dept", "proc_coverage@5", "icd_coverage@5")
        if key not in metrics
    ]
    report: Report = {
        "schema_version": "0.1.0",
        "benchmark_family": "kmuc_matching",
        "status": "computed" if metrics else "insufficient_inputs",
        "run_tag": summary.get("run_tag", ""),
        "model": summary.get("model", ""),
        "cases": summary.get("cases"),
        "doctors": summary.get("doctors"),
        "top_k": top_k,
        "records": len(per_case),
        "metrics": metrics,
        "metric_provenance": provenance,
        "skipped_metrics": missing,
    }
    if source_report:
        report["source_report"] = source_report
    return report


def markdown_original_metric_report(report: Report) -> str:
    lines = [
        f"# Original Metric Report: {report['benchmark_family']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Run tag: `{report.get('run_tag', '')}`",
        f"- Model: `{report.get('model', '')}`",
        f"- Cases: `{report.get('cases', 'n/a')}`",
        f"- Records: `{report.get('records', 0)}`",
        f"- Top-k: `{report.get('top_k', 'n/a')}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Provenance |",
        "|---|---:|---|",
    ]
    for key, value in report.get("metrics", {}).items():
        lines.append(f"| `{key}` | `{_fmt(value)}` | {report.get('metric_provenance', {}).get(key, '')} |")
    if report.get("skipped_metrics"):
        lines.extend(["", "## Skipped Metrics", ""])
        lines.extend(f"- `{metric}`" for metric in report["skipped_metrics"])
    lines.append("")
    return "\n".join(lines)


def format_original_metric_value(report: Report) -> str:
    metrics = report.get("metrics", {})
    ordered = ["dept_top1", _dept_hit_key(report), "mrr_dept", "proc_coverage@5", "icd_coverage@5"]
    parts = [f"`{key}={float(metrics[key]):.4f}`" for key in ordered if isinstance(metrics.get(key), int | float)]
    return ", ".join(parts) if parts else "n/a"


def _department_retrieval_metrics(rows: list[Report], *, top_k: int) -> Report:
    applicable = [row for row in rows if row.get("expected_dept") and _ranked_depts(row)]
    if not applicable:
        return {}

    top1 = 0
    hit = 0
    reciprocal_ranks = []
    for row in applicable:
        expected = str(row["expected_dept"])
        ranked = _ranked_depts(row)[:top_k]
        top1 += int(bool(ranked) and ranked[0] == expected)
        if expected in ranked:
            hit += 1
            reciprocal_ranks.append(1 / (ranked.index(expected) + 1))
        else:
            reciprocal_ranks.append(0)
    n = len(applicable)
    return {
        "dept_top1": top1 / n,
        f"dept_hit@{top_k}": hit / n,
        "mrr_dept": sum(reciprocal_ranks) / n,
    }


def _ranked_depts(row: Report) -> list[str]:
    value = row.get("top_depts")
    if isinstance(value, list):
        return _unique_preserve_order(str(item) for item in value if item not in (None, ""))
    value = row.get("predicted_dept")
    if value not in (None, ""):
        return [str(value)]
    return []


def _unique_preserve_order(values) -> list[str]:
    seen = set()
    out = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _infer_top_k(rows: list[Report]) -> int:
    widths = [len(_ranked_depts(row)) for row in rows if _ranked_depts(row)]
    return max(widths) if widths else 0


def _dept_hit_key(report: Report) -> str:
    metrics = report.get("metrics", {})
    if isinstance(metrics, dict):
        for key in sorted(metrics):
            if str(key).startswith("dept_hit@"):
                return str(key)
    return f"dept_hit@{int(report.get('top_k') or 5)}"


def _fmt(value: Any) -> str:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return f"{float(value):.4f}"
    return str(value)
