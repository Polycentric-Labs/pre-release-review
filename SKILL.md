---
name: pre-release-review
version: 2026.06.04-v5.2
description: |
  Run a comprehensive pre-release review of a project before tagging
  a high-stakes release. v5.2 (2026-06-04) folds in 4 refinements
  surfaced by the RegRails v0.4.0 + Evidentia v0.10.7/v0.10.8 sweeps
  (additive; no existing behavior changed): G27 unified capability
  inventory (Step 2.2 / Step 4 walk the CLI `--help` tree + API/OpenAPI
  surface + UI routes TOGETHER, flagging any CLI leaf with no API/UI
  surface — the gap a passing type-drift gate would mask); G28 docs-
  from-verified-facts publish gate (every shipped doc/wiki claim must
  trace to a `doc-runtime-verifier` PASS, proactive — not a post-hoc
  accuracy sweep); G29 right-sizing rubric (an explicit read-the-change
  → judge-attack-surface → dial-the-ceremony call: full vs right-sized,
  with criteria); G30 gates-exist seam (Step 1.0 checks the project's
  automatic gates — version-consistency / tag-time gate / CLI↔UI parity
  / secret-scan / commit-msg hook — exist, and points at the setup-time
  companion skill `release-safeguards-scaffolder` if any are missing).
  v5.1.4 (2026-05-27) reflects the Evidentia-
  side refactor that moves Step 5.D.3's phrase-audit regex set out of
  the public-tracked script source and into a gitignored config file
  (`private/check-docs-health-patterns.yaml`). The skill's invocation
  is unchanged (`scripts/check_docs_health.py --strict`); if the
  project under review has no config file present, the 4 phrase-
  related checks (phrase_audit, commit_msg_audit, tag_msg_audit,
  release_body_audit) emit one advisory WARN and the 4 doc-health
  checks (parse_validity, cross_link_resolve, readme_size_guard,
  private_path_leak) still run normally. v5.1.3 (2026-05-27) extended
  Step 5.D.3's comprehensive docs-health check from 5 invariants to 8
  by adding 3 publicly-facing-surface checks (commit_msg_audit,
  tag_msg_audit, release_body_audit) that scan `git log <cutoff>..HEAD`
  bodies + annotated tag bodies + the latest GitHub Release body
  against the same regex set as phrase_audit. Cutoff SHA `f1dac4e`
  per Allen 2026-05-27 treats earlier commit / tag history as
  immutable (force-update would break cosign signatures bound to those
  SHAs); v0.10.5 tag + earlier are allowlisted. `release_body_audit`
  uses `gh api` and runs in advisory mode (gracefully WARNs if gh is
  unauthenticated). Companion `.githooks/commit-msg` (activated via
  `bash scripts/setup-githooks.sh`) catches forbidden phrasing at
  `git commit` time as defense-in-depth before the skill's pre-tag
  gate fires; bypass env var EVIDENTIA_ALLOW_PHRASE_BYPASS=1.
  v5.1.2 (2026-05-27) added a Step 5.D.3
  comprehensive docs-health check that runs the target project's
  `scripts/check_docs_health.py --strict` and blocks the tag at 5.D
  on any FAIL across 5 invariants (parse_validity, cross_link_resolve,
  readme_size_guard, phrase_audit, private_path_leak). Prevents
  docs-only regressions (broken cross-links, forbidden-phrase matches,
  README bloat, private-path leaks) from shipping silently in a tag.
  Added per Allen's 2026-05-27 directive after the Evidentia v0.10.7
  docs-cleanup cycle surfaced ~50 broken cross-links + 35 forbidden-
  phrase matches that would have shipped without the gate.
  v5.1.1 (2026-05-27) added a Step 5.D.2 new-
  PyPI-project pending-publisher pre-flight check that catches the
  Evidentia v0.10.5 partial-publish failure mode (LL-V105-1) BEFORE
  `release.yml` fires: any workspace package that does NOT yet exist
  on PyPI (HTTP 404 on `pypi.org/pypi/<pkg>/json`) is flagged and the
  operator must confirm a pending publisher row is configured in the
  PyPI dashboard before Step 6.F is allowed to surface `git tag`.
  v5.1 (2026-05-24) added: 8 compliance-mapping extensions (SLSA v1.2
  + NIST SP 800-218A scope-corrected subset + OSPS Baseline 8-family
  enumeration + NIST SSDF v1.2 IPD watch + CMMI honest-claim + expanded
  honest-gap field with AI-as-force-multiplier framing); 5 bootstrap-
  emitted compliance templates (DORA Art. 17 incident matrix +
  SECURITY.md/security.txt/GHSA + GOVERNANCE.md/EOL.md/risk-appetite +
  A.6.3 training log + OSPS-DO-03 verification recipe); Row 20 OSPS-
  QA-05 binary-in-VCS check + Row 6 coverage-threshold enforcement;
  Step 7.4.5 reproducible-build verify (when in-scope); 4 skill-prose
  enhancements (3-question business-case prompt at Step 6.E + Goddard/
  Parasuraman/Cerbos/CodeRabbit/Apiiro citations in bypass-protocol +
  FAIR Loss Magnitude column in bug-bucketing); freshness-window
  parameterization (repo_risk_tier + context-sensitive invalidation
  triggers); new scripts/control_chart.py (I-MR / u-chart / g-chart /
  DPMO over per-run JSONs); DMADV 5th variant for major-version bumps.
  v5 baseline carried forward: project-shape detection (portable
  across Python/Node/Rust/Go/Java/Ruby/PHP/Elixir/.NET); first-run
  bootstrap wizard; Guideline #12 hard rule; 17→19→20-row pre-push
  gate; publish-targets.yaml-driven Step 7; /security-review-scoped
  wrapper; EPSS auto-lookup; G6 Python gates; auto-generate
  docs/security-review-vX.Y.Z.md; core (2) + optional (3) deliverables.
  Variants: Pre-tag, Pre-push, Pre-merge-to-main, Quarterly cadence,
  **DMADV** for major-version bumps. Multi-hour to multi-session
  investment; NOT appropriate for every PR or patch release.
  Prototyped on Evidentia v0.7.0 (v3, April 2026) → v0.7.5 (v4) →
  v0.10.4 (v5 design, May 2026) → v5.1 (May 24 2026) → v5.1.1
  (May 27 2026, LL-V105-1 prevention from Evidentia v0.10.5) →
  v5.1.2 (May 27 2026, docs-health gate from Evidentia v0.10.7
  docs-cleanup cycle) → v5.1.3 (May 27 2026, publicly-facing-surface
  extension from Evidentia commit `f1dac4e`) → v5.2 (Jun 4 2026, the
  4-refinement fold from the RegRails v0.4.0 + Evidentia v0.10.7/
  v0.10.8 sweeps; companion to the setup-time
  `release-safeguards-scaffolder` skill).
