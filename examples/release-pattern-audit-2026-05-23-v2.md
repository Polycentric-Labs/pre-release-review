# Release-pattern audit v2 — /pre-release-review v5.0.1

**Date**: 2026-05-23 (re-run requested after Allen refilled Perplexity credits)
**Skill version audited**: `2026.05.23-v5.0.1`
**Method**: 6 parallel research streams launched at 21:04 UTC; all 6 returned within ~21 min.
**v1 baseline**: `release-pattern-audit-2026-05-23.md` (same day, WebFetch-only fallback)
**Allen's directive**: `release_pattern_audit_directive.md` (project memory)

## Tool-routing report (degradation persisted despite credit refill)

| Tool | v1 audit (pre-refill) | v2 streams (post-refill) | Working? |
|---|---|---|---|
| `mcp__openrouter-multimodal__chat_completion` (perplexity/sonar-deep-research) | broken (error) | **STILL BROKEN** — `Cannot read properties of undefined (reading '0')` — all 6 streams confirmed | NO |
| `mcp__perplexity-mcp__perplexity_research` (deep mode) | timing out | **TIMING OUT** at all reasoning_effort levels (MCP-32001 5-min ceiling) | NO |
| `mcp__perplexity-mcp__perplexity_reason` (medium effort) | working | **WORKING** — primary fallback used by Streams A/B/C/D | YES |
| `mcp__perplexity-mcp__perplexity_ask` (Sonar Pro short queries) | working | **WORKING** — used for fact-checks and citations | YES |
| `mcp__0307533e-...__paper_search` (HF Hub) | not exercised | **WORKING** — Stream E primary tool; 19 papers surfaced | YES |
| WebFetch / WebSearch | working | working | YES |

**Implication**: the OpenRouter route to `perplexity/sonar-deep-research` appears upstream-broken on Anthropic's MCP proxy and the credit refill did not fix it. **Recommend reporting to Anthropic + opening a defect with the openrouter-multimodal MCP maintainer.** For now, `perplexity_reason` + HF Hub `paper_search` are the working deep-research path. Stream coverage remained high despite the degradation.

## Executive summary

Six streams produced ~16,000 words of synthesized findings. **v2 surfaces 7 material corrections to v1 audit + 3 entirely-missed FINALIZED framework publications + ~25 NEW backlog items + 19 cited papers validating v5's most-novel mechanisms.** Net effect: v5's design is **academically and industrially well-grounded** (Goddard/Parasuraman directly validate the verbatim-bypass-phrase pattern; SLSA/OpenSSF/CISA/DORA all corroborate the cryptographic-provenance + governance-vacuum themes), but specific parameters (4-hour freshness, 3-of-3 verbatim phrases, 19 monolithic rows) are *defensible by analogy*, not yet *empirically calibrated*. Highest-leverage single addition: **DORA Art. 17 incident-severity matrix template** mapped to Commission Delegated Regulation (EU) 2024/1772 — closes downstream-FE-compatibility gap with a write-once template.

## v1 audit corrections (7 items where v1 was wrong)

