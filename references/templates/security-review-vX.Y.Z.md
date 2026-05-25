# Security review — {PROJECT_NAME} v{VERSION} ({DATE})

> Skill-bootstrapped template (v5 first-run-bootstrap deliverable).
> Auto-generated at Step 7.10 from `.local/pre-release-review/runs/<run-id>.json` per Q9.
> Operator can hand-edit the markdown; per-run JSON remains source-of-truth.

## Summary

- Total findings: {N} ({CRIT} CRITICAL, {HIGH} HIGH, {MED} MEDIUM, {LOW} LOW)
- All CRITICAL fixed pre-tag: {YES_NO}
- Compliance posture: NIST SSDF + ISO 27001 + SOC 2 + DORA mapping in `~/.claude/skills/pre-release-review/references/compliance-mapping.md`

## Cycle scope

{CYCLE_SCOPE_NARRATIVE — what shipped, themes, references to v{VERSION}-plan.md}

## /security-review invocations

| # | Step | Kind | Scope | Findings |
|---|---|---|---|---|
| 1 | 3 | builtin | `<prev-tag>..HEAD` diff | {N1} |
| 2 | 4 | scoped-wrapper | per-subsystem (see partition) | {N2} |
| 3 | 6.C | builtin | full HEAD vs prev-tag | {N3} |

## /code-review auto-fires

| Trigger | Fired | Findings |
|---|---|---|
| #1 New public API/CLI/route | {Y_N} | {COUNT} |
| #2 New source file | {Y_N} | {COUNT} |
| #3 > 500 LOC changed | {Y_N} | {COUNT} |
| #4 Security-relevant subsystem touched | {Y_N} | {COUNT} |

## Bug-bucket table

| ID | Bucket | Category | Location | CVSS v3.1 | CWE | EPSS | Disposition |
|---|---|---|---|---|---|---|---|
| {ROW} | {CRIT/HIGH/MED/LOW} | {CATEGORY} | {file:line} | {score (severity)} | {CWE-N} | {prob} | {fix-in-S<n> / defer-to-vX.Y.Z+1 / accepted} |

## Step 6 19-row pre-push gate

| # | Check | Status |
|---|---|---|
| 1 | Credential pattern sweep | {PASS/FAIL/N_A} |
| 2 | Claude attribution sweep | {PASS/FAIL/N_A} |
| 3 | Commit-message attribution sweep | {PASS/FAIL/N_A} |
| 4 | .gitignore audit | {PASS/FAIL/N_A} |
| 5 | Staged secret-store files check | {PASS/FAIL/N_A} |
| 6 | Test gate | {PASS/FAIL/N_A} |
| 7 | Type/lint gate | {PASS/FAIL/N_A} |
| 8 | Build sanity | {PASS/FAIL/N_A} |
| 9 | Identity check | {PASS/FAIL/N_A} |
| 10 | Branch sanity | {PASS/FAIL/N_A} |
| 11 | Legacy-secret check | {PASS/FAIL/N_A} |
| 12 | Code-scanning alert delta | {PASS/FAIL/N_A} |
| 13 | Container CVE scan | {PASS/FAIL/N_A} |
| 14 | Vuln-aging SLO | {PASS/FAIL/N_A} |
| 15 | License/SCA SPDX | {PASS/FAIL/N_A} |
| 16 | Secret-rotation cadence | {PASS/FAIL/N_A} |
| 17 | CHANGELOG-presence | {PASS/FAIL/N_A} |
| 18 | Branch-protection bypass audit | {PASS/AUDIT_EVENT/N_A} |
| 19 | Documentation freshness | {PASS/FAIL/N_A} |

## Step 7 post-tag verification outcome

{Generated from publish-targets.yaml driving the sub-step list.}

## Bypass events

{If any verbatim bypass phrases were used during this cycle, listed here with rationale.}

## Disposition

{PROCEED-CLEAN / PROCEED-WITH-DEFERRALS / HOLD}

{Nth consecutive PROCEED-CLEAN of <line> tracking line.}

## Cross-references

- `docs/v{VERSION}-plan.md` — phase-by-phase scope
- `docs/v{VERSION_NEXT}-plan.md` — forward-looking next-release scope
- `docs/release-checklist.md` — the canonical per-release runbook
- `~/.claude/skills/pre-release-review/SKILL.md` — the skill driving this review
- `.local/pre-release-review/runs/{RUN_ID}.json` — structured source-of-truth
