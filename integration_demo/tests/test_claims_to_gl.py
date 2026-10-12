"""UAT-06 to UAT-10 for INT-02 (claims payments)."""
import claims_to_gl
import config
from bc_client import MockBusinessCentral


def claim(**overrides):
    row = {"claim_number": "CLM-1", "payment_seq": "1", "approved_date": "2026-01-10",
           "amount_paid": "500.00", "product": "TRAVEL", "channel": "DIRECT",
           "payee_type": "POLICYHOLDER", "diagnosis_code": "J18.9", "treatment_notes": "x"}
    row.update(overrides)
    return row


def test_uat06_lines_created_with_correct_accounts():
    bc = MockBusinessCentral()
    rows = [claim(claim_number="CLM-1", product="TRAVEL"), claim(claim_number="CLM-2", product="PMI")]
    result = claims_to_gl.run(rows, bc, "B1")
    assert [l["accountNumber"] for l in bc.journal_lines] == ["5100", "5200"]
    assert bc.journal_lines[0]["externalDocumentNumber"] == "CLM-1/1"
    assert len(result.loaded) == 2


def test_uat07_missing_amount_goes_to_exceptions():
    result = claims_to_gl.run([claim(amount_paid="")], MockBusinessCentral(), "B1")
    assert result.exceptions[0]["code"] == "V01"
    assert not result.loaded


def test_uat08_unknown_product_rejected():
    result = claims_to_gl.run([claim(product="PET")], MockBusinessCentral(), "B1")
    assert result.exceptions[0]["code"] == "V03"


def test_negative_amount_rejected():
    result = claims_to_gl.run([claim(amount_paid="-10")], MockBusinessCentral(), "B1")
    assert result.exceptions[0]["code"] == "V02"


def test_uat09_rerun_is_idempotent():
    bc = MockBusinessCentral()
    claims_to_gl.run([claim()], bc, "B1")
    second = claims_to_gl.run([claim()], bc, "B1")
    assert len(bc.journal_lines) == 1
    assert second.duplicates == ["CLM-1/1"]


def test_uat10_large_payment_flagged_for_approval():
    result = claims_to_gl.run([claim(amount_paid=str(config.AUTHORITY_LIMIT))], MockBusinessCentral(), "B1")
    assert result.loaded[0]["status"] == "REQUIRES_APPROVAL"


def test_below_limit_is_ready():
    result = claims_to_gl.run([claim(amount_paid="9999.99")], MockBusinessCentral(), "B1")
    assert result.loaded[0]["status"] == "READY"


def test_nfr08_medical_fields_never_sent():
    bc = MockBusinessCentral()
    claims_to_gl.run([claim()], bc, "B1")
    assert "diagnosis_code" not in bc.journal_lines[0]
    assert "treatment_notes" not in bc.journal_lines[0]