---

# Pre-release review (v5)

A comprehensive, methodical, user-in-the-loop pre-tag review process
for high-stakes releases. v5 is **portable across project types**
(language + build system + publish targets are detected at Step 1.0)
and adds a mechanical hard rule that the AI driver cannot bypass the
review and surface push commands.

> ⚠️ **Guideline #12 hard rule + Publishing-authority protocol**
>
> The AI driver MAY NOT surface `git push`, `git push --tags`,
> `gh pr merge`, or any irreversible-publish command unless:
> (a) a per-run JSON exists for THIS review with `completed_at` < 4
>     hours, AND
> (b) the user has explicitly approved the action per the global
>     publishing-authority protocol in `~/.claude/CLAUDE.md`.
>
> If (a) is missing, the user must type ONE of three verbatim bypass
> phrases per [references/bypass-protocol.md](references/bypass-protocol.md):
> `PUSH TO MAIN BYPASS AUTHORIZED` / `STALE REVIEW ACCEPTED — <reason>`
> / `DOC FRESHNESS BYPASS — <reason>`.

## Skill architecture (v4 split, v5 extends)

Entry point (`SKILL.md`) + reference files in `references/`. Load
only references you need per step.

| File | Loaded when | Contents |
|---|---|---|
| [references/variants.md](references/variants.md) | Step 1 | 4 variant flows + time estimates + skip criteria |
| [references/steps-1-2.md](references/steps-1-2.md) | Steps 1–2 | Step 1.0 shape-detect + bootstrap + scope-confirm + threat-model freshness + protected-branch suggest + per-run freshness check |
| [references/steps-3-4.md](references/steps-3-4.md) | Steps 3–4 | Commit re-test + capability matrix + adversarial + DAST + scoped wrapper |
| [references/steps-5-6.md](references/steps-5-6.md) | Steps 5–6 | Refinements + doc-inventory iteration + 19-row gate + tag prep |
| [references/step-7-post-tag.md](references/step-7-post-tag.md) | Step 7 | Publish-targets-driven verification (SLSA L3 / NIST SSDF PS.3.1) |
| [references/pre-push-gate.md](references/pre-push-gate.md) | Any push | **19-row runbook** (17 base + Row 18 bypass-audit + Row 19 doc-freshness) |
| [references/security-review-integration.md](references/security-review-integration.md) | Steps 3, 4, 6.C | 3-invocation pattern (#1 + #3 builtin; #2 scoped wrapper) |
| [references/security-review-scoped-wrapper.md](references/security-review-scoped-wrapper.md) | Step 4 | **NEW v5** — per-subsystem `/security-review-scoped` wrapper |
| [references/code-review-integration.md](references/code-review-integration.md) | Step 3 entry | 4 auto-fire triggers (project-shape-aware) |
| [references/deliverables.md](references/deliverables.md) | Steps 2, 4, 5, 6, 7.10 | **Core 2 + optional 3** + auto-gen security-review doc |
| [references/bug-bucketing.md](references/bug-bucketing.md) | Every step | CRITICAL/HIGH/MEDIUM/LOW + CVSS / CWE auto / EPSS auto |
| [references/compliance-mapping.md](references/compliance-mapping.md) | Steps 6, 7 | NIST SSDF + SLSA + ISO 27001 + SOC 2 + DORA + OpenSSF + CISA |
| [references/verification-gates.md](references/verification-gates.md) | Step boundaries | **Rewritten in Python** for cross-platform parity |
| [references/tools-prerequisites.md](references/tools-prerequisites.md) | Step 1 entry | Tool install guide + worktrees + Python 3.11+ hard prereq |
| [references/maintenance.md](references/maintenance.md) | Editing this skill | Meta-rubric for SKILL.md changes (v5 extensions) |
| [references/bypass-protocol.md](references/bypass-protocol.md) | Any push attempt | **NEW v5** — Guideline #12 + 3 verbatim bypass phrases + protected-branch auto-suggestion |
| [references/project-shape-detection.md](references/project-shape-detection.md) | Step 1.0 | **NEW v5** — language/build/publish/branch-protection auto-detection |
| [references/first-run-bootstrap.md](references/first-run-bootstrap.md) | Step 1.0 first-run only | **NEW v5** — wizard for new projects |
| [references/publish-targets.md](references/publish-targets.md) | Steps 1 + 7 | **NEW v5** — 9-kind `publish-targets.yaml` drives Step 7 |
| [references/documentation-freshness.md](references/documentation-freshness.md) | Steps 1, 5.C, 6 (Row 19), 7.10 | **NEW v5** — `doc-inventory.yaml` + freshness gate + `must_match_version` |

`_archive/` preserves prior major versions (`SKILL-2026.04.25-v3.md`,
`SKILL-2026.04.30-v4.md`, `SKILL-2026.05.23-v5.0.1.md`). Read-only;
not callable.

`scripts/control_chart.py` (NEW v5.1; 1J): stdlib-only Python helper
for statistical process control (I-MR / u-chart / g-chart / DPMO)
over per-run JSONs. Standalone CLI invocation; no install step.

## When to use this skill

**Use** when:

- Project will be evaluated by employers, customers, auditors, or regulators
- Release introduces a new "enterprise-grade" claim (Sigstore, SBOM, SLSA, OSCAL, etc.)
- Major or minor version bump that will be widely consumed
- Project hasn't had a formal review in 3+ months
- User explicitly asks for "comprehensive" / "exhaustive" / "full ship"

**Do NOT use the full pre-tag flow** when:

- Patch release with a single bug fix (use the [19-row pre-push gate](references/pre-push-gate.md) alone — but the gate STILL produces a per-run JSON to satisfy Guideline #12)
- Hot-fix needing same-day deployment (skip everything except the pre-push gate; bypass with explicit phrase if even that's too long)
- Project has minimal external visibility and review cost would exceed bug-discovery upside

For variants and time estimates, see [references/variants.md](references/variants.md).

## The 12 binding guidelines (apply at every step)

1. Parallel tool calls for performance.
2. Use the full capability set: parallel `Agent`, Perplexity research/reason/ask MCP, Hugging Face MCP, WebSearch + WebFetch, gh CLI via Bash. List relevant subset to the user up front.
3. Question all assumptions. Validate with primary sources.
4. Validate every claim with at least one citation. Flag uncited claims.
5. Update the user on errors, findings, ideas, improvements as they arise.
6. Ask all relevant questions with pros/cons + stated recommendation.
7. Present planned changes for explicit approval before making them.
8. Present a review of what occurred at each step boundary.
9. Get explicit user permission before moving to the next step.
10. Commit process + results to memory after each step.
11. Explain things as we go (educational mode on).
12. **(NEW v5) NEVER surface `git push`, `git push --tags`, `gh pr merge`, or any irreversible-publish command without a fresh per-run JSON (< 4 hours) AND user's explicit per-action approval. Bypass requires a verbatim phrase per [bypass-protocol.md](references/bypass-protocol.md). This rule is mechanical, not advisory.**

## The 7-step structure (unchanged from v4)

| Step | Goal | Reference |
|---|---|---|
| 1 | Process review (incl. 1.0 shape-detect + bootstrap + **1.0 gates-exist seam [G30]** + 1.4 scope + **right-sizing rubric [G29]** + 1.5 threat-model + 1.5.1 protected-branch + 1.5.2 review-freshness) | [steps-1-2.md](references/steps-1-2.md) §1 |
| 2 | Project review (positioning, value, world-class direction; **2.2 unified CLI+API+UI capability inventory [G27]**) — skip-by-reuse if criteria hold; SKIP entirely when optional deliverable not in `config.yaml` | [steps-1-2.md](references/steps-1-2.md) §2 |
| 3 | Re-test commits (mandatory `/security-review` + auto-fire `/code-review`) | [steps-3-4.md](references/steps-3-4.md) §3 |
| 4 | Full capability test (mandatory `/security-review-scoped` + DAST per [G11]; **cross-surface capability walk [G27]**) | [steps-3-4.md](references/steps-3-4.md) §4 |
| 5 | Project-wide refinements + doc-inventory iteration (**5.C docs-from-verified-facts provenance [G28]**) | [steps-5-6.md](references/steps-5-6.md) §5 |
| 6 | Release-checklist + final review + tag + push (final `/security-review` + 19-row pre-push gate; **Row 19 trace-to-verifier [G28]**) | [steps-5-6.md](references/steps-5-6.md) §6 |
| 7 | Post-tag verification (publish-targets-driven; SLSA / NIST SSDF PS.3.1; auto-gen security-review doc) | [step-7-post-tag.md](references/step-7-post-tag.md) |

Each step boundary STOPs for explicit user approval. Step output is
programmatically verified by [verification-gates.md](references/verification-gates.md)
(Python; cross-platform).

## What's new in v5 (vs v4 `2026.04.30-v4`)

11 substantive changes addressing the v4 deep-review's 20 surfaced
gaps + the standing documentation-freshness requirement. Full
mapping in `~/.claude/projects/<project>/memory/pre_release_review_v5_design_decisions.md`.

- **G16** — Guideline #12 hard rule: AI cannot bypass review-before-push without a verbatim bypass phrase
- **G17** — Project-shape detection at Step 1.0 (language/build/publish/branch-protection autodetect)
- **G18** — First-run bootstrap wizard for greenfield projects
- **G19** — `/security-review-scoped` wrapper unblocks the v4 Step 4 per-subsystem invocation
- **G20** — `publish-targets.yaml` schema drives Step 7 sub-step generation (9 kinds + custom)
- **G21** — `doc-inventory.yaml` + Row 19 documentation-freshness gate + `must_match_version`
- **G22** — Row 18 branch-protection bypass audit (capture + flag, never hard-fail)
- **G23** — EPSS auto-lookup via FIRST.org API + CWE auto-populate from `/security-review` output
- **G24** — G6 verification gates rewritten in Python (cross-platform; drops GNU coreutils dependencies)
- **G25** — Auto-generate `docs/security-review-vX.Y.Z.md` from per-run JSON at Step 7.10
- **G26** — Stale-review lockout: WARN at 2h, REFUSE at 4h (per-run JSON age check)

Plus 2 sub-changes:

- **Core (2) + optional (3) deliverables split** — replaces v4's 5-mandatory shape
- **17→19 row pre-push gate** — Row 17 (CHANGELOG-presence, post-v0.10.3) + Row 18 (bypass-audit, v5) + Row 19 (doc-freshness, v5)

## What's new in v5.2 (vs v5.1.4)

4 additive refinements surfaced by the RegRails v0.4.0 +
Evidentia v0.10.7/v0.10.8 sweeps. Each is a refinement to an
existing step — no step renumbered, no existing behavior changed.

- **G27 — Unified capability inventory.** Step 2.2's internal
  capability inventory (and the Step 4 surface walk) now enumerates
  the CLI `--help` tree **+** the API/OpenAPI surface **+** the UI
  routes **together**, not docs-only. The cross-surface diff flags any
  CLI leaf with **no** corresponding API or UI surface — the
  coverage gap a passing type-drift gate masks (a typed frontend can
  stay green against the schema while large parts of the CLI never
  reached the GUI). The inventory is one matrix keyed by capability,
  with a column per surface (CLI / API / UI) and a verdict per cell;
  a CLI-only row is a finding to surface, not a silent omission.
- **G28 — Docs-from-verified-facts publish gate.** Every shipped
  doc/wiki claim must trace to a `doc-runtime-verifier` PASS
  **before** it ships — a proactive publish gate, not a post-hoc
  accuracy sweep. The Step 5.C doc-inventory iteration + the Row 19
  freshness gate gain a provenance requirement: an in-scope doc whose
  factual/command claims have not been run through `doc-runtime-verifier`
  (PASS recorded) is treated as unverified and surfaced for
  verification before tag, rather than trusted because it "looks
  right." Stops a confidently-wrong command or stat from shipping in
  the docs or wiki.
- **G29 — Right-sizing rubric.** An explicit
  **read-the-change → judge-attack-surface → dial-the-ceremony**
  call at Step 1, replacing instinct with criteria. Read the actual
  diff; classify the change's attack/blast surface; then choose
  **full** ceremony vs a **right-sized** variant. A
  presentation-only / docs-only / internal-refactor change with no
  new externally-reachable surface right-sizes down (often the
  pre-push gate alone). A change that adds a **new endpoint, a new
  secret/credential path, or any irreversible surface** (a publish
  target, a destructive operation, a new network egress) takes the
  full flow regardless of line count. The rubric is advisory input to
  the Step 1 variant choice (see
  [variants.md](references/variants.md)) — it never lowers a gate, it
  sizes the *review*.
- **G30 — Gates-exist seam.** Step 1.0 adds a check that the
  project's **automatic** gates exist — version-consistency,
  tag-time release gate, CLI↔UI parity, secret-scan, commit-msg
  hook. These are *setup-time* machinery, not something this
  release-time skill installs. If any are missing, point the operator
  at the **`release-safeguards-scaffolder`** skill (the setup-time
  companion that wires them once per project) rather than hand-rolling
  them mid-review. This skill *checks the gates exist and runs the
  review*; the scaffolder *creates the gates*. The seam keeps the two
  responsibilities distinct (see "Companion skills" below).

## Commit-attribution discipline (unchanged from v3)

Every commit during this review uses the user's canonical git
identity per `~/.claude/CLAUDE.md`. NEVER include
`Co-Authored-By: Claude` or 🤖 footers. Use conventional-commit
prefixes (`feat(<scope>):` / `fix(<scope>):` / `chore(release|lint|refinements):`
/ `docs(<scope>):` / `ci(<scope>):` / `chore(lint):`).

## Anti-patterns to avoid

- **Force-pushing main** — destroys audit trail; can break Sigstore provenance chains. Only forward commits.
- **Rushing HIGH-bucket design decisions** — v(X+1) narrative > half-baked current fix.
- **Marking a release "enterprise-grade" without honest gap list** — auditors and hiring managers respect honest gaps.
- **Skipping external repo + service review** — catches stale GitHub About text, missing PyPI Trusted Publisher entries, leaked emails, expired environment-protection rules.
- **Pushing or tagging without explicit user approval** — even after earlier approvals, the tag is the irreversible step + deserves its own gate. Step 7 has its own STOP.
- **Skipping `/security-review` because the diff "looks fine"** — v5 makes this mechanical at 3 boundaries. Catches what human eyeballing misses.
- **Lowering a verification-gate threshold without explicit rationale** — gates exist to catch coverage drops. Remediate, don't relax. Any threshold change logs explicit risk-acceptance.
- **Treating Step 7 as optional** — it's the SLSA L3 / NIST SSDF PS.3.1 audit-loop closure. A "tagged but not Step-7-verified" release is not finished.
- **(NEW v5) Surfacing `git push` without a fresh per-run JSON** — Guideline #12 makes this a hard rule. Use the bypass phrase or run the review.
- **(NEW v5) Editing a doc that's not in `doc-inventory.yaml`** — surface "add to inventory?" before commit. Untracked docs decay silently.
- **(NEW v5) Skipping `/security-review-scoped` Step 4 invocation** — v4 let this slide 4 cycles running. v5 makes it mandatory with the wrapper.
- **(NEW v5.2) Inventorying capabilities from one surface only [G27]** — a docs-only or CLI-only inventory hides a CLI leaf that never reached the API/UI. Walk all surfaces together; a CLI-only row is a finding, and a passing type-drift gate does NOT mean GUI coverage is complete.
- **(NEW v5.2) Shipping a doc/wiki claim that never ran [G28]** — "it looks right" is not verification. Every shipped doc/wiki command + factual claim must trace to a `doc-runtime-verifier` PASS before tag, not a post-hoc sweep after a reader notices it's wrong.
- **(NEW v5.2) Running full ceremony (or skipping it) on instinct [G29]** — read the change, judge the attack surface, then dial: presentation-only right-sizes down; a new endpoint / secret / irreversible surface takes the full flow regardless of line count. The rubric sizes the *review*, never the *gates*.
- **(NEW v5.2) Hand-rolling automatic gates mid-review [G30]** — version-consistency / tag-time / parity / secret-scan / commit-msg gates are setup-time machinery. If they're missing, point at `release-safeguards-scaffolder`; don't improvise them during a release-time review.

## "in-repo doc + MEMORY.md pointer" pattern

Per `~/.claude/CLAUDE.md`: each in-repo doc gets a single-line
MEMORY.md entry + a sibling `pointer_<doc>.md` file. Future Claude
sessions auto-load pointers + know where canonical content lives.
Applies to all deliverables — see [references/deliverables.md](references/deliverables.md).

## Companion skills

This skill is **release-time**: it runs the comprehensive review
before a tag. Two skills compose with it; neither duplicates it.

- **`release-safeguards-scaffolder` — the setup-time counterpart.**
  It *installs* a project's automatic gates **once** — version-
  consistency, the tag-time release gate, CLI↔UI parity, secret-scan,
  and the commit-msg hygiene hook — so release quality is mechanical
  rather than remembered. This skill *checks those gates exist* (the
  G30 seam at Step 1.0) and *runs the review* every release; the
  scaffolder *creates* them. Setup-time vs release-time: if Step 1.0
  finds a gate missing, point the operator at the scaffolder rather
  than hand-rolling it mid-review.
- **`doc-runtime-verifier` — the docs-accuracy engine behind G28.**
  Every shipped doc/wiki command + factual claim must trace to a
  `doc-runtime-verifier` PASS before tag (the Step 5.C provenance
  requirement + the Row 19 trace-to-verifier check). This skill
  orchestrates *when* verification is required; `doc-runtime-verifier`
  performs the run-it-in-a-sandbox-and-diff verification itself.
- **`api-gui-parity-tracker` — the typed-frontend parity engine.**
  For a typed OpenAPI frontend, the G27 cross-surface walk leans on
  the schema → typed-client drift-gate this skill wires; a passing
  drift-gate is necessary but not sufficient for GUI coverage (hence
  the G27 CLI-leaf flag).

## Reference implementations

- **v3** (six-step) — Evidentia v0.7.0, April 2026. 18 bugs surfaced across 4 buckets.
- **v4** (seven-step, mandatory `/security-review` + 17-row gate) — Evidentia v0.7.5, April 2026 → v0.10.3, May 2026 (where the v4 design's `/security-review` #2-skipped failure mode + the AI-bypasses-push-gate failure mode surfaced).
- **v5** (project-shape portable + hard-rule push-gate + doc-freshness) — designed at Evidentia v0.10.4 May 23 2026 after the v4 deep-review identified 20 gaps. v5.1 prototyped on Evidentia v0.10.4 ship 2026-05-24 (17th consecutive PROCEED-CLEAN; first ship under v5.1; 9 skill-iteration findings surfaced for follow-on cycles). Project-shape support beyond Python/uv is wired in `references/project-shape-detection.md` + `references/publish-targets.md`; per-shape validation against other project types pending.

For v4 prototype output cross-reference, see Evidentia's
`docs/security-review-v0.10.3.md` + `docs/security-review-v0.10.2.md`
+ the v3-pattern docs (`docs/positioning-and-value.md`,
`docs/capability-matrix.md`, `docs/v0.10.4-plan.md`,
`docs/release-checklist.md`).

For maintenance instructions on this skill itself, see
[references/maintenance.md](references/maintenance.md).
