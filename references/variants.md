# Variants

The full 7-step process is calibrated for the **pre-tag** case. Three
common variants compress or expand it; pick the right one in Step 1.

| Variant | When | Steps to run | Time |
|---|---|---|---|
| **Pre-tag (default)** | About to tag a public release | 1 (incl. 1.0 shape-detect + 1.4 scope) → 2 → 3 (+ /security-review + /code-review triggers) → 4 (+ /security-review-scoped + DAST) → 5 (+ doc-inventory iteration) → 6 (+ /security-review at 6.C + 20-row pre-push gate) → **7 (publish-targets-driven verification)** | **10–18 hours** |
| **Pre-push (in-flight)** | Local dev work ready to push to a feature/dev branch | 1 (adapted, incl. 1.0+1.4) → 3 (diff-only + /security-review) → 5.A → pre-push gate (20 rows) | **2–4 hours** |
| **Pre-merge-to-main** | PR ready to merge from a feature branch (via `gh pr create` + `gh pr merge` flow) | 1 (incl. 1.0+1.4) → 3 (+ /security-review + /code-review triggers) → 5.A + 5.C (CHANGELOG + doc-inventory iteration) → pre-push gate | **3–5 hours** |
| **Quarterly cadence** | No release in flight, 3+ months since last review | 2 (refresh) + 4 (re-validate, /security-review-scoped on full-project surface) + doc-inventory drift check | **4–7 hours** |
| **DMADV (major-version)** (NEW v5.1; 1K) | Major-version bump (0.x → 1.0, 1.x → 2.0); introduces breaking changes, formal API stability, or any "v1.0-class" commitment | 1 → 2 (positioning expanded with v1.0 commitments) → **2.5 (Measure phase: current-state baseline doc)** → 3 → 4 (+ **Analyze phase: gap matrix vs major-version vision**) → 5 (+ **Design phase: ADRs for breaking-change decisions; migration guide**) → 6 (full pre-tag) → **7 (+ Verify phase: formal commitment certification doc, e.g., api-stability.md normative)** | **20–40 hours across 2–4 sessions** |

