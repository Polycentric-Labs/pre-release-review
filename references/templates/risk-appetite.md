# Risk appetite statement (bootstrap-emitted; 1C in v5.1)

> Companion doc to GOVERNANCE.md. Declares what risks the project is willing to accept, mitigate, transfer, or avoid. Read by `/pre-release-review` Step 5.A bug-bucketing to calibrate ship/no-ship calls on MEDIUM+ findings.

## Risk-appetite tiers (per ISO 31000 framing)

| Risk category | Posture | Rationale |
|---|---|---|
| **Security — known CVEs in dependencies** | AVOID | Hard block on CRITICAL / HIGH at pre-push gate; v5 Row 14 |
| **Security — solo-dev structural gaps (no two-person review)** | ACCEPT, with mitigation | AI-as-force-multiplier framing + automated gates; honest-gap declared per compliance-mapping.md |
| **Security — zero-day in upstream** | TRANSFER | Coordinated disclosure via SECURITY.md; do not promise instant patches |
| **Reliability — non-deterministic test failures** | MITIGATE | Quarantine + flaky-test issue; do not ship cycle until fixed |
| **Reliability — silent data corruption** | AVOID | Hard block; rollback before publish if detected |
| **Compatibility — breaking API change in patch release** | AVOID | SemVer hard rule; patch releases NEVER break consumers |
| **Compatibility — breaking API change in minor release (pre-1.0)** | ACCEPT, with notice | Pre-1.0 explicit "anything may change" signal; document in CHANGELOG |
| **Compatibility — breaking change in major release** | ACCEPT, with migration path | `/pre-release-review` DMADV variant (1K) covers; provide codemod or migration guide |
| **Operational — release process failure mid-publish** | MITIGATE | Verification gates (Step 7) catch; rollback playbook in release-checklist |
| **Reputational — public security advisory** | ACCEPT | Coordinated disclosure is healthier than concealment |
| **Reputational — premature shipment of unfinished feature** | AVOID | Better to delay than to ship something that under-delivers stated capability |
| **Regulatory — DORA Art. 17 incident classification** | MITIGATE | Bootstrap-emitted DORA-Art-17-incident-matrix.md (1A) calibrates classification thresholds |
| **Legal — GPL/AGPL contamination** | AVOID | Step 7 SCA gate flags incompatible licenses |
| **Legal — DCO/CLA absent on contributions** | ACCEPT (solo-dev) | OSPS-LE-01 partial; v5.2 candidate to enforce |

## Quantitative bounds (where measurable)

| Metric | Bound | Source |
|---|---|---|
| Mean time to acknowledge security report | ≤ 72 hours | SECURITY.md |
| Mean time to patch CRITICAL | ≤ 30 days | SECURITY.md |
| Mean time to patch HIGH | ≤ 30 days | SECURITY.md |
| Mean time to patch MEDIUM | ≤ 90 days | SECURITY.md |
| Coverage threshold (test) | ≥ 80% (OpenSSF Silver) or ≥ 90% (Gold) | Pre-push gate Row 6 (1I, v5.1) |
| Stale review tolerance | < 4 hours (low risk) / < 2 hours (medium) / < 1 hour (high) | Guideline #12 + 1R repo-risk-tier (v5.1) |
| MEDIUM-and-above finding density per release | < 5 per minor release | Bug-bucketing rule of thumb |

## Acceptance criteria

The project does NOT ship a release if any of the following are true:

1. Any unresolved CRITICAL or HIGH security finding
2. Any failing pre-push gate row without an explicit bypass-phrase + documented reason
3. Stale per-run JSON (> bound from 1R repo-risk-tier; default 4 hours)
4. Any uncovered honest-gap that has shifted from "accept" to "avoid" since the last cycle
5. New regulatory requirement (DORA, EU AI Act, etc.) that the current release would not satisfy

## Review cadence

Re-read this doc at every `/pre-release-review` Step 1 (process review) and update if any tier or bound has shifted. Bump the policy version + commit date in CHANGELOG.
