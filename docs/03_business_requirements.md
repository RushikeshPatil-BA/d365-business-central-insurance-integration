# 03 · Business Requirements Document (BRD)

| | |
|---|---|
| **Project** | NAV 2016 → Business Central migration & finance integrations |
| **Version** | 1.0 (portfolio version) |
| **Business owner** | Financial Controller |
| **Prioritisation** | MoSCoW (Must / Should / Could / Won't this release) |

## 1. Functional requirements

### 1.1 General Ledger & Dimensions

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-GL-01 | The system shall hold a single chart of accounts for both legal entities, mapped from NAV with obsolete accounts removed. | Must | Fin. Controller |
| FR-GL-02 | Every posting shall carry the dimensions **PRODUCT** (Travel / PMI), **CHANNEL** (Direct / Broker / Affinity) and **ENTITY** (UK / IE). | Must | Fin. Controller |
| FR-GL-03 | Postings without mandatory dimensions shall be blocked (Default Dimensions, Code Mandatory). | Must | Internal Audit |
| FR-GL-04 | The system shall support GBP as the local currency and EUR transactions, with daily exchange rates. | Must | Treasury |
| FR-GL-05 | Accounting periods shall be closed in BC once month-end is complete, to stop back-posting. | Must | Fin. Controller |

### 1.2 Premium billing (Accounts Receivable), linked to INT-01

| ID | Requirement | Priority |
|---|---|---|
| FR-AR-01 | Each new policy, renewal or mid-term adjustment billed in the PAS shall create a sales invoice (or credit memo) in BC automatically. | Must |
| FR-AR-02 | The PAS policy number shall be stored as the External Document No. on the BC invoice for traceability. | Must |
| FR-AR-03 | Broker policies shall be invoiced to the broker account, not the policyholder. | Must |
| FR-AR-04 | Insurance Premium Tax (IPT) shall be posted to a separate liability account, not to premium income. | Must |
| FR-AR-05 | A duplicate PAS billing event (same policy, same transaction ID) shall be rejected, not invoiced twice. | Must |
| FR-AR-06 | Credit control shall see aged debt by broker and by product in BC. | Should |

### 1.3 Claims payments, linked to INT-02

| ID | Requirement | Priority |
|---|---|---|
| FR-CP-01 | Claims approved for payment in the Claims Platform shall create payment journal lines in BC automatically, with no re-keying. | Must |
| FR-CP-02 | Each line shall reference the claim number (External Document No.) and post to the claims-paid GL account by PRODUCT dimension. | Must |
| FR-CP-03 | Payments above the **authority limit** set by Finance shall require a second approver in BC before posting (maker-checker). | Must |
| FR-CP-04 | The person who imports or creates a payment batch shall not be able to approve it (segregation of duties). | Must |
| FR-CP-05 | Rejected or invalid claim records shall go to an exceptions report and never be silently dropped. | Must |
| FR-CP-06 | Payment files for the bank shall be generated from BC. | Should |

### 1.4 Bank reconciliation, linked to INT-03

| ID | Requirement | Priority |
|---|---|---|
| FR-BR-01 | Daily bank statements shall be imported into BC bank account reconciliation automatically. | Must |
| FR-BR-02 | Lines shall be auto-matched on **amount + reference**, then on **amount + date within ±3 days**. | Must |
| FR-BR-03 | Unmatched lines shall stay in an exceptions queue for Treasury to clear manually, with a reason recorded. | Must |
| FR-BR-04 | Matching rules shall be configurable by Treasury without development. | Could |

### 1.5 Reporting, linked to INT-04

| ID | Requirement | Priority |
|---|---|---|
| FR-RP-01 | Power BI shall report premium written, claims paid, loss ratio (claims ÷ earned premium proxy) and cash, by PRODUCT and CHANNEL. | Must |
| FR-RP-02 | Data shall refresh at least daily. | Must |
| FR-RP-03 | Finance users shall drill from a Power BI figure to the underlying GL entries. | Should |

## 2. Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Security | Integrations shall authenticate with **OAuth 2.0 client credentials** (Microsoft Entra ID app registration). No user credentials are stored in integration code. |
| NFR-02 | Security | Each integration app registration shall have the **minimum BC permission set** it needs. |
| NFR-03 | Auditability | Every integrated record shall be traceable from source system ID → BC document → GL entry. |
| NFR-04 | Reliability | Integrations shall be **idempotent**, so re-running a batch never creates duplicates. |
| NFR-05 | Reliability | Transient API failures (HTTP 429 / 5xx) shall be retried with exponential backoff, up to 5 attempts. |
| NFR-06 | Performance | The daily claims batch (up to ~2,000 lines) shall complete within 30 minutes. |
| NFR-07 | Monitoring | Failed batches shall alert the Finance Systems team within 15 minutes. |
| NFR-08 | Data protection | Claim data sent to BC shall exclude medical details (claim number, payee and amount only), in line with UK GDPR data minimisation. |
| NFR-09 | Availability | Integration windows shall avoid the BC SaaS maintenance window. |

## 3. Business rules

| ID | Rule |
|---|---|
| BR-01 | Premium invoice amount = net premium + IPT. IPT is posted separately (FR-AR-04). |
| BR-02 | Claims payment authority limit: set by Finance and held in configuration, not code. |
| BR-03 | A claim can only be paid once. The claim number + payment sequence is unique. |
| BR-04 | The posting date is the source system's approval or billing date, unless that period is closed, in which case it is the first open day. |
| BR-05 | EUR transactions use the BC exchange rate on the posting date. |

## 4. Sign-off

| Role | Name | Decision |
|---|---|---|
| Financial Controller | (fictional) | Approved |
| IT Integration Lead | (fictional) | Approved |

Traceability to user stories and tests: see [10 Traceability Matrix](10_traceability_matrix.md).
