# DORA Article 17 — Incident severity matrix (bootstrap-emitted; 1A in v5.1)

EU Regulation 2022/2554 (Digital Operational Resilience Act) Article 17 requires financial entities and their critical ICT third-party providers to classify ICT-related incidents by severity and report them within fixed deadlines. The thresholds below mirror the Commission Delegated Regulation (EU) 2024/1773 RTS classification criteria.

This template is informational for non-FE projects. Adopt as-is for projects that ship into EU financial entities; tighten thresholds for higher-risk verticals.

> 📚 **Authority**: https://eur-lex.europa.eu/eli/reg/2022/2554/oj  
> 📚 **RTS**: Commission Delegated Regulation (EU) 2024/1773

## Classification criteria (per Art. 18 + RTS)

An ICT incident is classified by 7 criteria. A "major" incident must reach significance on ≥ 2 of these criteria simultaneously.

| # | Criterion | Significant threshold | Project-specific value |
|---|---|---|---|
| 1 | Clients / financial counterparts affected | ≥ 10% of all clients OR ≥ EUR 100k transaction value | <FILL_IN> |
| 2 | Reputational impact | Media coverage in 2+ EU member states OR regulator inquiry | <FILL_IN> |
| 3 | Duration + service downtime | > 24 hours total OR > 2 hours during critical business window | <FILL_IN> |
| 4 | Geographical spread | Affects clients in 2+ EU member states | <FILL_IN> |
| 5 | Data losses | Confidentiality / integrity / availability breach of business-critical data | <FILL_IN> |
| 6 | Criticality of services affected | Function listed in entity's Critical or Important Function inventory | <FILL_IN> |
| 7 | Economic impact | ≥ EUR 100k direct cost OR ≥ EUR 500k expected indirect | <FILL_IN> |

## Reporting deadlines (per Art. 19)

| Phase | Deadline (after detection) |
|---|---|
| Initial notification | 4 hours of classification as major |
| Intermediate report | 72 hours |
| Final report | 1 month |

## Project response playbook

1. **Detect** — alert fires (PagerDuty / Sentry / observability stack).
2. **Triage** — on-call engineer assesses against the 7 criteria above within 1 hour.
3. **Classify** — if ≥ 2 criteria significant → invoke Major Incident workflow.
4. **Notify** — for projects shipping to FE customers: open the FE-notification channel within 4 hours.
5. **Document** — record in `docs/incidents/<YYYY-MM-DD>-<short-name>.md` with the 7-criteria scorecard.
6. **Postmortem** — within 5 business days; cross-link from CHANGELOG security advisory section.
7. **Lessons-learned** — append to `lessons-learned.yaml` (v5.2 register).
