from __future__ import annotations

from typing import Any

Record = dict[str, Any]


def export_amlsim_records(rows: list[Record], *, split_fraction: float = 0.5, limit: int | None = None) -> dict[str, list[Record]]:
    """Convert IBM AMLSim transaction rows into SDE-Bench records.

    AMLSim is a fully synthetic finance dataset, so this adapter follows the
    same internal split convention used for other public synthetic-only data.
    The first partition is the reference distribution and the second partition
    is the synthetic set being evaluated.
    """
    selected = rows[:limit] if limit else rows
    if not selected:
        return {"reference": [], "source": [], "synthetic": []}
    split_at = max(1, min(len(selected) - 1, int(len(selected) * split_fraction)))
    reference_rows = [_row(row) for row in selected[:split_at]]
    synthetic_rows = [_row(row, source_id=_source_id(row)) for row in selected[split_at:]]
    source_rows = [_row(row, source_id=_source_id(row)) for row in selected[split_at:]]
    return {"reference": reference_rows, "source": source_rows, "synthetic": synthetic_rows}


def _row(row: Record, *, source_id: str | None = None) -> Record:
    transaction_id = _text(row, "TXN_ID", "txn_id", "transaction_id")
    transaction_type = _text(row, "TXN_SOURCE_TYPE_CODE", "transaction_type", "type")
    out: Record = {
        "case_id": f"AMLSIM-TXN-{transaction_id}",
        "account_id": _text(row, "ACCOUNT_ID", "account_id"),
        "counterparty_account_id": _text(row, "COUNTER_PARTY_ACCOUNT_NUM", "counterparty_account_id"),
        "transaction_type": transaction_type,
        "tx_count": _number(row.get("tx_count")),
        "amount": _number(row.get("TXN_AMOUNT_ORIG", row.get("amount", ""))),
        "start_step": _number(row.get("start")),
        "end_step": _number(row.get("end")),
        "expected_transaction_type": transaction_type,
    }
    if source_id:
        out["source_id"] = source_id
    return out


def _source_id(row: Record) -> str:
    return f"AMLSIM-TXN-{_text(row, 'TXN_ID', 'txn_id', 'transaction_id')}"


def _text(row: Record, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def _number(value: Any) -> int | float | str:
    if value in (None, ""):
        return ""
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return str(value)
    if as_float.is_integer():
        return int(as_float)
    return as_float
