"""Generate synthetic source files for the demo (fixed seed, so output is repeatable).

Writes to this folder:
  customers.csv        brokers + policyholders that exist in BC
  billing_events.csv   PAS billing extract (INT-01) - includes deliberate errors and duplicates
  approved_claims.csv  Claims Platform extract (INT-02) - includes deliberate errors and a medical-notes
                       column that must NOT reach Business Central
  bank_statement.csv   Bank statement (INT-03) for the same period

All data is synthetic. No real people, policies or claims.
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
rng = random.Random(2026)
START = date(2026, 1, 5)
DAYS = 10

BROKERS = [f"BRK-{i:03d}" for i in range(1, 21)]
HOLDERS = [f"PH-{i:05d}" for i in range(1, 401)]


def d(offset: int) -> str:
    return (START + timedelta(days=offset)).isoformat()


def write(name: str, rows: list[dict]) -> None:
    with open(HERE / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- customers
customers = [{"number": b, "name": f"Broker {b[-3:]} (synthetic)", "type": "BROKER"} for b in BROKERS]
customers += [{"number": h, "name": f"Policyholder {h[-5:]}", "type": "POLICYHOLDER"} for h in HOLDERS]

# ---------------------------------------------------------------- billing events (INT-01)
billing = []
for i in range(1, 241):
    product = rng.choice(["TRAVEL", "TRAVEL", "PMI"])
    channel = rng.choice(["DIRECT", "DIRECT", "BROKER", "AFFINITY"])
    via_broker = channel == "BROKER"
    net = round(rng.uniform(25, 120) if product == "TRAVEL" else rng.uniform(300, 2400), 2)
    billing.append({
        "billing_txn_id": f"T{i:04d}",
        "policy_number": f"POL-{(1000 + i)}",
        "transaction_type": "NEW_BUSINESS" if rng.random() < 0.7 else "RENEWAL",
        "billing_date": d(rng.randrange(DAYS)),
        "product": product,
        "channel": channel,
        "bill_to_type": "BROKER" if via_broker else "POLICYHOLDER",
        "broker_code": rng.choice(BROKERS) if via_broker else "",
        "policyholder_id": rng.choice(HOLDERS),
        "currency": "GBP",
        "net_premium": f"{net:.2f}",
        "ipt_amount": f"{round(net * 0.12, 2):.2f}",  # UK standard IPT rate 12%
    })
# mid-term returns -> credit memos
for i, src in enumerate(rng.sample(billing, 5), start=1):
    billing.append({**src, "billing_txn_id": f"R{i:04d}", "transaction_type": "MTA_RETURN",
                    "net_premium": f"{-round(float(src['net_premium']) * 0.3, 2):.2f}",
                    "ipt_amount": f"{-round(float(src['net_premium']) * 0.3 * 0.12, 2):.2f}"})
# deliberate problems
billing.append({**billing[3], "billing_txn_id": "T9001", "channel": "BROKER", "bill_to_type": "BROKER",
                "broker_code": "BRK-099"})                       # unknown broker
billing += [dict(billing[10]), dict(billing[20]), dict(billing[30])]  # re-sent events (duplicates)

# ---------------------------------------------------------------- claims (INT-02)
claims = []
for i in range(1, 181):
    product = rng.choice(["TRAVEL", "TRAVEL", "PMI"])
    amount = rng.lognormvariate(6.3, 1.0) if product == "TRAVEL" else rng.lognormvariate(7.4, 0.9)
    claims.append({
        "claim_number": f"CLM-{20000 + i}",
        "payment_seq": "1",
        "approved_date": d(rng.randrange(DAYS)),
        "amount_paid": f"{min(round(amount, 2), 48000):.2f}",
        "product": product,
        "channel": rng.choice(["DIRECT", "BROKER", "AFFINITY"]),
        "payee_type": rng.choice(["POLICYHOLDER", "PROVIDER"]),
        "diagnosis_code": rng.choice(["S82.6", "J18.9", "K35.8", "T78.4"]),  # sensitive - must not reach BC
        "treatment_notes": "synthetic note",
    })
for amt in ("12500.00", "18750.00", "26400.00"):                 # guaranteed large payments (approval)
    claims[rng.randrange(len(claims))]["amount_paid"] = amt
claims[50]["approved_date"] = claims[51]["approved_date"]        # two claims, same amount, same day
claims[50]["amount_paid"] = claims[51]["amount_paid"]
claims.append({**claims[0], "claim_number": "CLM-29001", "amount_paid": ""})          # V01
claims.append({**claims[1], "claim_number": "CLM-29002", "amount_paid": "-150.00"})   # V02
claims.append({**claims[2], "claim_number": "CLM-29003", "product": "PET"})           # V03
claims.append({**claims[3], "claim_number": "CLM-29004", "approved_date": "2026-13-01"})  # V01 bad date
claims.append(dict(claims[5]))                                    # duplicate (V04)

# ---------------------------------------------------------------- bank statement (INT-03)
statement = []
for c in claims[:180]:
    shift = 1
    narrative = f"FASTER PAYMENT {c['claim_number']} ASHGROVE CLAIMS"
    r = rng.random()
    if c in (claims[50], claims[51]):
        narrative = "FASTER PAYMENT ASHGROVE CLAIMS"               # no ref -> ambiguous
    elif r < 0.12:
        narrative, shift = "BACS ASHGROVE CLAIMS BATCH", rng.choice([1, 2])  # no ref, inside window
    elif r < 0.15:
        narrative, shift = "BACS ASHGROVE CLAIMS BATCH", 5        # no ref, outside window
    elif r < 0.20:
        continue                                                   # not cleared yet
    statement.append({"date": (date.fromisoformat(c["approved_date"]) + timedelta(days=shift)).isoformat(),
                      "amount": f"{-float(c['amount_paid']):.2f}", "narrative": narrative})

seen = set()
for b in billing[:240]:                                            # premium receipts for ~60% of invoices
    key = (b["policy_number"], b["billing_txn_id"])
    if key in seen or rng.random() > 0.6:
        continue
    seen.add(key)
    gross = round(float(b["net_premium"]) + float(b["ipt_amount"]), 2)
    statement.append({"date": (date.fromisoformat(b["billing_date"]) + timedelta(days=rng.randint(0, 2))).isoformat(),
                      "amount": f"{gross:.2f}",
                      "narrative": f"RECEIPT {b['policy_number']}-{b['billing_txn_id']}"})

statement += [
    {"date": d(4), "amount": "-35.00", "narrative": "ACCOUNT FEE"},
    {"date": d(7), "amount": "-12.50", "narrative": "CHAPS CHARGE"},
]
statement.sort(key=lambda r: r["date"])
for i, row in enumerate(statement, start=1):
    row["line_id"] = f"BS{i:05d}"
statement = [{"line_id": r["line_id"], "date": r["date"], "amount": r["amount"], "narrative": r["narrative"]}
             for r in statement]

write("customers.csv", customers)
write("billing_events.csv", billing)
write("approved_claims.csv", claims)
write("bank_statement.csv", statement)
print(f"customers {len(customers)}, billing events {len(billing)}, claims {len(claims)}, "
      f"statement lines {len(statement)}")
