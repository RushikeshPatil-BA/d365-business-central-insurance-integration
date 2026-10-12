# 08 · UAT Test Cases

**Entry criteria:** SIT complete with no open Critical/High defects; UAT environment loaded with TM2 migration data; test users set up with production permission sets.
**Exit criteria:** all Must-have test cases passed; no open Critical/High defects; Medium defects have an agreed workaround; sign-off by the Financial Controller.

| ID | Story | Scenario | Steps | Expected result | Automated in demo |
|---|---|---|---|---|---|
| UAT-01 | US-01 | New policy billed | Bill a new Travel policy in PAS UAT, run INT-01 | Posted sales invoice in BC, External Doc No. `{policy}-{txn}`, PRODUCT = TRAVEL | ✅ `test_premiums_to_ar.py` |
| UAT-02 | US-02 | Broker policy | Bill a broker policy | Invoice customer = broker code | ✅ |
| UAT-03 | US-02 | Unknown broker | Bill with a broker code not in BC | Rejected, reason "Unknown customer" | ✅ |
| UAT-04 | US-03 | IPT split | Bill net 500.00 + IPT 60.00 | Lines: 4000 = 500.00, 2310 = 60.00, total 560.00 | ✅ |
| UAT-05 | US-04 | Duplicate event | Re-send the UAT-01 event | No new invoice. Logged as duplicate. | ✅ |
| UAT-06 | US-05 | Daily claims batch | Approve 20 claims (mixed products), run INT-02 | 20 journal lines, correct accounts 5100 / 5200 | ✅ `test_claims_to_gl.py` |
| UAT-07 | US-07 | Missing amount | Include a claim with a blank amount | Exceptions report, code V01. Not loaded. | ✅ |
| UAT-08 | US-07 | Unknown product | Include a claim with product "PET" | Exceptions report, code V03 | ✅ |
| UAT-09 | US-05 | Re-run batch | Run INT-02 twice for the same day | Second run creates 0 new lines (all duplicates) | ✅ |
| UAT-10 | US-06 | Large payment | Include a claim above the authority limit | Line flagged REQUIRES_APPROVAL. Posting blocked until approved in BC. | ✅ flag · ⬜ BC workflow (manual) |
| UAT-11 | US-06 | Self-approval | Batch creator attempts approval | Approval refused | ⬜ manual in BC |
| UAT-12 | US-08 | Reference match | Import a statement line with a claim ref in the narrative | Matched by Rule 1 | ✅ `test_bank_reconciliation.py` |
| UAT-13 | US-08 | Date-window match | Statement line without a reference, one candidate within ±3 days | Matched by Rule 2 | ✅ |
| UAT-14 | US-08 | Ambiguous match | Two candidates with the same amount and date | Exceptions, "Multiple candidates" | ✅ |
| UAT-15 | US-08 | Outside window | Same amount, 5 days apart | Not matched → exceptions | ✅ |
| UAT-16 | NFR-05 | API throttling | Simulate HTTP 429 from BC | Retried with backoff, then succeeds | ✅ `test_bc_client.py` |
| UAT-17 | US-09 | Dashboard reconciles | Compare Power BI totals to the BC trial balance | Equal for the test date | ⬜ manual |

## Defect severity definitions

| Severity | Definition | Go-live impact |
|---|---|---|
| Critical | Financial misstatement, or a process cannot run | Blocks go-live |
| High | Process runs only with a significant manual workaround | Blocks go-live unless the sponsor accepts it |
| Medium | Workaround available, limited impact | Fix in hypercare |
| Low | Cosmetic | Backlog |
