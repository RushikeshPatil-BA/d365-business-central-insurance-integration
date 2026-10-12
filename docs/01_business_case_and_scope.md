# 01 · Business Case & Scope

> **Fictional scenario.** Ashgrove Mutual Insurance Ltd is an invented company. All names, figures and data in this repository are illustrative and were created for this portfolio.

## Company context

| | |
|---|---|
| **Organisation** | Ashgrove Mutual Insurance Ltd (fictional), a UK insurer writing travel and private medical insurance |
| **Size** | ~350 staff, 2 legal entities (UK insurer + Ireland branch), GBP and EUR |
| **Current finance system** | Microsoft Dynamics NAV 2016, on-premises, with heavy customisation |
| **Surrounding systems** | Policy Administration System (PAS), Claims Management Platform, bank (daily statement files), Excel-based management reporting |

## Problem statement

Finance runs on an out-of-support NAV 2016 instance. Premium and claims data reach the ledger through **manual CSV uploads and re-keying**. The result:

- **Month-end close takes 9 working days.** Most of the effort goes on reconciling PAS and claims totals against the GL.
- **Claims payments are re-keyed** from the claims platform into NAV payment journals. That is a control weakness, because the same person can enter and approve a payment.
- **Bank reconciliation is done in Excel**, outside the system, with no audit trail.
- **No real-time view** of premium income, claims paid or cash position for management.
- **Upgrade risk:** the NAV customisations block upgrades, and the infrastructure is reaching end of life.

## Objectives

| # | Objective | Measure of success |
|---|---|---|
| O1 | Replace NAV 2016 with Dynamics 365 Business Central (SaaS) | Go-live with no critical defects open |
| O2 | Automate premium billing from PAS into BC Accounts Receivable | Zero manual premium invoice entry |
| O3 | Automate claims payment postings from the Claims Platform into BC | Zero re-keying, with maker-checker enforced in BC |
| O4 | Bring bank reconciliation into BC with automatic matching | Most bank lines auto-matched; exceptions worked in BC |
| O5 | Provide finance reporting from BC into Power BI | Daily refresh of the premium, claims and cash dashboards |
| O6 | Shorten month-end close | Target agreed with the Finance Director at project start |

> Targets are set as *measures* rather than invented percentages. On a real engagement, baselines would be measured during discovery and agreed with the business.

## Scope

**In scope**
- Business Central SaaS: General Ledger, Dimensions, Accounts Receivable, Accounts Payable, Cash Management / Bank Reconciliation
- Data migration from NAV 2016: chart of accounts, dimensions, customers, vendors, open AR/AP items, GL opening balances
- Integrations:
  - **INT-01** PAS → BC: premium invoices (sales invoices)
  - **INT-02** Claims Platform → BC: approved claim payments (general journal)
  - **INT-03** Bank → BC: daily statement import for reconciliation
  - **INT-04** BC → Power BI: finance reporting
- Roles, permission sets and approval workflows (maker-checker)
- UAT, training and cutover

**Out of scope**
- Replacing the PAS or the Claims Platform
- Reinsurance accounting and IFRS 17 actuarial calculations (actuarial journals are imported as summarised GL journals only)
- Payroll (stays with the external provider; a monthly summary journal is posted)
- Fixed assets (phase 2)

## Approach

- **Hybrid delivery:** Waterfall stage gates for migration and cutover, and Agile sprints (2 weeks) for integration build and configuration.
- **Phases:** Discovery → Design → Build & Configure → Data Migration (3 trial loads) → SIT → UAT → Cutover → Hypercare (4 weeks)
- **Tooling:** Jira (backlog), Confluence (documentation), BPMN for process maps, Postman for API testing, Power BI for reporting

## Key assumptions

1. The PAS and Claims Platform vendors can expose outbound data as files or API calls. No change to their core products is needed.
2. BC SaaS is provisioned in the UK region, using standard BC API v2.0. No custom APIs are built in phase 1.
3. Go-live is at a financial year-end (1 January) to simplify opening balances.
4. Finance Systems owns BC after hypercare.

## Related documents

[02 Stakeholders & RACI](02_stakeholders_raci.md) · [03 BRD](03_business_requirements.md) · [04 Process Maps](04_process_maps.md) · [05 Integration Spec](05_integration_specification.md) · [06 Data Migration](06_data_migration.md)
