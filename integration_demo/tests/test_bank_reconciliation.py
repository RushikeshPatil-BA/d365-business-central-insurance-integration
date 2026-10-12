"""UAT-12 to UAT-15 for INT-03 (bank matching)."""
from bank_reconciliation import reconcile


def line(line_id, dt, amount, narrative):
    return {"line_id": line_id, "date": dt, "amount": str(amount), "narrative": narrative}


def entry(entry_id, dt, amount, reference):
    return {"entry_id": entry_id, "posting_date": dt, "amount": amount, "reference": reference}


def test_uat12_reference_match_rule1():
    r = reconcile([line("L1", "2026-01-11", -1250.00, "FASTER PAYMENT CLM-20431")],
                  [entry("E1", "2026-01-10", -1250.00, "CLM-20431/1")])
    assert r.matches == [{"line_id": "L1", "entry_id": "E1", "rule": 1}]


def test_uat13_date_window_match_rule2():
    r = reconcile([line("L1", "2026-01-12", -300.00, "BACS BATCH")],
                  [entry("E1", "2026-01-10", -300.00, "CLM-1/1")])
    assert r.matches[0]["rule"] == 2


def test_uat14_ambiguous_goes_to_exceptions():
    r = reconcile([line("L1", "2026-01-11", -300.00, "BACS BATCH")],
                  [entry("E1", "2026-01-10", -300.00, "CLM-1/1"), entry("E2", "2026-01-10", -300.00, "CLM-2/1")])
    assert not r.matches
    assert r.exceptions[0]["reason"] == "Multiple candidates"


def test_uat15_outside_window_not_matched():
    r = reconcile([line("L1", "2026-01-15", -300.00, "BACS BATCH")],
                  [entry("E1", "2026-01-10", -300.00, "CLM-1/1")])
    assert r.exceptions[0]["reason"] == "No matching BC entry"
    assert r.unmatched_bc[0]["entry_id"] == "E1"


def test_entry_matched_only_once():
    r = reconcile([line("L1", "2026-01-11", -50.00, "CLM-7"), line("L2", "2026-01-11", -50.00, "CLM-7")],
                  [entry("E1", "2026-01-10", -50.00, "CLM-7/1")])
    assert len(r.matches) == 1 and len(r.exceptions) == 1


def test_receipt_matches_policy_reference():
    r = reconcile([line("L1", "2026-01-11", 560.00, "RECEIPT POL-1001-T55")],
                  [entry("E1", "2026-01-10", 560.00, "POL-1001-T55")])
    assert r.matches[0]["rule"] == 1