| # | v1 claim | v2 correction | Source |
|---|---|---|---|
| C1 | "Reproducible build closes 4 frameworks: OpenSSF Silver+Gold, SLSA L3, S2C2F P6" | **Closes ONLY OpenSSF Gold + S2C2F P6.** SLSA v1.2 explicitly: hermetic/parameterless/reproducible builds NOT required at any level (incl. L3). Silver does not require `build_repeatable` (Gold does). | Stream A — https://slsa.dev/spec/v1.2/build-requirements |
| C2 | "Coverage 80% for Silver" | **Gold requires 90% statement + 80% branch**, not just 80%. v5.1 Tier 1.2 needs both thresholds to claim Gold; Silver is 80% statement alone. | Stream A — https://www.bestpractices.dev/en/criteria |
| C3 | "Two-person review cites OpenSSF Gold + ISO A.5.35" (2 frameworks) | **Cite 4 frameworks**: OpenSSF Gold + SLSA Source L4 + ISO A.5.35 + (likely) OSPS-AC. Broadens honest-gap defensibility. | Stream A |
| C4 | "Trivy claim unverified" | **CONFIRMED.** CVE-2026-33634 CVSS 9.4; PyPI `litellm`+`telnyx` also compromised; CISA KEV April 9 deadline. **Already migrated to Grype in v5.0.1**. | Stream F + WebSearch this turn |
| C5 | "gitsign for Source Track L1" (v1 Tier 3 #3.1) | **DOWNGRADE** — <6% developer adoption (arXiv 2604.14014); GitHub still won't show "Verified" badge (sigstore/gitsign#40 unresolved); v0.7.1 (2024) is latest release. **Recommend SSH-key signing instead** — wider GitHub recognition. | Stream F |
| C6 | "PRINCE2 1-question business-case prompt at Step 6.E" | **TOO THIN.** PRINCE2 7 "continued business justification" requires **3 questions**: value / viability / achievability. v5.1 Tier 1.4 should be 3-question or 1-question explicitly enumerating all three. | Stream D |
| C7 | "CC4 closable by between-release loop alone" | **Loop is technically sufficient but auditor-INSUFFICIENT.** SOC 2 CC4 expects PROCEDURE doc + remediation workflow + evidence storage in addition to the loop's technical artifact. | Stream B |

## NEW FINALIZED framework publications v1 missed (3)

| Framework | Status | Publication date | v5 impact |
|---|---|---|---|
| **NIST SP 800-218A (SSDF AI Profile)** | FINAL | July 26, 2024 | The skill is itself AI-authored. Must map. Adds PO.5.2.AI / PW.4.2.AI / PW.7.AI / RV.1.AI per Stream A. | (Stream A) https://csrc.nist.gov/pubs/sp/800/218/a/final
| **NIST SP 800-218r1 IPD v1.2** | IPD (public comment closed) | Dec 17, 2025 → Jan 30, 2026 | Final could land before Evidentia v0.10.5. v5.x compliance-mapping.md needs a "v1.2 final pending" watch note + re-audit at FINAL drop. | (Stream A) https://csrc.nist.gov/pubs/sp/800/218/r1/ipd
| **OpenSSF OSPS Baseline** | RELEASED | Feb 19, 2026 (v2026.02.19) | **Entirely new framework**; 8 control families (AC/BR/DO/GV/LE/QA/SA/VM), 3 maturity levels. v5 maps to ~12+ controls already (e.g., BR-04.01 = Row 17, BR-06.01 = Step 7.3/7.5). Adds VEX emission (VM-04.02) + PR-time auto-blocking (VM-05.03 + VM-06.02). | (Stream A) https://baseline.openssf.org/

**Plus 2 framework updates worth noting**:
- **ISO/IEC 27001:2022 Amendment 1:2024** — Climate-action integration (Stream B)
- **SLSA v1.0 → v1.2 (Approved)** — adds Source Track + VSA Approved (Stream A)

## v5 innovations validated by academic prior art (Stream E)

19 cited papers across 6 research areas. Strongest:

| v5 innovation | Academic validation | Citation |
|---|---|---|
| **Guideline #12 verbatim bypass phrases** | Forced cognitive engagement + accountability cues are the two consistent winners across 17 mitigation studies | **Goddard et al. 2012** — JAMIA 19(e1):e189-e197, DOI 10.1136/amiajnl-2011-000536 |
| **AI driver complacency at the v0.10.3 ship gate** | Exactly the failure mode predicted: complacency rises with task duration + repeated PASS results | **Parasuraman & Manzey 2010** — Human Factors 52(3), DOI 10.1518/001872010X12647080762611 |
| **`/security-review-scoped` per-subsystem wrapper** | Per-subsystem AI agents outperform whole-codebase SAST + LLM baselines | **Charoenwet et al. 2026** — arXiv:2601.19138 |
| **Mandatory `/security-review` triad at Steps 3/4/6** | Trust-first framing for AI software engineers requires analysis tools at LLM-agent boundaries | **Roychoudhury et al. 2025** — arXiv:2502.13767 |
| **Guideline #12 as policy-as-prompt** | Governance documents as runtime guardrails with HITL review is the prescribed pattern | **Kholkar & Ahuja 2025** — arXiv:2509.23994 |
| **doc-inventory.yaml + must_match_version** | "Outdated documentation" is the #1 cited developer pain point; tolerance is silent until misleading | **Lethbridge et al. 2003** + **Aghajani et al. ICSE 2020** |
| **project-shape detection across 10 langs** | Monorepo build-graph + per-target staleness is the canonical Google-scale precedent | **Potvin & Levenberg 2016** — CACM 59(7):78-87 |
| **publish-targets.yaml Step 7 verification** | Cryptographic refereed-delegation + RepOps for reproducibility | **Arun et al. 2025** — arXiv:2502.19405; **Lamb & Zacchiroli 2021** — arXiv:2104.06020 |
| **Step 6.E STOP boundary** | 5-layer architecture for high-stakes decisions (calibration-sequence + protection-architecture) | **Jadad 2025** — arXiv:2511.07669 |

**Items where empirical anchor is weak (publishable opportunities for v6)**:
- **4-hour freshness window** — no paper validates 4 hours specifically; defensible by analogy to Parasuraman vigilance-decline curves. **Recommendation E4** below: instrument across next 5 Evidentia cycles to calibrate.
- **DORA metrics for security review** — no published study covers MTTR/MTBF for AI-driven security; v5 already collects this passively. **Recommendation E2** below: publishable as ESEM short paper.

## 12 cross-stream themes (v1 had 10; v2 adds 5; closes 3)

**Carried forward from v1 (still valid)**:
- Theme 1: Two-person review gap (now cites 4 frameworks, not 2 — C3 above)
- Theme 2: Reproducible-build gap (scope corrected per C1 above — closes 2 frameworks not 4)
- Theme 3: Coverage threshold gap (Gold = 90% statement + 80% branch per C2)
- Theme 4: Between-release monitoring gap (must include procedure doc + remediation workflow per C7)
- Theme 5: Quantitative measurement gap (chart types now specified per Stream D)
- Theme 6: Lessons-learned register (now structured YAML schema per Stream C)
- Theme 7: Business-case freshness (3-question minimum per C6)
- Theme 8: Design-review checkpoint
- Theme 10: 8 publishable v5 innovations (carried forward + validated by Stream E)

**NEW v2 themes (5)**:
- **Theme 11 — Governance vacuum** (4 of 5 compliance frameworks): no `GOVERNANCE.md` / risk-appetite / role enumeration (Stream B + D)
- **Theme 12 — External communication channel** (4 of 5): no `SECURITY.md` / `security.txt` / GitHub Security Advisories enablement; v5 auto-gen security-review docs are internal-only (Stream B)
- **Theme 13 — Post-release/runtime monitoring** (5 of 5): every framework expects runtime observability; v5 stops at tag push (Stream B + Stream A OSPS-VM-05.03/06.02 PR-time blocking)
- **Theme 14 — Continuity / EOL / exit-strategy** (4 of 5): no `EOL.md` per project; DORA Art. 28 + SOC 2 CC9 require this (Stream B)
- **Theme 15 — Threat-intelligence consumption** (3 of 5): no documented intel-feed subscription + monthly review cadence (Stream B; ISO A.5.7 + DSOMM L4 Info Gathering + SOC 2 CC3)

**Closed by v5.0.1 already (3)**:
- Theme 9 (Trivy compromise) — migrated to Grype default in v5.0.1; Trivy retained as opt-in
- v1 Tier 1.6 (framework citations) — landed in maintenance.md this session
- v1 Tier 1.7 (v5 innovations doc) — landed in maintenance.md this session

## Re-prioritized backlog (v2 — supersedes v1's tier ranking)

### Tier S — Critical / time-sensitive (do as v5.0.1 or v5.1)

| ID | Item | Source | Effort |
|---|---|---|---|
| S1 | **Trivy → Grype migration** — DONE in v5.0.1 | Stream F + Web verify | (done) |
| S2 | **Bump SLSA citation v1.0 → v1.2 in compliance-mapping.md + emit `.slsa-policy.yaml`** — current spec is v1.2 Approved; v5 cites stale v1.0 | Stream A | LOW |
| S3 | **Add NIST SP 800-218A (AI Profile) mapping rows** — skill is AI-authored; must address | Stream A | LOW (doc) |
| S4 | **Add OSPS Baseline v2026.02.19 to compliance-mapping.md** — 8 control families, ~12 existing v5 features already conform; map them | Stream A | LOW-MEDIUM |
| S5 | **Skill-layer "v1.2 watch note"** — NIST SSDF v1.2 IPD comment-closed; final could drop before Evidentia v0.10.5 | Stream A | LOW (1 line) |

### Tier 1 — High impact / low effort (pull into v5.1; ~half-day to 1 day total)

| ID | Item | Source | Effort | Closes frameworks |
|---|---|---|---|---|
| 1A | **DORA Art. 17 incident-severity matrix template** mapped to CDR 2024/1772 (7-field schema; first-run-bootstrap emit) — **single highest-leverage item per Stream B** | Stream B | LOW | DORA Art. 17 + SOC 2 CC2/CC7 + ISO A.5.24/A.5.25 |
| 1B | **`SECURITY.md` + `security.txt` (RFC 9116) + GitHub Security Advisories enablement** at first-run-bootstrap, using CISA/FTC VDP sample text | Stream B | LOW | CISA Goal 5 + SOC 2 CC2 + ISO A.5.24 + DORA Art. 17 comms |
| 1C | **`GOVERNANCE.md` + risk-appetite paragraph + `EOL.md` triple** at first-run-bootstrap | Stream B + D | LOW-MEDIUM | ISO A.5.1+A.5.30 + SOC 2 CC1+CC9 + DORA Art. 5+28 + CISA Goal 1 indirect |
| 1D | **A.6.3 training-currency log** (`docs/sec-competence.md`) auto-append entry whenever `/security-review` fires | Stream B | LOW | ISO A.6.3 + SOC 2 CC1.4 |
| 1E | **3-question business-case prompt at Step 6.E** (value / viability / achievability per PRINCE2 7) | Stream D + C6 above | LOW | PRINCE2 + COBIT EDM02+EDM03 + PMBOK Stewardship |
| 1F | **Qualitative FAIR Loss Magnitude column** (NEGLIGIBLE/MINOR/MODERATE/SEVERE) in bug-bucketing.md — per-finding AND per-release-aggregated | Stream D | LOW | FAIR-Lite |
| 1G | **Cite Goddard 2012 + Parasuraman 2010 directly in `bypass-protocol.md`** — strengthens academic defensibility | Stream E E1 | LOW (1h) | HCI / automation-bias prior art |
| 1H | **Reproducible-build verification at Step 7.x** (second build + diff dist/) — corrected scope per C1: closes OpenSSF Gold + S2C2F P6 (NOT SLSA L3) | v1 Theme 2 + Stream A correction | LOW | OpenSSF Gold + S2C2F P6 |
| 1I | **`--cov-fail-under` enforcement on Row 6** — Gold tier needs 90% statement + 80% branch (Silver = 80% statement) | Stream A correction C2 | LOW | OpenSSF Silver + Gold |
| 1J | **`scripts/control_chart.py` with I-MR / u-chart / g-chart + DPMO** reading MEMORY.md SHIPPED entries | Stream D D1 (chart types specified) | MEDIUM (~3h) | Six Sigma Control + CMMI MPM/QPM-aligned |
| 1K | **DMADV variant for major-version bumps** — new 5th variant covering v0.10.x → v1.0 path | Stream D G-D23 | LOW-MEDIUM | Six Sigma DMADV + relevant for Evidentia v1.0 |
| 1L | **CMMI honest-claim paragraph** in maintenance.md ("ML3-with-ML4-style-quantitative-control"; never claim ML4 without SCAMPI) | Stream D D4 | LOW | CMMI |
| 1M | **Honest-gap field expanded** in security-review-vX.Y.Z.md template to cite 4 two-person frameworks (Gold + SLSA Source L4 + ISO A.5.35 + likely OSPS-AC) + 2025 Sloppish "AI is force-multiplier, not 2nd reviewer" framing | Stream A C3 + Stream C bonus C7 | LOW (template) | OpenSSF Gold + SLSA Source L4 + ISO A.5.35 + (likely) OSPS-AC |

### Tier 2 — Medium impact / medium effort (pull into v5.2 or v6)

| ID | Item | Source | Effort |
|---|---|---|---|
| 2A | **Lessons-learned YAML register** at `.local/pre-release-review/lessons-learned.yaml` with tags/severity/recurrence + Step 1.6 query helper | Stream C C1 | MEDIUM |
| 2B | **DoD base/extensions split** of 19-row gate — route by project-shape (e.g., container rows only fire when Dockerfile present) | Stream C C2 | MEDIUM |
| 2C | **Global WIP YAML + 4th bypass phrase `WIP LIMIT BYPASS — <reason>`** for cross-project concurrent reviews | Stream C C3 | LOW-MEDIUM |
| 2D | **Auto-generated VSM** at `docs/release-vsm.md` from per-run JSON timing data (extends 1J control-chart script) | Stream C C4 | MEDIUM |
| 2E | **Release Retrospective template** (pipeline-only) appended to release-checklist.md | Stream C C5 | LOW |
| 2F | **`release-policy.md` (Zachman Why@Business + TOGAF Architecture Contract)** — release rationale + risk appetite + roles + quality bar | Stream D D5 | LOW (1-pager) |
| 2G | **VEX document emission** at Step 7.x (OpenVEX schema) | Stream A OSPS-VM-04.02 | LOW-MEDIUM |
| 2H | **VSA (Verification Summary Attestation) emission** at Step 7.x per SLSA v1.2 spec | Stream A | LOW-MEDIUM (30 LOC Python) |
| 2I | **PR-time auto-blocking workflow** (OSPS-VM-05.03 + VM-06.02) — `.github/workflows/osps-baseline-gate.yml` from first-run-bootstrap | Stream A | MEDIUM |
| 2J | **Webhooks audit + Binary-Artifacts grep** as pre-push gate additions | Stream A + Stream F + v1 #1.8 | LOW |
| 2K | **CC4 procedure-doc + remediation-workflow stubs** alongside Theme 4 between-release loop (Tier 2 v1) | Stream B B5 | LOW-MEDIUM |
| 2L | **Threat-intel feed subscription doc** + Step 2 sub-check (ISO A.5.7) | Stream B Theme 15 | LOW |
| 2M | **Doc-erosion delta tracking** on Row 19 inspired by SlopCodeBench — track verbosity-delta + structural-erosion per inventory doc | Stream E E5 | MEDIUM (~2 days) |
| 2N | **ITIL 4 7-question Continual Improvement Model** for Quarterly variant | Stream D G-D12 | LOW |
| 2O | **ITIL Emergency-change variant** for hot-fix path | Stream D G-D11 | LOW |
| 2P | **TOGAF Phase H prompt** in Quarterly variant ("do we need to re-architect, not just refactor?") | Stream D G-D13 | LOW |
| 2Q | **Lead time vs cycle time split** in per-run JSON schema | Stream C bonus C6 | LOW |

### Tier 3 — Innovation / architectural (v6+)

| ID | Item | Source |
|---|---|---|
| 3A | **Step 7.11 dynamic-install scan via DySec eBPF pattern** | Stream E E3 — arXiv:2503.00324 |
| 3B | **DORA-for-security metrics auto-record** (MTTR / lead-time / change-failure-rate) — publishable ESEM short paper | Stream E E2 |
| 3C | **Empirically validate 4h freshness window** by instrumenting per-run JSONs over next 5 Evidentia cycles (passive collection) | Stream E E4 |
| 3D | **APO12 risk register** at `docs/risk-register.md` updated at Step 6 | Stream D G-D10 |
| 3E | **Kanban CFD-style metric** + flow efficiency calculation from per-run JSON | Stream C |
| 3F | **`harden-runner` (v2.19.4 confirmed maintained) as recommended (not optional)** for projects with untrusted workflow code | Stream F + v1 Tier 3 |
| 3G | **`gh attestation verify` for non-package binaries** at Step 7 | Stream F #3 |
| 3H | **GUAC v1.1.0 optional post-tag enrichment query** | Stream F #6 |
| 3I | **AI-driven event-driven design-doc stub** — Cursor Automations + DevOps Crew set the bar; v5.x is manual-driver-only | Stream F #10 |
| 3J | **gittuf for Source Track L3** when available as stable | Stream A |
| 3K | **release-please-action v3→v4 stability warning** + recommended pin doc | Stream F #4 |
| 3L | **Cosign v2.6.0 / Rekor v2 awareness in verification-gates.md** | Stream F #5 |

### Tier 4 — Concept-only / never (solo-dev structural limits)

- **CMMI ML4 formal claim** — requires SCAMPI appraisal + multi-project org-scale baselines (Stream D G-D3 + G-D4)
- **DSOMM L4 Culture & Organization** — assumes org-wide programs (Stream B)
- **DSOMM L5 entirely** — requires SOAR + fleet-wide risk scoring (Stream B)
- **DORA Art. 24 TLPT** — out-of-scope for OSS solo dev
- **ISO 9001 certification** — only `clause 6.1 risk-based thinking` is relevant pull (Stream D G-D20)
- **SOC 2 full-org closure** — narrow scope explicitly to "OSS release pipeline" (Stream B)
- **Two-person review SUBSTANTIVE compliance** — structurally impossible solo; honest-gap is correct path (Stream C + multiple sources)

## Recommended implementation order

**Stage 1 (v5.1 — ~1 day work)**: Tier S (S2-S5; S1 already done) + Tier 1 items 1A-1F + 1G-1I (LOW each). These are all template/doc/short-script changes. Closes ~18 framework gaps cumulatively + adds 1 new variant (1K) + closes 2 v1 corrections (C1+C2).

**Stage 2 (v5.2 — ~1 week)**: Remaining Tier 1 (1J-1M) + Tier 2 items 2A-2H. Mid-effort each. Establishes the lessons-learned + retrospective + VSM/VSA/VEX disciplines. Closes governance vacuum + continuity gap + external comms gap simultaneously.

**Stage 3 (v6 — quarter-scale)**: Tier 2 items 2I-2Q + select Tier 3. Architectural changes (PR-time blocking workflow, doc-erosion tracking, dynamic-install scan).

**Stage 4 (never)**: Tier 4 acknowledged as structural ceilings; document each as honest-gap in compliance-mapping.md.

## Audit hygiene checklist

- [x] All 6 streams completed within 21 minutes
- [x] Cross-stream consensus + contradictions identified
- [x] 7 v1 corrections surfaced + evidenced
- [x] 3 missed FINALIZED publications surfaced (NIST 800-218A, NIST SSDF v1.2 IPD, OSPS Baseline)
- [x] Academic-angle pass complete (19 papers, ~6 research areas)
- [x] Tool-routing degradation documented (OpenRouter sonar-deep-research broken + perplexity_research timing out)
- [x] All 5 v2 themes mapped to source frameworks with primary URLs
- [x] Re-prioritized backlog uses S/1/2/3/4 tiering consistent with v1 audit
- [x] Honest-gap items (CMMI ML4, DSOMM L5, etc.) flagged as Tier 4 not actionable
- [x] Publishable opportunities (R2 DORA-metrics, R4 4h-window validation) flagged for v6
- [ ] **Cost-benefit Loss-Magnitude ranking** — still qualitative; Tier 1.6/2.D Loss Magnitude column would enable this
- [ ] **Stream E peer-reviewer validation** — Goddard 2012 + Parasuraman 2010 should be cited in the skill itself before any external use of v5 as prior art (1G item)

## Phase C trigger (gated on Allen's explicit approval per standing instruction)

After Allen reviews this v2 audit, the natural next step is the **skill-fix pass** that lands Tier S + Tier 1 items 1A-1M as v5.1. Then Phase C executes the v5.1-against-Evidentia migration + v0.10.4 ship.

Skill-fix pass scope (if Allen approves):
- Tier S (4 items: S2-S5)
- Tier 1 (13 items: 1A-1M)
- 17 total file/template changes
- Estimated 6-10 hours
- Bumps skill to `2026.05.23-v5.1`

Allen's standing directive: **NO Phase C without explicit approval after skill-fix pass.**
