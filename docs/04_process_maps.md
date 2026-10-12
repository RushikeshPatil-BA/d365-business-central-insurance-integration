# 04 · Process Maps (As-Is → To-Be)

Diagrams are written in Mermaid, so they render directly on GitHub. They use swimlane-style subgraphs to show who does what.

---

## Process A: Claims payment to ledger

### As-Is (NAV 2016)

```mermaid
flowchart LR
  subgraph CLAIMS[Claims Platform]
    A1[Claim approved for payment]
    A2[Export daily CSV of approved claims]
  end
  subgraph AP[AP & Claims Payments team]
    B1[Open CSV in Excel]
    B2[Check totals by hand]
    B3[Re-key lines into NAV payment journal]
    B4[Same person posts journal]
  end
  subgraph BANK[Bank portal]
    C1[Upload payment file manually]
  end
  A1 --> A2 --> B1 --> B2 --> B3 --> B4 --> C1
  B3 -. "Re-keying errors" .-> X1((Risk))
  B4 -. "No maker-checker" .-> X2((Control gap))
```

**Pain points:** manual re-keying, no segregation of duties, no link from GL entry back to claim number, and time-consuming reconciliation at month-end.

### To-Be (Business Central)

```mermaid
flowchart LR
  subgraph CLAIMS[Claims Platform]
    A1[Claim approved for payment]
  end
  subgraph INT[Integration INT-02]
    I1[Extract approved claims]
    I2{Validate:<br/>mandatory fields,<br/>duplicate check}
    I3[Create journal lines via BC API<br/>claim no. = External Doc No.]
    I4[Exceptions report]
  end
  subgraph BC[Business Central]
    D1{Amount above<br/>authority limit?}
    D2[Approval request to second approver]
    D3[Post payment journal]
    D4[Generate bank payment file]
  end
  A1 --> I1 --> I2
  I2 -- valid --> I3 --> D1
  I2 -- invalid --> I4
  D1 -- yes --> D2 --> D3
  D1 -- no --> D3
  D3 --> D4
```

**Benefits:** no re-keying, maker-checker enforced in the system, full traceability from claim → journal → GL, and exceptions visible instead of lost.

---

## Process B: Premium billing to Accounts Receivable

### To-Be

```mermaid
flowchart LR
  subgraph PAS[Policy Admin System]
    P1[Policy bound / renewed / adjusted]
    P2[Billing event raised]
  end
  subgraph INT[Integration INT-01]
    I1{Already invoiced?<br/>policy + transaction ID}
    I2[Map: customer = policyholder or broker,<br/>net premium + IPT lines, dimensions]
    I3[Create & post sales invoice via BC API]
    I4[Skip & log duplicate]
  end
  subgraph BC[Business Central]
    B1[Customer ledger entry]
    B2[GL: premium income, IPT liability, debtors]
    B3[Aged debt by broker / product]
  end
  P1 --> P2 --> I1
  I1 -- no --> I2 --> I3 --> B1 --> B2 --> B3
  I1 -- yes --> I4
```

---

## Process C: Bank reconciliation

### To-Be

```mermaid
flowchart TB
  S1[Bank statement file received daily] --> S2[Import into BC Bank Acc. Reconciliation]
  S2 --> M1{Rule 1:<br/>amount + reference match?}
  M1 -- yes --> OK[Matched]
  M1 -- no --> M2{Rule 2:<br/>amount + date within ±3 days,<br/>single candidate?}
  M2 -- yes --> OK
  M2 -- no / multiple --> EX[Exceptions queue]
  EX --> T1[Treasury investigates]
  T1 --> T2[Manual match with reason, or post adjustment]
  OK --> P[Post reconciliation]
  T2 --> P
```

---

## Gap analysis summary

| Area | As-Is | To-Be | Gap closed by |
|---|---|---|---|
| Claims payments | Re-keyed from CSV | API-created journal lines | INT-02 |
| Payment controls | Single user enters & posts | Approval workflow above limit, SoD | BC approvals + permission sets |
| Premium billing | Monthly summary upload | Invoice per billing event | INT-01 |
| Bank reconciliation | Excel, off-system | In BC with auto-match rules | INT-03 + matching rules |
| Reporting | Excel packs from NAV exports | Power BI on BC data, daily | INT-04 |
