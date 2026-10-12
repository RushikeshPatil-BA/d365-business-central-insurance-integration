# 10 · Requirements Traceability Matrix

| Requirement | Description | User story | Test case(s) | Interface | Demo code |
|---|---|---|---|---|---|
| FR-AR-01 | Auto-create premium invoices | US-01 | UAT-01 | INT-01 | `premiums_to_ar.py` |
| FR-AR-02 | Policy no. as External Doc No. | US-01 | UAT-01 | INT-01 | `premiums_to_ar.py` |
| FR-AR-03 | Broker billing | US-02 | UAT-02, UAT-03 | INT-01 | `premiums_to_ar.py` |
| FR-AR-04 | IPT posted separately | US-03 | UAT-04 | INT-01 | `premiums_to_ar.py` |
| FR-AR-05 | No duplicate invoices | US-04 | UAT-05 | INT-01 | `premiums_to_ar.py` |
| FR-CP-01 | Auto-create claim payment lines | US-05 | UAT-06 | INT-02 | `claims_to_gl.py` |
| FR-CP-02 | Claim no. reference, account by product | US-05 | UAT-06 | INT-02 | `claims_to_gl.py` |
| FR-CP-03 | Approval above authority limit | US-06 | UAT-10 | INT-02 + BC workflow | `claims_to_gl.py` (flag) |
| FR-CP-04 | Segregation of duties | US-06 | UAT-11 | BC permission sets | – (BC config) |
| FR-CP-05 | Exceptions report | US-07 | UAT-07, UAT-08 | INT-02 | `claims_to_gl.py` |
| FR-BR-01 | Statement import | US-08 | UAT-12 | INT-03 | `bank_reconciliation.py` |
| FR-BR-02 | Auto-match rules | US-08 | UAT-12, 13, 14, 15 | INT-03 | `bank_reconciliation.py` |
| FR-BR-03 | Exceptions queue | US-08 | UAT-14, UAT-15 | INT-03 | `bank_reconciliation.py` |
| FR-RP-01 | Finance dashboard | US-09 | UAT-17 | INT-04 | – (Power BI) |
| NFR-04 | Idempotency | US-04 | UAT-05, UAT-09 | All | `bc_client.py` |
| NFR-05 | Retry with backoff | – | UAT-16 | All | `bc_client.py` |
| NFR-08 | Data minimisation | – | Design review | INT-02 | `claims_to_gl.py` |
