# 06 · Data Migration: NAV 2016 → Business Central

## Strategy

| Decision | Choice | Rationale |
|---|---|---|
| History | **Balances only.** Opening GL balances at cut-off plus **open** AR/AP items. Historical transactions are not migrated. | Keeps the new ledger clean. NAV stays read-only for 7 years for audit lookups. |
| Cut-off | Financial year-end (31 Dec) | Simplifies opening balances, and P&L starts at zero |
| Method | BC Configuration Packages (RapidStart) for master data, and general journals for balances | Standard, repeatable, no custom code |
| Trial loads | 3 trial migrations (TM1, TM2, dress rehearsal) before live | Each one is reconciled and signed off by the Financial Controller |

## Migration objects & mapping

| # | Object | NAV source | BC target | Key transformation | Owner |
|---|---|---|---|---|---|
| M1 | Chart of accounts | G/L Account (T15) | G/L Account | ~420 NAV accounts rationalised. Unused or duplicate accounts are dropped via a mapping table. | Fin. Controller |
| M2 | Dimensions | Dimension / Dimension Value | Dimensions | Old `DEPT` dimension replaced by `PRODUCT` and `CHANNEL`. `ENTITY` added. | Fin. Controller |
| M3 | Customers (brokers) | Customer (T18) | Customer | Only brokers with activity in the last 24 months, or an open balance | AR Lead |
| M4 | Vendors | Vendor (T23) | Vendor | Deduplicated on bank details + name. Inactive vendors excluded. | AP Lead |
| M5 | Open AR items | Cust. Ledger Entry (open) | Sales journal | One line per open invoice, with original doc no. as External Doc No. | AR Lead |
| M6 | Open AP items | Vendor Ledger Entry (open) | Purchase journal | As above | AP Lead |
| M7 | GL opening balances | G/L Entry (balance at cut-off) | General journal | Balance sheet accounts only, by dimension | Fin. Controller |
| M8 | Bank accounts | Bank Account | Bank Account | Statement import format set per account | Treasury |

## Chart of accounts mapping (extract)

| NAV account | NAV name | BC account | BC name | Notes |
|---|---|---|---|---|
| 10100 | Premium Income – Travel | 4000 | Premium Income | Product moves to PRODUCT dimension |
| 10200 | Premium Income – Medical | 4000 | Premium Income | Merged, PRODUCT = PMI |
| 22050 | IPT Control | 2310 | IPT Payable | Renamed |
| 50100 | Claims Paid Travel | 5100 | Claims Paid – Travel | |
| 50200 | Claims Paid Medical | 5200 | Claims Paid – PMI | |
| 50999 | Claims Suspense (old) | – | *not migrated* | Balance must be cleared to zero before cut-off |

## Data quality rules

| Rule | Check | Action if failed |
|---|---|---|
| DQ1 | Customer/vendor has a valid post code and country | Fix in NAV before extract |
| DQ2 | No duplicate vendors on the same bank account | Merge, then keep the oldest active vendor |
| DQ3 | Open item balances = control account balance in GL | Investigate before sign-off |
| DQ4 | Every balance carries the mandatory dimensions | Default dimension mapping applied |
| DQ5 | Suspense / clearing accounts are zero at cut-off | Finance clears them before the final extract |

## Reconciliation & sign-off

For each trial load and for the live load:

1. **Record counts:** NAV extract vs BC import (customers, vendors, open items)
2. **Value totals:** open AR/AP total and GL trial balance by account, NAV vs BC (difference must be 0.00)
3. **Sample checks:** 25 random customers and 25 vendors checked field by field
4. **Sign-off:** the Financial Controller signs the reconciliation pack, and that sign-off is a gate for cutover

## Cutover outline

| Step | When | Owner |
|---|---|---|
| Freeze NAV postings | D-2, 18:00 | Fin. Controller |
| Final extract and transform | D-2 to D-1 | BC Partner |
| Load master data and balances | D-1 | BC Partner |
| Reconciliation and sign-off | D-1, evening | Fin. Controller / BA |
| Switch on integrations INT-01 to INT-04 | D-Day, 06:00 | IT Integration Lead |
| Go / no-go | D-Day, 08:00 | Finance Director |
| Hypercare starts | D-Day | All |

**Rollback:** if go/no-go fails, NAV is reopened and integrations stay pointed at the old CSV process.
