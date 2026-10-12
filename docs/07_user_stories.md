# 07 · User Stories & Acceptance Criteria

Format: *As a … I want … so that …*, with acceptance criteria in Given / When / Then.

---

### US-01 · Automatic premium invoices
**As an** AR clerk **I want** premium invoices created in BC automatically from PAS billing events **so that** I no longer upload monthly summaries by hand.

*Traces to:* FR-AR-01, FR-AR-02 · *Priority:* Must · *Estimate:* 8 pts

- **Given** a new policy is billed in the PAS **when** the nightly integration runs **then** a posted sales invoice exists in BC with External Doc No. = `{policy}-{txn}`.
- **Given** a mid-term reduction in the PAS **when** the integration runs **then** a sales credit memo is created instead of an invoice.

### US-02 · Broker billing
**As a** credit controller **I want** broker-placed policies invoiced to the broker account **so that** I chase the party who actually owes us.

*Traces to:* FR-AR-03 · *Priority:* Must · *Estimate:* 3 pts

- **Given** a billing event with `bill_to_type = BROKER` and broker code `BRK-014` **when** it is loaded **then** the invoice customer is `BRK-014`.
- **Given** the broker code does not exist in BC **then** the record is rejected to the exceptions report with reason "Unknown customer".

### US-03 · IPT posted separately
**As a** Financial Controller **I want** Insurance Premium Tax posted to the IPT liability account **so that** premium income is not overstated and the IPT return is accurate.

*Traces to:* FR-AR-04, BR-01 · *Priority:* Must · *Estimate:* 2 pts

- **Given** net premium 500.00 and IPT 60.00 **when** the invoice is posted **then** 500.00 is credited to 4000 Premium Income, 60.00 to 2310 IPT Payable, and 560.00 debited to debtors.

### US-04 · No duplicate invoices
**As a** Financial Controller **I want** repeated billing events to be ignored **so that** customers are never invoiced twice.

*Traces to:* FR-AR-05, NFR-04 · *Priority:* Must · *Estimate:* 3 pts

- **Given** an invoice already exists for `POL-1001-T55` **when** the same event is sent again **then** no new invoice is created and the event is logged as "duplicate – skipped".

### US-05 · Claims payments without re-keying
**As an** AP & Claims Payments clerk **I want** approved claims to arrive as BC payment journal lines **so that** I stop re-keying from CSV files.

*Traces to:* FR-CP-01, FR-CP-02 · *Priority:* Must · *Estimate:* 8 pts

- **Given** 150 approved claims in today's file **when** INT-02 runs **then** 150 journal lines exist in batch `CLAIMS-PAY`, each with External Doc No. = `{claim}/{seq}` and the correct claims-paid account for its product.

### US-06 · Maker-checker on large payments
**As** Internal Audit **I want** claim payments above the authority limit to need a second approver **so that** no single person can release a large payment.

*Traces to:* FR-CP-03, FR-CP-04, BR-02 · *Priority:* Must · *Estimate:* 5 pts

- **Given** a journal line above the authority limit **when** a user tries to post the batch **then** BC blocks posting until an approver approves it.
- **Given** user A created the batch **when** user A tries to approve it **then** the approval is refused.

### US-07 · Exceptions are visible
**As an** AP & Claims Payments lead **I want** invalid claim records listed with a reason **so that** none are silently missed.

*Traces to:* FR-CP-05 · *Priority:* Must · *Estimate:* 3 pts

- **Given** a claim record with a missing amount **when** INT-02 runs **then** it appears in the exceptions report with code V01 and is not loaded.

### US-08 · Automatic bank matching
**As a** Cash Manager **I want** bank lines matched to BC entries automatically **so that** I only work the exceptions.

*Traces to:* FR-BR-01, FR-BR-02 · *Priority:* Must · *Estimate:* 5 pts

- **Given** a bank line of 1,250.00 with narrative containing `CLM-20431` **and** a BC payment of 1,250.00 with External Doc No. `CLM-20431/1` **then** they are matched by Rule 1.
- **Given** a bank line with no reference **and** exactly one BC entry with the same amount within ±3 days **then** they are matched by Rule 2.
- **Given** two possible BC entries **then** the line goes to exceptions with reason "Multiple candidates".

### US-09 · Finance dashboard
**As a** Finance Director **I want** a daily Power BI view of premium, claims, loss ratio and cash by product and channel **so that** I can spot problems without waiting for month-end.

*Traces to:* FR-RP-01, FR-RP-02 · *Priority:* Must · *Estimate:* 8 pts

- **Given** the scheduled refresh has run **when** I open the dashboard **then** the figures match the BC trial balance for the same date.
