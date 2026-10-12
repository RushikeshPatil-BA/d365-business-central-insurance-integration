"""UAT-01 to UAT-05 for INT-01 (premium billing)."""
import premiums_to_ar
from bc_client import MockBusinessCentral


def event(**overrides):
    row = {"billing_txn_id": "T55", "policy_number": "POL-1001", "billing_date": "2026-01-10",
           "product": "TRAVEL", "channel": "DIRECT", "bill_to_type": "POLICYHOLDER",
           "broker_code": "", "policyholder_id": "PH-00001", "currency": "GBP",
           "net_premium": "500.00", "ipt_amount": "60.00"}
    row.update(overrides)
    return row


def bc():
    return MockBusinessCentral(customers={"PH-00001", "BRK-014"})


def test_uat01_invoice_created_with_traceable_reference():
    mock = bc()
    premiums_to_ar.run([event()], mock)
    inv = mock.sales_invoices[0]
    assert inv["externalDocumentNumber"] == "POL-1001-T55"
    assert inv["lines"][0]["dimensions"]["PRODUCT"] == "TRAVEL"


def test_uat02_broker_policy_billed_to_broker():
    mock = bc()
    premiums_to_ar.run([event(channel="BROKER", bill_to_type="BROKER", broker_code="BRK-014")], mock)
    assert mock.sales_invoices[0]["customerNumber"] == "BRK-014"


def test_uat03_unknown_broker_rejected():
    result = premiums_to_ar.run([event(channel="BROKER", bill_to_type="BROKER", broker_code="BRK-099")], bc())
    assert result.exceptions[0]["reason"] == "Unknown customer BRK-099"
    assert not result.invoices


def test_uat04_ipt_on_separate_account():
    mock = bc()
    premiums_to_ar.run([event()], mock)
    lines = {l["lineObjectNumber"]: l["unitPrice"] for l in mock.sales_invoices[0]["lines"]}
    assert lines == {"4000": 500.00, "2310": 60.00}
    assert mock.sales_invoices[0]["totalAmountIncludingTax"] == 560.00


def test_uat05_duplicate_event_not_invoiced_twice():
    mock = bc()
    premiums_to_ar.run([event()], mock)
    result = premiums_to_ar.run([event()], mock)
    assert len(mock.sales_invoices) == 1
    assert result.duplicates == ["POL-1001-T55"]


def test_mid_term_return_creates_credit_memo():
    mock = bc()
    result = premiums_to_ar.run([event(billing_txn_id="R1", net_premium="-150.00", ipt_amount="-18.00")], mock)
    assert len(result.credit_memos) == 1 and not result.invoices
    assert mock.sales_credit_memos[0]["totalAmountIncludingTax"] == 168.00
