"""INT-02 · Claims Platform -> Business Central claim payment journal lines.

Implements docs/05_integration_specification.md (INT-02):
  V01 mandatory fields · V02 amount > 0 · V03 known product
  V04 duplicate check (idempotency) · V05 authority limit flag
Medical details in the source file are never sent to BC (NFR-08).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date

import config

MANDATORY = ("claim_number", "payment_seq", "approved_date", "amount_paid", "product")


@dataclass
class BatchResult:
    loaded: list[dict] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    exceptions: list[dict] = field(default_factory=list)

    @property
    def requires_approval(self) -> list[dict]:
        return [l for l in self.loaded if l["status"] == "REQUIRES_APPROVAL"]

    def summary(self) -> str:
        total = sum(l["amount"] for l in self.loaded)
        return (
            f"loaded {len(self.loaded)} lines (total {total:,.2f}), "
            f"{len(self.requires_approval)} need approval, "
            f"{len(self.duplicates)} duplicates skipped, {len(self.exceptions)} exceptions"
        )


def validate(row: dict) -> tuple[str, str] | None:
    """Return (code, reason) if the row fails validation, else None."""
    missing = [f for f in MANDATORY if not (row.get(f) or "").strip()]
    if missing:
        return "V01", f"Missing mandatory field(s): {', '.join(missing)}"
    try:
        amount = float(row["amount_paid"])
    except ValueError:
        return "V01", f"Amount is not numeric: {row['amount_paid']!r}"
    if amount <= 0:
        return "V02", "Amount must be greater than zero"
    if row["product"].strip().upper() not in config.VALID_PRODUCTS:
        return "V03", f"Unknown product: {row['product']}"
    try:
        date.fromisoformat(row["approved_date"])
    except ValueError:
        return "V01", f"Invalid approved_date: {row['approved_date']}"
    return None


def map_to_journal_line(row: dict, batch_id: str) -> dict:
    """Map a validated claims record to a BC journalLine payload (+ dimensions)."""
    product = row["product"].strip().upper()
    amount = round(float(row["amount_paid"]), 2)
    payee = row.get("payee_type", "Policyholder").strip().title()
    return {
        "accountType": "G/L Account",
        "accountNumber": config.GL_CLAIMS_PAID[product],
        "postingDate": row["approved_date"],
        "documentNumber": batch_id,
        "externalDocumentNumber": f"{row['claim_number'].strip()}/{row['payment_seq'].strip()}",
        "amount": amount,
        "description": f"Claim payment - {payee}",
        "dimensions": {"PRODUCT": product, "CHANNEL": row.get("channel", "DIRECT").strip().upper()},
        # nothing from diagnosis / treatment columns is mapped (NFR-08)
    }


def run(rows: list[dict], bc, batch_id: str) -> BatchResult:
    result = BatchResult()
    for row in rows:
        error = validate(row)
        if error:
            code, reason = error
            result.exceptions.append({"claim_number": row.get("claim_number", ""), "code": code, "reason": reason})
            continue

        line = map_to_journal_line(row, batch_id)
        ext = line["externalDocumentNumber"]
        if bc.exists("journalLines", ext):
            result.duplicates.append(ext)
            continue

        status = "REQUIRES_APPROVAL" if line["amount"] >= config.AUTHORITY_LIMIT else "READY"
        bc.create_journal_line(config.CLAIMS_JOURNAL_CODE, dict(line))
        result.loaded.append({**line, "status": status})
    return result


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
