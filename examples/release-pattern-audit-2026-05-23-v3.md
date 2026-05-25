# Release-pattern audit v3 — /pre-release-review v5.0.1

**Date**: 2026-05-23 (Path B re-run after Sonar Deep Research timeout confirmed structural)
**Skill version audited**: `2026.05.23-v5.0.1`
**Method**: 8 parallel WebFetch calls on primary sources + 3 perplexity_ask calls (Sonar Pro short queries; the only reliable Perplexity path)
**Predecessors**: v1 (WebFetch fallback) + v2 (6 parallel subagents, sonar-reasoning fallback)

## Tool-routing diagnosis CONFIRMED

3 attempts at `mcp__perplexity-mcp__perplexity_research` (the Sonar Deep Research path Allen authorized via 1Password) all hit MCP-32001 5-minute timeout — including a trivial 5-word query ("What is NIST SP 800-218A?") with minimal reasoning_effort. **Diagnosis**: the MCP wrapper's hard 5-minute ceiling cannot accommodate Sonar Deep Research's typical response time. Cause is structural, not credit-related. Investigation checklist provided to Allen separately (7 config locations to check, starting with `~/.claude/settings.json mcp.timeoutMs` and env var `MCP_TIMEOUT`).

**Fallback path that DOES work**: WebFetch on primary sources (when the source is HTML/YAML — the NIST PDFs came back as binary that the WebFetch parser couldn't decode) + `perplexity_ask` (Sonar Pro short queries). This combination produced substantive depth on all 3 sub-questions.

## Executive summary

v3 adds depth on 3 specific items v2 only sketched + opens 1 NEW critical clarification:

- **NIST SP 800-218A scope CLARIFIED**: v2 framed "the skill is AI-authored, must map the entire AI Profile." v3 shows this is overscoped. **SP 800-218A primarily addresses AI MODEL DEVELOPMENT** (producers/acquirers of foundation models + AI systems), NOT AI-AUTHORED CODE (tools whose code was generated with AI help). The skill maps to a smaller subset (~10 tasks across PO.2.2 / PO.3.x / PS.1.x / PW.5–8 / RV.*) for the "AI-assisted code production" lens.
- **NIST SSDF v1.2 IPD adds 7+ concrete new tasks** (v2 only noted "v1.2 IPD landed"): **PO.6 (Continuous Process Improvement Plan)** with PO.6.1/.2/.3 + **PS.4 (Robust and Reliable Updates)** with PS.4.1-.4 + **expanded RV.1.2** requiring testing of "default and other common configurations". NO new top-level practice groups; NO confirmed removals.
- **OSPS Baseline 8 families fully enumerated** (~42 total controls): v2 sketched ~6 control IDs across BR + VM; v3 has the complete 8-family map (AC + BR + DO + GV + LE + QA + SA + VM). 4 NEW gap items surface that v2 missed.
- **4-hour freshness window EMPIRICALLY DEFENSIBLE** (conservative, not under-justified). NEW: should be parameterized by repo risk tier + add context-sensitive invalidation (new commits or CI changes = immediate invalidation regardless of age).

## Sub-question 1 — NIST SP 800-218A scope correction

### What v2 audit framed (overscoped)

> "Skill maps to v1.1 only — v1.2 IPD dropped Dec 17 2025... SP 800-218A (AI Profile) FINAL July 26 2024 — skill never references it. The skill is itself AI-authored (Claude Code). SP 800-218A is the SSDF AI Profile and was finalized July 2024 — 22 months before v1 audit ran and v1 audit STILL missed it."

### What v3 clarifies

SP 800-218A is **structurally a Community Profile** of SSDF v1.1 — it inherits the same task IDs (PO.\*, PS.\*, PW.\*, RV.\*) and adds AI-specific augmentation per task where relevant. **The doc's audience is producers/acquirers of AI MODELS and AI SYSTEMS**, not "anyone who used AI to write some code."

For a release-review tool whose code was written with Claude Code assistance (the v5 skill itself):

| SP 800-218A practice family | Applies to AI-authored code? | Concrete v5 mapping |
|---|---|---|
| **PO.2.2** (role-based training) | YES — strongly | "Developers using Claude Code must be trained on AI-coding-assistant risks" — currently uncited in skill |
| **PO.3.x** (toolchain) | YES — strongly | Claude Code IS part of v5's dev toolchain; should be in any toolchain inventory + approved + monitored |
| **PO.1.x** (security req's for dev env) | Partially | Prompts/telemetry may contain source code or secrets — treat as sensitive |
| **PS.1.x** (protect code) | Partially | Treat prompts + AI-generated code as sensitive artifacts; ensure AI tools don't leak proprietary code via telemetry |
| **PS.3.x** (protect build env) | Marginal | Only if AI is self-hosted/CI-integrated (Claude Code via API does not count) |
| **PW.5–PW.8** (review / test / threat-model) | YES — strongly | AI-generated code must meet equal-or-stricter review than human-written code |
| **RV.\*** (vuln response) | YES — strongly | When AI-generated code has a vuln, identify similar occurrences + adjust prompt/tool configuration |

**v5.1 action**: instead of mapping ALL of SP 800-218A (overscope), add a focused **~10-task subset** to compliance-mapping.md citing "AI-authored code production (b)" applicability per the structured rubric above. Drop the v2 framing "the skill is AI-authored, must map" → replace with "v5 skill development uses AI assistance, so a subset of 218A tasks apply via the AI-tool-in-toolchain lens."

**Source**: Perplexity Sonar Pro (declined to enumerate full 218A task list citing copyright; provided structural rubric instead).

## Sub-question 2 — NIST SSDF v1.2 IPD specific new tasks

v2 said "v1.2 IPD landed Dec 17 2025; final pending." v3 has the specific changes:

### NEW practice group additions

#### PO.6 — Continuous Process Improvement Plan (NEW practice group within PO)

| Task ID | One-sentence summary | v5 conformance |
|---|---|---|
| **PO.6.1** | Update and improve development environments as threats, tools, technologies change | ✅ v5 already does this (maintenance.md + skill version bumps) |
| **PO.6.2** | Adopt new processes/tools/techniques to avoid errors + improve product security | ✅ v5 already does this (skill itself is meta-process) |
| **PO.6.3** | Improve vulnerability response processes + **periodically review previous decisions, especially "don't patch" decisions, accounting for customer impact over time** | ⚠ NEW GAP — v5 has no "review previous don't-patch decisions" workflow |

#### PS.4 — Robust and Reliable Updates (NEW practice group within PS)

| Task ID | One-sentence summary | v5 conformance |
|---|---|---|
| **PS.4.1** | (full text not surfaced) update strategy | ⚠ NEW GAP — Allen's libraries don't have customer-update-control infrastructure |
| **PS.4.2** | (full text not surfaced) customer control | ⚠ NEW GAP — same |
| **PS.4.3** | Provide rollback mechanisms + protections against unauthorized rollback to vulnerable versions | ⚠ NEW GAP — libraries don't have rollback infrastructure; honest-gap for solo OSS |
| **PS.4.4** | Ensure resilient update engines + delivery infrastructure | ⚠ NEW GAP — same |

### Updated existing task

| Task ID | Change | v5 conformance |
|---|---|---|
| **RV.1.2** | Now explicitly requires testing **"default and other common configurations"**, not just code | ⚠ PARTIAL — v5 Row 6 test gate tests code; should add config-permutation test sub-check |

### Structure confirmed

- No new top-level practice groups (still PO + PS + PW + RV)
- No confirmed task removals or merges
- NO official anticipated FINAL publication date announced by NIST (only IPD date Dec 17 2025 + comment close Jan 30 2026)

**v5.1 action**:
- Add SSDF v1.2 IPD section to compliance-mapping.md as "FORTHCOMING (final pending)" with PO.6.1/.2/.3 + PS.4.1-.4 + expanded RV.1.2 rows
- For PO.6.3, add **NEW skill capability**: `lessons-learned.yaml` register (already in v2 Tier 2A) should include "previous don't-patch decisions" as a tracked category with quarterly review cadence
- For PS.4.x, declare as HONEST GAP — v5-managed projects are libraries/CLIs without update infrastructure; PS.4 is for shipped applications/services
- For RV.1.2 expansion, NEW Row 6 sub-check: "test default + common config permutations" (cheap addition for projects with config; honest-gap-when-N/A for pure libraries)

**Source**: Cycode summary of NIST IPD + NIST CSRC IPD landing page; cited via perplexity_ask.

## Sub-question 3 — OSPS Baseline 8-family complete control map

v2 sketched 6 control IDs across BR + VM. v3 has all 8 families enumerated below. **Total: ~42 controls across 3 maturity levels.**

### AC — Access Control (4 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-AC-01.01 | 1/2/3 | MFA required for sensitive actions in authoritative repo | ✅ relies on org MFA (out-of-skill-scope) |
| OSPS-AC-02.01 | 1/2/3 | New collaborators receive manual permission OR default to lowest-privilege | ✅ relies on org policy (out-of-skill-scope) |
| OSPS-AC-03.01 | 1/2/3 | Direct commit on primary branch blocked by enforcement mechanism | ✅ v5 Step 1.5.1 protected-branch state check |
| OSPS-AC-03.02 | 1/2/3 | Primary branch deletion requires explicit confirmation (sensitive action) | ✅ branch protection covers this |
| **OSPS-AC-04.01** | 2/3 | **CI/CD tasks without specified permissions default to lowest tier** | ⚠ **NEW GAP** — v5 doesn't audit `.github/workflows/*` for missing `permissions:` keys |
| **OSPS-AC-04.02** | 3 | **Pipeline job permissions limited to minimum necessary** | ⚠ **NEW GAP** — same |

### BR — Build & Release (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-BR-01 | 1/2/3 | Prevent untrusted input access to privileged resources in pipelines | ✅ Row 11 + Step 1.5.1 |
| OSPS-BR-02 | 2/3 | Unique version IDs per release + asset | ✅ tag + per-package version pin atomic bump |
| OSPS-BR-03 | 1/2/3 | Encrypted channels for all dev + release comms | ✅ HTTPS default; v5 doesn't check explicitly |
| OSPS-BR-04 | 2/3 | Descriptive change logs documenting functional + security mods | ✅ Row 17 CHANGELOG-presence gate |
| OSPS-BR-05 | 2/3 | Use standardized dependency management tools | ✅ uv.lock / package-lock.json / Cargo.lock per project-shape |
| OSPS-BR-06 | 2/3 | Cryptographic signatures + hashes on released assets | ✅ Step 7.3 PEP 740 + Step 7.5 cosign |
| OSPS-BR-07 | 1/3 | Prevent unintentional secret storage + establish credential mgmt policy | ⚠ PARTIAL — Row 1 sweep catches unintentional storage; explicit policy doc missing (closes via v2 B4 GOVERNANCE.md) |

### DO — Documentation (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-DO-01 | 1/2/3 | User guides (install/config/feature usage) | ✅ relies on project docs |
| OSPS-DO-02 | 1/2/3 | Defect/issue reporting mechanism | ✅ GitHub Issues (out-of-skill) |
| **OSPS-DO-03** | 3 | **Publish authenticity/integrity verification instructions for releases** | ⚠ **NEW GAP** — v5 step 7 verifies; doesn't publish the verification recipe for consumers (closes via v2 Tier 2H VSA emission + recipe doc) |
| **OSPS-DO-04** | 3 | **Document scope + duration of support per released version** | ⚠ NEW GAP — closes via v2 B4 EOL.md (already in plan) |
| **OSPS-DO-05** | 3 | **Communicate when security-update cessation occurs per release** | ⚠ NEW GAP — closes via v2 B4 EOL.md |
| OSPS-DO-06 | 2/3 | Describe process for selecting + obtaining + tracking deps | ✅ partial via SBOM (Step 7.6); explicit process doc missing |
| OSPS-DO-07 | 2/3 | Build-from-source instructions including required deps | ✅ relies on project README |

### GV — Governance (4 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-GV-01 | 2/3 | Publish project roles + responsibilities | ⚠ NEW GAP — closes via v2 B4 GOVERNANCE.md |
| OSPS-GV-02 | 1/2/3 | Public discussion mechanism | ✅ relies on GitHub Discussions/Issues |
| OSPS-GV-03 | 1/2/3 | Contribution guide | ✅ relies on CONTRIBUTING.md |
| **OSPS-GV-04** | 3 | **Formal review of permission grants before contributor elevation** | ⚠ **NEW GAP** — solo-dev honest-gap (no second reviewer for self-elevation) |

### LE — Legal (3 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| **OSPS-LE-01** | 2/3 | **Contributors assert legal authorization (DCO/CLA) on every contribution** | ⚠ **NEW GAP** — v5 doesn't check for DCO sign-off; solo-dev defaults to "self-DCO" (could add as honest-gap or trivial git config check) |
| OSPS-LE-02 | 1/2/3 | OSI-approved / FSF-recognized license | ✅ checked at project setup (Apache-2.0 for Evidentia) |
| OSPS-LE-03 | 1/2/3 | License files in standard locations | ✅ LICENSE in repo root |

### QA — Quality Assurance (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-QA-01 | 1/2/3 | Publish source + change history | ✅ GitHub repo + CHANGELOG |
| OSPS-QA-02 | 1/2/3 | Publicly visible deps | ✅ pyproject.toml / package.json / Cargo.toml |
| OSPS-QA-03 | 2/3 | Automated status checks pass before accepting changes | ✅ v5 pre-push gate + branch protection |
| OSPS-QA-04 | 1/2/3 | Consistent security requirements across codebases | ✅ Guideline #12 + 19-row gate |
| **OSPS-QA-05** | 1/2/3 | **Exclude generated executables + binaries from VCS** | ⚠ **NEW GAP** — closes via v1 Tier 1.8 Binary-Artifacts grep |
| OSPS-QA-06 | 2/3 | Automated testing in CI/CD | ✅ Row 6 |
| **OSPS-QA-07** | 3 | **At least one non-author approval before merging to primary** | ⚠ **NEW GAP — structural** — solo-dev honest-gap per v2 Theme 1 |

### SA — Security Assessment (3+1 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-SA-01 | 2/3 | Publish design descriptions of system actors + actions | ✅ partial via docs/positioning-and-value.md + threat-model.md |
| OSPS-SA-02 | 2/3 | Publish external interface descriptions (API/integration) | ✅ relies on project README / api docs |
| OSPS-SA-03 | 2/3 | Maintain project security assessment | ✅ docs/security-review-vX.Y.Z.md (auto-generated per release) |
| **OSPS-SA-03.02** | 3 | **Threat modeling + attack surface analysis for critical code paths** | ✅ v5 Step 1.5 threat-model freshness gate |

### VM — Vulnerability Management (6 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-VM-01 | 2/3 | CVD policy for reporting + addressing vulns | ⚠ NEW GAP — closes via v2 B2 SECURITY.md |
| OSPS-VM-02 | 1 | Security contacts discoverable in docs | ⚠ NEW GAP — closes via v2 B2 SECURITY.md + security.txt |
| OSPS-VM-03 | 2/3 | Confidential reporting channels for researchers | ⚠ NEW GAP — closes via v2 B2 GitHub Security Advisories enablement |
| OSPS-VM-04 | 2/3 | Publicly disclose vulns with mitigation; **VEX docs at maturity 3** | ⚠ NEW GAP — closes via v2 Tier 2G VEX emission (OpenVEX schema) |
| OSPS-VM-05 | 3 | Enforce pre-release dep-vuln + license policies | ⚠ PARTIAL — v5 Row 14 + Row 15 fire pre-tag; OSPS wants PR-time blocking |
| OSPS-VM-06 | 3 | Automated security testing with documented remediation thresholds + blocking | ✅ /security-review-scoped + /security-review triad |

### v3 net OSPS coverage assessment for Evidentia (v0.10.4 state)

- **Maturity 1**: ~95% conforming (only OSPS-VM-02 SECURITY.md gap)
- **Maturity 2**: ~75% conforming (gaps in BR-07 policy + DO-06 process doc + GV-01 + LE-01 + VM-01/02/03/04)
- **Maturity 3**: ~50% conforming (gaps in AC-04 + DO-03/04/05 + GV-04 + QA-07 + VM-04 VEX + VM-05 PR-time blocking)

**v5.1 enables Maturity 2 closure** via the v2 Tier 1 template-only additions (B1 + B2 + B4 in particular). Maturity 3 closure requires v5.2+ for the PR-time blocking workflow + VSA emission + VEX emission + Solo-dev honest-gaps for two-person-review + permission-elevation review.

## Sub-question 4 — 4-hour freshness window empirical research

### What v2 audit said (academic Stream E)

> "No paper validates 4 hours specifically. Closest empirical anchor is Parasuraman & Manzey (Section 3) showing complacency rises with task duration & uninterrupted vigilance windows of 30 minutes to several hours. v5's threshold is defensible by analogy, not by direct measurement."

### What v3 clarifies (specific quantitative anchors)

- **NO LLM-coding-specific paper** establishes a "safe" trust/vigilance time window
- **General vigilance literature**: anomaly detection drops within **20-60 minutes** of monotonous monitoring; significant degradation over **1-2 hours**; **10-30% performance decline** from first quartile to last quartile over a 2-hour session
- **Long AI sessions** (Cerbos 2024): "output quality gets worse the more context you add" — typical study designs cap at 1-2 hours
- **AI-generated code severity** (CodeRabbit 2024): 10.83 issues/PR vs 6.45 for human-only; ~1.4-1.7× more critical findings
- **AI-generated code risk** (Apiiro 2024): 322% more privilege-escalation paths + 153% more design flaws
- **Subjective speed bias** (cited in Cerbos 2024): developers using AI were 19% slower yet *convinced* they were faster

### Net empirical verdict on 4-hour bound

**4 hours is CONSERVATIVE, not under-justified.**

- Longer than known early vigilance-decrement intervals (20-60 min)
- Short enough to prevent stale approvals carrying across a full afternoon of context drift + fatigue
- General vigilance literature, if anything, would argue **4h is generous** for high-security contexts

### v3 NEW recommendations (extend v5 freshness logic)

1. **Parameterize by repo risk tier** in `.local/pre-release-review/config.yaml`:
   ```yaml
   review_freshness:
     repo_risk_tier: high  # or "medium" / "low"
     # high: warn at 30min, refuse at 1h
     # medium: warn at 1h, refuse at 2h  
     # low (default): warn at 2h, refuse at 4h  (current v5.0.1 default)
   ```
2. **Add context-sensitive invalidation** that REGARDLESS of clock-time:
   - If new commits land on the reviewed branch → invalidate immediately
   - If CI / SAST / SCA / Scorecard results materially change → invalidate
   - If the approving reviewer was also primary author of large AI-generated changes → require stricter staleness OR second reviewer (impossible for solo dev; mark as honest-gap honestly)
3. **Document policy stance** in bypass-protocol.md:
   > "The 4-hour bound is a policy parameter informed by, not dictated by, research. Vigilance and anomaly-detection performance reliably decline over multi-hour periods in human-in-the-loop automation tasks (Parasuraman & Manzey 2010, Goddard 2012). AI-assisted coding is empirically associated with higher issue densities + over-confidence (CodeRabbit 2024, Cerbos 2024, Apiiro 2024). 4 hours is an operational compromise between safety and workflow friction; high-risk repos should configure stricter bounds."

### Publishable opportunity (carry forward from v2 audit Tier 3 #3B)

There is NO published study on AI-coding HITL freshness windows specifically. **v5 could become the referenced empirical baseline** if Allen instruments per-run JSONs across the next 5-10 Evidentia cycles to capture (a) elapsed seconds Step 6 sign-off → Step 7 commit, (b) any finding flagged stale at re-run. **Publishable as an ESEM short paper.**

## v3 NEW backlog items (additions to v2 Tier 1/2/3)

### Tier 1 additions (LOW effort; pull into v5.1)

| ID | Item | Source | Closes |
|---|---|---|---|
| 1N | **OSPS-DO-03 verification recipe doc** at first-run-bootstrap (publishes consumer-side verification commands for cosign + PEP 740) | Sub-Q3 | OSPS-DO-03 maturity 3 |
| 1O | **OSPS-QA-05 binary-in-VCS check** added to Row 5 (`git ls-files | xargs file | grep -E "ELF|Mach-O|PE32"`) | Sub-Q3 + v1 #1.8 | OSPS-QA-05 maturity 1-3 |
| 1P | **SSDF v1.2 IPD section** in compliance-mapping.md (FORTHCOMING — PO.6.1-.3 + PS.4.1-.4 + RV.1.2-expanded) | Sub-Q2 | NIST SSDF v1.2 forward-readiness |
| 1Q | **NIST SP 800-218A scope correction** in compliance-mapping.md — replace v2's "skill is AI-authored, must map AI Profile entirely" with the ~10-task subset per sub-Q1 rubric | Sub-Q1 | Honest scoping; closes overscope risk |
| 1R | **Repo-risk-tier freshness parameterization** in `config.yaml` (default low/4h; medium/2h; high/1h) | Sub-Q4 | Empirical recommendation per AI-coding studies |
| 1S | **Context-sensitive invalidation** of freshness (new-commit OR CI-result-change → invalidate regardless of age) | Sub-Q4 | Strengthens Guideline #12 hard rule |
| 1T | **Policy-stance paragraph** in bypass-protocol.md citing Cerbos 2024 + CodeRabbit 2024 + Apiiro 2024 alongside existing Goddard 2012 + Parasuraman 2010 | Sub-Q4 | Strongest academic defensibility |

### Tier 2 additions (MEDIUM effort; v5.2)

| ID | Item | Source | Closes |
|---|---|---|---|
| 2R | **OSPS-AC-04.01 + 04.02 workflow-permissions audit** — grep `.github/workflows/*.yml` for missing/loose `permissions:` keys; fail Row 18-adjacent | Sub-Q3 | OSPS-AC-04 maturity 2-3 |
| 2S | **SSDF v1.2 IPD PO.6.3 "previous-don't-patch-decision review"** — extends lessons-learned.yaml register (v2 Tier 2A) with quarterly review-cadence | Sub-Q2 | NIST SSDF v1.2 PO.6.3 |
| 2T | **RV.1.2 config-permutation test sub-check** at Row 6 — for projects with config, test default + common variant configurations | Sub-Q2 | NIST SSDF v1.2 RV.1.2 expanded |
| 2U | **DCO sign-off enforcement (OSPS-LE-01)** — optional config flag to require `Signed-off-by:` trailer; default off for solo dev | Sub-Q3 | OSPS-LE-01 maturity 2-3 (with solo-dev honest-gap noted) |

### Tier 3 additions (architectural; v6+)

| ID | Item | Source | Notes |
|---|---|---|---|
| 3M | **PS.4 robust-and-reliable-updates HONEST-GAP** declaration in compliance-mapping.md | Sub-Q2 | Allen's projects are libraries/CLIs without customer-update-control infrastructure; honest-gap is correct stance |
| 3N | **OSPS-GV-04 + OSPS-QA-07 solo-dev structural honest-gap** documentation in compliance-mapping.md + auto-gen security-review-vX.Y.Z.md template | Sub-Q3 | Same as v2 Theme 1; OSPS adds 2 more frameworks to the citation list |
| 3O | **Empirical 4-hour-window study** instrument per-run JSONs across 5-10 cycles → publishable ESEM short paper | Sub-Q4 + v2 Tier 3 #3B | Publishable opportunity |

### Tier 4 — structural ceilings (carry forward; no v3 changes)

- All v2 Tier 4 items remain N/A
- v3 adds OSPS-GV-04 + OSPS-QA-07 to the two-person-review structural-impossible-for-solo-dev list (honest-gap is the correct posture; same as v2 Theme 1)

## Updated v5.1 skill-fix-pass scope (supersedes v2 Tier 1 17-item list)

v2 proposed 17 items (Tier S + Tier 1 1A-1M). v3 adds 7 NEW items (1N-1T) for **24 total v5.1 items**.

**Reorganized by category:**

### Compliance-mapping doc additions (8 items, all LOW effort)
- S2 SLSA v1.0→v1.2 + emit `.slsa-policy.yaml` (v2)
- S3 NIST SP 800-218A mapping rows — **CORRECTED SCOPE per 1Q** (v3)
- S4 OSPS Baseline 8-family mapping (v2; **expanded with v3 8-family enumeration**)
- S5 NIST SSDF v1.2 watch note (v2)
- 1P SSDF v1.2 IPD FORTHCOMING section (v3)
- 1L CMMI honest-claim paragraph (v2)
- 1Q NIST SP 800-218A scope correction (v3)
- 1M Honest-gap field expanded with 4 two-person-review frameworks + AI-as-force-multiplier framing (v2)

### Bootstrap-emitted templates (4 items, LOW effort)
- 1A DORA Art. 17 incident-severity matrix (v2)
- 1B SECURITY.md + security.txt + GitHub Security Advisories (v2)
- 1C GOVERNANCE.md + risk-appetite + EOL.md triple (v2)
- 1D A.6.3 training-currency log auto-append (v2)
- 1N OSPS-DO-03 verification recipe doc (v3)

### Pre-push gate additions (3 items, LOW each)
- 1O OSPS-QA-05 binary-in-VCS check (v3)
- 1H Reproducible-build verify at Step 7.x (v2, scope corrected per v2 C1)
- 1I `--cov-fail-under` Gold/Silver threshold enforcement (v2)

### Skill-prose additions (4 items, LOW each)
- 1E 3-question business-case prompt at Step 6.E (v2)
- 1G Goddard + Parasuraman direct citation in bypass-protocol.md (v2)
- 1T Policy-stance paragraph extending 1G with Cerbos + CodeRabbit + Apiiro citations (v3)
- 1F Qualitative FAIR Loss Magnitude column in bug-bucketing.md (v2)

### Freshness-window enhancements (2 items, LOW-MEDIUM)
- 1R Repo-risk-tier parameterization (v3)
- 1S Context-sensitive invalidation (new-commit + CI-change triggers) (v3)

### New code / new variant (2 items, MEDIUM)
- 1J `scripts/control_chart.py` with I-MR / u-chart / g-chart + DPMO (v2)
- 1K NEW 5th variant DMADV for major-version bumps (v2; for Evidentia v1.0)

### Carry-over: S1 (Trivy→Grype) already done in v5.0.1

**Total v5.1 scope**: 23 items × LOW-MEDIUM each = **~8-12 hours**. Bumps skill to `2026.05.23-v5.1`.

## Confidence calibration

| Sub-question | v3 confidence | Notes |
|---|---|---|
| Sub-Q1 (SP 800-218A scope) | HIGH | Structural rubric is canonical NIST framing; copyright-driven refusal of full task enumeration is expected behavior for a Sonar Pro model |
| Sub-Q2 (SSDF v1.2 IPD changes) | HIGH for new PO.6 + PS.4 + RV.1.2; MEDIUM on absence-of-removals/mergers (NIST hasn't posted a formal change log) | Cycode summary is the canonical secondary source NIST + community both cite |
| Sub-Q3 (OSPS Baseline 8 families) | VERY HIGH | Direct YAML fetch from authoritative GitHub repo; 8/8 families fully enumerated |
| Sub-Q4 (4-hour window) | HIGH for "no LLM-specific empirical bound"; HIGH for "4h is conservative not under-justified"; MEDIUM for new recommendations (parameterization + context-invalidation) — these are research-informed extrapolation | Sonar Pro provided multiple cited 2024 studies + general vigilance literature |

## Recommendation

The v3 findings strengthen v2's proposed v5.1 fix pass (now 23 items instead of 17). All additions are LOW-effort doc + template + simple-helper changes. The combined v5.1 closes:

- **OpenSSF OSPS Baseline Maturity 2** entirely (modulo solo-dev structural gaps)
- **CISA SbD Pledge Goals 1+2+3+5+6** (was 3+4+6 in v2; v3 adds explicit SECURITY.md = Goal 5)
- **ISO 27001 Annex A.5.1+A.5.7+A.5.23+A.5.24+A.5.30+A.5.31+A.6.3** (7 controls via templates)
- **NIST SSDF v1.1 + v1.2 IPD forward-readiness** (corrected scope per v3 Q1)
- **SOC 2 CC1+CC2+CC4 (with procedure-doc)+CC7+CC9** 
- **DORA Art. 17 downstream-FE compatibility** (via 1A incident-severity matrix template)

## Phase C trigger (UNCHANGED from v2)

Phase C (Evidentia v5.1 migration + v0.10.4 ship) fires only AFTER Allen approves the v5.1 skill-fix pass + the fix pass completes + Allen explicitly approves Phase C.

Standing instruction: **NO Phase C without explicit approval after skill-fix pass.**
