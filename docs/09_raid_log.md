# 09 · RAID Log (extract)

## Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R1 | NAV data quality is worse than expected (duplicate vendors, uncleared suspense) and delays migration sign-off | High | High | Data quality rules DQ1–DQ5 run from TM1. Cleansing owners named per object. | Fin. Controller | Open |
| R2 | The PAS vendor cannot deliver the billing extract in time | Medium | High | Agree the file spec early. Fallback is a daily CSV export using an existing PAS report. | PAS Product Owner | Open |
| R3 | BC API throttling (HTTP 429) during large claims batches | Medium | Medium | Retry with backoff (NFR-05). Batch size limited. Runs scheduled off-peak. | IT Integration Lead | Mitigated |
| R4 | Finance users are not ready at go-live | Medium | High | Change champions, role-based training, sandbox practice 3 weeks before go-live | Change Lead | Open |
| R5 | Claim data sent to BC includes sensitive medical information | Low | High | Field-level mapping excludes medical data (NFR-08). DPIA reviewed by InfoSec. | BA / InfoSec | Closed |

## Assumptions

| ID | Assumption | Validated? |
|---|---|---|
| A1 | Standard BC API v2.0 covers all integration needs in phase 1 | Yes, confirmed in design |
| A2 | Go-live at year-end is acceptable to the business | Yes, sponsor confirmed |
| A3 | The bank can provide a daily machine-readable statement | Yes |

## Issues

| ID | Issue | Impact | Action | Owner | Status |
|---|---|---|---|---|---|
| I1 | TM1 open AR total differed from the NAV control account by 1,240.00 | Migration sign-off blocked | Traced to 3 unapplied credit memos in NAV. Applied before TM2. | AR Lead | Closed |
| I2 | Broker codes in the PAS do not match NAV customer numbers | INT-01 rejects broker invoices | Mapping table added. Long-term fix is to align codes in the PAS. | BA | Closed |

## Dependencies

| ID | Dependency | On | Needed by |
|---|---|---|---|
| D1 | Entra ID app registrations created and consented | IT Security | Start of integration build |
| D2 | Authority limits confirmed by the Finance Director | Finance | Approval workflow configuration |
| D3 | Bank statement format confirmed | Treasury / Bank | INT-03 build |