**v5 NOTE — push without review**: per Guideline #12, the AI driver
CANNOT surface push commands without a fresh per-run JSON (gate within
the last 4 hours). Bypass via verbatim phrase `PUSH TO MAIN BYPASS
AUTHORIZED` per [bypass-protocol.md §B1](bypass-protocol.md#b1--push-to-main-bypass-authorized).
This rule applies to ALL variants — even the lightweight pre-push
variant must produce a per-run JSON before push surfaces.

## Pre-push variant specifics

Steps 2 (positioning landscape) and 4 (full capability matrix) are
usually skippable for pre-push — positioning rarely changes between
back-to-back pushes, and the test suite that was written alongside
the in-flight code IS the capability matrix for the new surface.
Steps 6 + 7 are irrelevant (no tag).

What matters is the [19-row pre-push gate](pre-push-gate.md), which
the full pre-tag flow rolls into Step 6.C but should be a named,
runnable check on its own.

## Pre-merge-to-main specifics

Like pre-push, but with explicit CHANGELOG curation (Step 5.C subset)
because the PR is the user-visible boundary. `/code-review` is more
likely to fire than for a single-developer push (PRs typically aggregate
multiple commits), so plan for the auto-fire path.

## Quarterly cadence specifics

Runs orthogonal to releases. Goal: catch **decay** in the long-form
research artifacts (positioning-and-value.md and capability-matrix.md)
without waiting for the next release to surface it.

- Step 2: re-run the 7 research streams using the `research-resync`
  skill in parallel; semantic-diff vs prior; promote on material
  change
- Step 4: re-validate every documented capability — adversarial
  probes especially benefit from quarterly cadence because the
  surrounding ecosystem (vendor APIs, dependency behavior, regulatory
  guidance) moves

No commits, no tag — outputs are doc updates + a memory note.

## DMADV variant specifics (NEW v5.1; 1K)

DMADV (Define / Measure / Analyze / Design / Verify) is the Six Sigma methodology for designing NEW products or processes — appropriate for **major-version bumps** that introduce new architectural commitments rather than incremental polish. The other 4 variants are DMAIC-flavored (improve an existing process); DMADV is for re-architecture-class change.

When to invoke DMADV vs the standard Pre-tag variant:

| Symptom | Use DMADV (not Pre-tag) |
|---|---|
| Promoting 0.x → 1.0 with formal API stability commitment | ✅ |
| Bumping 1.x → 2.0 with breaking changes | ✅ |
| Introducing a new commercial / regulatory tier (Pro / Federal / Enterprise) | ✅ |
| Adding a new persona / use-case the product wasn't designed for | ✅ |
| Patch / minor release within the current major | ❌ — use Pre-tag |
| Same major version with refinements only | ❌ — use Pre-tag |

### DMADV phase mapping onto the 7-step structure

| DMADV phase | Maps to | What's different from Pre-tag |
|---|---|---|
| **Define** | Step 1 + Step 2 | Step 2 positioning doc expands with explicit v1.0 commitments (api-stability boundary, deprecation policy, support window per EOL.md, intended user populations per persona). Recommendation: lock these in a SCR (Stability Commitment Record) signed off by maintainer. |
| **Measure** | NEW Step 2.5 baseline | Document the current-state system: current API surface enumeration, current performance/security baseline, current OSPS Baseline maturity, current finding density. This is the "before" snapshot that the major bump will improve. |
| **Analyze** | Extended Step 4 | Gap matrix: every commitment from Define vs the Measure baseline. For each gap: severity, design choice options, ADR (Architecture Decision Record) capturing the choice + alternatives + rationale. |
| **Design** | Extended Step 5 | Each breaking change documented with: migration path (codemod if possible), backward-compat shim duration, deprecation timeline, communication plan. Update GOVERNANCE.md to add v1.0+ contributor expectations. |
| **Verify** | Step 6 + Step 7 | Standard pre-tag gates PLUS a "Verify" deliverable: `docs/v<MAJOR>-commitment-certification.md` that maps every commitment from Define to the evidence it was satisfied. The v1.0 commitment doc becomes a normative artifact for the version line. |

### DMADV-specific deliverables (extending the 5-deliverable core+optional set)

- `docs/api-stability.md` (or equivalent) — NORMATIVE — what changes count as breaking; SemVer interpretation for this project
- `docs/v<MAJOR>-migration-guide.md` — for users on the prior major; codemod where applicable
- `docs/v<MAJOR>-commitment-certification.md` — Verify-phase artifact; closes the DMADV loop
- ADRs (one per material design decision) at `docs/adr/NNNN-<slug>.md` using the Michael Nygard format

### Why DMADV justifies the 20-40 hour investment

Major-version-bump regret is expensive: a wrong API stability commitment locks in a years-long migration debt OR breaks the trust ratchet (users who upgraded to v1.0 expecting stability and got breaking changes in v1.1 typically don't upgrade to v2.0). The DMADV variant front-loads the design work so that the major version's commitments are explicit, evidenced, and verified at tag time. This aligns with NIST SSDF PO.4 (documented + maintained) at higher maturity, plus closes 218A PO.3.x toolchain-decisions for the new major.

## Variant decision matrix

| Symptom | Use this variant |
|---|---|
| "I'm about to type `git tag vX.Y.Z`" | Pre-tag |
| "I'm about to type `git push origin <feature-branch>`" | Pre-push |
| "I'm about to click 'Merge' on a PR" | Pre-merge-to-main |
| "It's been 90+ days since the last release-time review" | Quarterly |
| "I'm typing `git push origin main` for a docs/typo fix" | Use the pre-push gate alone — no full skill |
| "I'm doing a same-day hot-fix" | Pre-push gate alone |
| "I'm bumping 0.x → 1.0 OR 1.x → 2.0 OR introducing a new product tier" | **DMADV (NEW v5.1)** |

## Time-investment table (full pre-tag)

| Step | Time |
|---|---|
| 1 (process review + scope confirm + bug-fix policy) | 30–60 min |
| 2 (project review — skip-by-reuse if criteria hold) | 2–4 hours |
| 3 (commit re-test + /security-review + /code-review triggers) | 1–3 hours |
| 4 (capability matrix + adversarial + DAST) | 2–4 hours |
| 5 (refinements across 5–7 sub-commits) | 2–3 hours |
| 6 (release-checklist + final review + /security-review + 19-row gate) | 1–2 hours |
| 7 (post-tag verification — runs after `git push origin vX.Y.Z`) | 30–90 min |

**Total**: 10–18 hours across 1–3 sessions. Warn the user upfront
and offer a shorter variant if appropriate.

## Step 2 skip-by-reuse criteria (unchanged from v3)

Declare Step 2 complete-by-reuse and move on if **all** of these hold:

- A `docs/positioning-and-value.md` exists and is < 90 days old
- The release in flight is a **patch or minor** version bump (not
  major)
- No new "enterprise-grade" claim is being introduced
- No competitor has shipped a category-defining feature in the
  interim
- Industry-tailwind dates inside the existing doc haven't passed
  unobserved
- Threat-model doc has been refreshed within the last 180 days
  (NEW gate added in v4 — see [steps-1-2.md §1.5](steps-1-2.md))

If skipped, add a one-line note to the existing
`docs/positioning-and-value.md`'s version-history section: "Reviewed
for vX.Y.Z release on YYYY-MM-DD; no material change since vA.B.C."

## Step 4 skip-by-reuse criteria (TIGHTENED in v4)

v3: any release where `docs/capability-matrix.md` exists + < 90 days
old + no enterprise-grade claim added.

**v4**: only patch + hot-fix + docs-only releases can reuse the prior
matrix. **Every minor release re-runs the full Step 4 surface walk**
including adversarial probing per surface tier. Major releases
likewise.

Rationale: each minor release adds a new attack surface (new
collectors, new integrations, new public APIs); reusing the matrix
silently undercounts coverage.
