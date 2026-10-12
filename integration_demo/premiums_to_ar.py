"""INT-01 · Policy Admin System -> Business Central premium invoices / credit memos.

Implements docs/05_integration_specification.md (INT-01):
  - bill to broker or policyholder (FR-AR-03)
  - net premium and IPT on separate G/L lines (FR-AR-04, BR-01)
  - External Doc No. = {policy}-{txn} for traceability and duplicate check (FR-AR-02, FR-AR-05)
  - negative billing events (mid-term returns) become credit memos (US-01)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import config


@dataclass
class BillingResult:
    invoices: list[dict] = field(default_factory=list)
    credit_memos: list[dict] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    exceptions: list[dict] = field(default_factory=list)

    def summary(self) -> str:
        gross = sum(d["totalAmountIncludingTax"] for d in self.invoices)
        return (
            f"{len(self.invoices)} invoices (gross {gross:,.2f}), {len(self.credit_memos)} credit memos, "
            f"{len(self.duplicates)} duplicates skipped, {len(self.exceptions)} exceptions"
        )


def bill_to(row: dict) -> str:
    if row["bill_to_type"].strip().upper() == "BROKER":
        return row["broker_code"].strip()
    return row["policyholder_id"].strip()


def build_lines(row: dict) -> list[dict]:
    product = row["product"].strip().upper()
    dims = {"PRODUCT": product, "CHANNEL": row["channel"].strip().upper()}
    net = abs(round(float(row["net_premium"]), 2))
    ipt = abs(round(float(row["ipt_amount"]), 2))
    lines = [{
        "lineType": "Account",
        "lineObjectNumber": config.GL_PREMIUM_INCOME,
        "description": f"Premium {row['policy_number']} ({product.title()})",
        "quantity": 1,
        "unitPrice": net,
        "dimensions": dict(dims),
    }]
    if ipt:
        lines.append({
            "lineType": "Account",
            "lineObjectNumber": config.GL_IPT_PAYABLE,
            "description": f"Insurance Premium Tax {row['policy_number']}",
            "quantity": 1,
            "unitPrice": ipt,
            "dimensions": dict(dims),
        })
    return lines


def run(rows: list[dict], bc) -> BillingResult:
    result = BillingResult()
    for row in rows:
        ext = f"{row['policy_number'].strip()}-{row['billing_txn_id'].strip()}"
        product = row.get("product", "").strip().upper()
        channel = row.get("channel", "").strip().upper()
        if product not in config.VALID_PRODUCTS or channel not in config.VALID_CHANNELS:
            result.exceptions.append({"externalDocumentNumber": ext, "reason": "Invalid product or channel"})
            continue

        customer = bill_to(row)
        if not bc.customer_exists(customer):
            result.exceptions.append({"externalDocumentNumber": ext, "reason": f"Unknown customer {customer}"})
            continue

        sign = -1 if float(row["net_premium"]) < 0 else 1
        entity = "salesCreditMemos" if sign < 0 else "salesInvoices"
        if bc.exists(entity, ext):
            result.duplicates.append(ext)
            continue

        header = {
            "customerNumber": customer,
            "postingDate": row["billing_date"],
            "externalDocumentNumber": ext,
        }
        header["invoiceDate" if sign > 0 else "creditMemoDate"] = row["billing_date"]
        if row.get("currency", "GBP").strip().upper() != "GBP":
            header["currencyCode"] = row["currency"].strip().upper()

        doc = bc.create_sales_document(entity, header, build_lines(row))
        (result.invoices if sign > 0 else result.credit_memos).append(doc)
    return result
