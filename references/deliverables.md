# Canonical deliverable docs — core 2 + optional 3 (v5 — was "5 canonical" in v4 per Q7)

v5 splits the v4 5-deliverable bundle into **core (always emitted)**
and **optional (opt-in per `.local/pre-release-review/config.yaml`)**.
This makes the skill usable on fresh projects without forcing them
to author 10k+ word positioning docs on their first release.

## Core deliverables (always)

| Doc | Purpose | Step | Length target |
|---|---|---|---|
| `docs/release-checklist.md` | Step-6 11-step self-referential per-release checklist | 6.A | 250–350 lines |
| **`docs/security-review-vX.Y.Z.md`** (NEW v4 — auto-generated v5 per Q9) | Per-release security audit artifact: 3 `/security-review` invocations (Step 3 builtin + Step 4 scoped wrapper + Step 6.C builtin), all `/code-review` auto-fires, CVSS/CWE/EPSS-scored findings. v5 auto-generates from per-run JSON at Step 7.10. | 3, 4, 6.C, 7 | 300–600 lines |

## Optional deliverables (opt-in)

| Doc | Purpose | Step | Length target | Opt-in via |
|---|---|---|---|---|
| `docs/positioning-and-value.md` | Step-2 exhaustive landscape + value synthesis | 2 | 10,000–15,000 words | `config.yaml deliverables.optional: [positioning-and-value]` |
| `docs/capability-matrix.md` | Step-4 functional + code-review + adversarial test snapshot | 4 | 200–400 lines | `config.yaml deliverables.optional: [capability-matrix]` |
| `docs/vX.Y.Z+1-plan.md` | Step-5 forward-looking next-release scope with design-decision rationale | 5.B | 150–250 lines | `config.yaml deliverables.optional: [next-release-plan]` |

## Default opt-in per project type

| Project shape | Default opted-in optionals |
|---|---|
| First-run new project | none (core only) |
| Job-search / portfolio project | all 3 |
| Commercial / customer-shipping project | all 3 |
| OSS library with > 100 stars | positioning + capability-matrix |
| Internal-tooling-only project | next-release-plan only |
| Hot-fix-line project (`hotfix/*` branches) | none (core only) |

Operator overrides at any time by editing
`.local/pre-release-review/config.yaml`.

Cross-link between all in-use deliverables + the project's existing
quality-bar doc (e.g., `docs/enterprise-grade.md` if it exists),
the operational test loop (e.g., `docs/testing-playbook.md`), and
the project's threat model (`docs/threat-model.md` per G5).

## Auto-generation (Q9) — `docs/security-review-vX.Y.Z.md` from per-run JSON

v4 had operators hand-curating the security-review doc from the
per-run JSON each cycle. v5 closes the loop:

1. The per-run JSON at `.local/pre-release-review/runs/<run-id>.json`
   is the structured source-of-truth
2. The template in [`docs/security-review-vX.Y.Z.md structure`](#docs-security-review-vxyzmd-structure-new-v4)
   below is the canonical rendering shape
3. At Step 7.10, the skill does template substitution: per-run JSON
   → markdown rendering → `docs/security-review-vX.Y.Z.md`
4. Operator reviews + can hand-edit the markdown (changes don't
   round-trip back to JSON — JSON stays the audit-truth)
5. Auto-commit via [commit](../../commit/SKILL.md) skill

Saves ~30 min per cycle + removes the drift surface where the JSON
+ markdown disagree about the same finding.

## The "in-repo doc + MEMORY.md pointer" pattern

Per the canonical pattern in `~/.claude/CLAUDE.md`:

- Each in-repo doc gets a single-line MEMORY.md entry + a
  sibling `pointer_<doc>.md` file
- The pointer file contains: doc location, what it is, re-execution
  recipe (if applicable), version history, picked-up-where-we-left-off
  context
- Future Claude sessions auto-load the pointers and know where to
  find the canonical content

## `docs/security-review-vX.Y.Z.md` structure (NEW v4)

Required top-level sections:

```
# Security review — v0.7.5 (2026-04-30)

## Summary
- Total findings: N (X CRITICAL, Y HIGH, Z MEDIUM, W LOW)
- All CRITICAL fixed pre-tag: yes/no (with deferral rationale if no)
- Compliance posture: NIST SSDF + ISO 27001 + SOC 2 + DORA mapping

## /security-review invocations
- Invocation 1 (Step 3, diff prev-tag..HEAD): N findings
- Invocation 2 (Step 4, per-subsystem): N findings
- Invocation 3 (Step 6.C, full pre-tag): N findings

## /code-review auto-fires
- Trigger 1 (new public API): fired/not-fired, findings
- Trigger 2 (new source file): fired/not-fired, findings
- ...

## Bug-bucket table
[CRITICAL/HIGH/MEDIUM/LOW with CVSS/CWE/EPSS columns]

## Step 7 post-tag verification outcome
[See step-7-post-tag.md §7.10 for inputs]

## Cross-references
- capability-matrix.md row links
- threat-model.md asset/boundary mapping
- enterprise-grade.md BLOCKER list
```
