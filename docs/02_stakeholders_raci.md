# 02 · Stakeholders & RACI

## Stakeholder map

| Stakeholder | Role in project | Interest | Influence | Engagement approach |
|---|---|---|---|---|
| Finance Director | Project sponsor | High | High | Fortnightly steering update, stage-gate sign-off |
| Financial Controller | Business owner, GL and close | High | High | Weekly working session, owner of the BRD sign-off |
| AR / Credit Control Lead | Premium billing and collections | High | Medium | Process workshops, UAT lead for AR |
| AP & Claims Payments Lead | Claims payment processing | High | Medium | Process workshops, UAT lead for payments |
| Treasury / Cash Manager | Bank reconciliation | High | Medium | Bank rec workshops, matching-rule sign-off |
| Head of Claims Operations | Claims Platform business owner | Medium | High | Interface agreement for INT-02 |
| PAS Product Owner | Policy Admin System owner | Medium | High | Interface agreement for INT-01 |
| IT Integration Lead | Integration build and support | High | High | Daily stand-up, design authority |
| Information Security | Access, data protection | Medium | High | Design review of auth and permission sets |
| Internal Audit | Controls assurance | Medium | Medium | Review of maker-checker and audit trail design |
| BC Implementation Partner | Configuration, extensions | High | Medium | Joint sprint ceremonies |
| End users (Finance team, ~25) | Daily BC users | High | Low | Demos, training, change champions |

## RACI

R = Responsible · A = Accountable · C = Consulted · I = Informed

| Activity | Fin. Director | Fin. Controller | Business Analyst | IT Integration Lead | BC Partner | Process Leads (AR/AP/Treasury) | InfoSec / Audit |
|---|---|---|---|---|---|---|---|
| Business case & scope | A | C | R | C | I | C | I |
| Current-state process mapping | I | A | R | I | C | C | I |
| Business requirements (BRD) | I | A | R | C | C | C | C |
| Integration specifications | I | C | R | A | C | C | C |
| Data migration mapping | I | A | R | C | R | C | I |
| BC configuration | I | C | C | I | R/A | C | I |
| Integration build | I | I | C | A | R | I | C |
| Permission sets & approvals design | I | A | R | C | R | C | C |
| SIT | I | I | C | A | R | I | I |
| UAT | I | A | R (coordinate) | C | C | R (execute) | I |
| Cutover & go-live decision | A | R | C | R | R | C | I |
| Hypercare | I | A | C | R | R | C | I |

## Communication plan

| Audience | Channel | Frequency | Owner |
|---|---|---|---|
| Steering group | Status report + RAID summary | Fortnightly | Project Manager / BA |
| Finance process leads | Workshops, Confluence pages | Weekly during design | Business Analyst |
| Delivery team | Stand-up, sprint review | Daily / fortnightly | Scrum Master |
| All finance users | Newsletter, demo sessions | Monthly, then weekly pre go-live | Change Lead |
