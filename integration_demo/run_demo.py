"""Run the full daily integration cycle against a mock Business Central.

    python integration_demo/run_demo.py

1. INT-01  PAS billing events      -> sales invoices / credit memos
2. INT-02  approved claims         -> CLAIMS-PAY journal lines (with approval flags)
3. Re-run INT-02 to prove idempotency (0 new lines)
4. INT-03  bank statement          -> auto-matching against BC entries

Exception and approval reports are written to integration_demo/output/.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import bank_reconciliation  # noqa: E402
import claims_to_gl  # noqa: E402
import premiums_to_ar  # noqa: E402
from bc_client import MockBusinessCentral  # noqa: E402

DATA = HERE / "sample_data"
OUT = HERE / "output"


def read(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        if not rows:
            f.write("no rows\n")
            return
        fields = [k for k in rows[0].keys() if k != "dimensions"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def bc_bank_entries(bc: MockBusinessCentral) -> list[dict]:
    """Entries BC expects to see on the bank statement (bank's sign convention)."""
    entries = [{"entry_id": l["id"], "posting_date": l["postingDate"], "amount": -l["amount"],
                "reference": l["externalDocumentNumber"]} for l in bc.journal_lines]
    entries += [{"entry_id": i["id"], "posting_date": i["postingDate"], "amount": i["totalAmountIncludingTax"],
                 "reference": i["externalDocumentNumber"]} for i in bc.sales_invoices]
    return entries


def main() -> None:
    bc = MockBusinessCentral(customers={c["number"] for c in read("customers.csv")})

    print("INT-01  Premium billing  ->", end=" ")
    billing = premiums_to_ar.run(read("billing_events.csv"), bc)
    print(billing.summary())

    claims_rows = read("approved_claims.csv")
    print("INT-02  Claims payments  ->", end=" ")
    claims = claims_to_gl.run(claims_rows, bc, batch_id="CLM-20260116")
    print(claims.summary())

    print("INT-02  Re-run same file ->", end=" ")
    rerun = claims_to_gl.run(claims_rows, bc, batch_id="CLM-20260116")
    print(rerun.summary())

    sensitive = {"diagnosis_code", "treatment_notes"}
    assert not any(sensitive & l.keys() for l in bc.journal_lines), "medical data reached BC"
    print("NFR-08  No medical fields sent to Business Central: OK")

    print("INT-03  Bank matching    ->", end=" ")
    recon = bank_reconciliation.reconcile(read("bank_statement.csv"), bc_bank_entries(bc))
    print(recon.summary())

    write("int01_billing_exceptions.csv", billing.exceptions)
    write("int02_claims_exceptions.csv", claims.exceptions)
    write("int02_requires_approval.csv", claims.requires_approval)
    write("int03_bank_exceptions.csv", recon.exceptions)
    write("int03_matches.csv", recon.matches)
    print(f"\nReports written to {OUT.relative_to(HERE.parent)}/")


if __name__ == "__main__":
    main()
