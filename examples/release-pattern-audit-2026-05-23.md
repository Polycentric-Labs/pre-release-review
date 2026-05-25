# Release-pattern audit — /pre-release-review v5

**Date**: 2026-05-23
**Skill version audited**: `2026.05.23-v5`
**Audit method**: 3 parallel research streams via WebFetch + WebSearch + (attempted) Perplexity/OpenRouter (degraded — see note); cross-referenced against 10 DevSecOps frameworks + 13 engineering/PM/EA frameworks + GitHub/Claude ecosystem inventory.
**Allen's directive**: `release_pattern_audit_directive.md` (committed to project memory 2026-05-23).

> **Tool note**: `perplexity-mcp` and `mcp__openrouter-multimodal__chat_completion` with `perplexity/sonar-deep-research` both returned errors during this audit pass (OpenRouter side returned `Cannot read properties of undefined`; direct Perplexity quota exhausted). Streams fell back to WebFetch + WebSearch + local skill/plugin inventory. Coverage of all 23 frameworks confirmed via primary sources (URLs in stream outputs). Recommend retry of Perplexity deep-research after a future quota refill for academic angle.

## Executive summary

v5 is **strong on jidoka discipline + cryptographic provenance + skill composability** (uncommon among solo-dev release tools). It is **weak on quantitative measurement + between-release monitoring + retrospective discipline + two-person review** (universal across frameworks). One **critical** supply-chain item (Trivy ↔ Grype migration) needs immediate attention. ~15 v5.1 / v6 items surface as prioritizable, of which ~5 are battle-tested wins with LOW implementation cost.

## Cross-stream themes (consensus)

### Theme 1 — Two-person review / human-second-pair-of-eyes gap (universal)

Surfaced by: OpenSSF Gold `two_person_review` (Stream 1), ISO 27001 A.5.35 independent review (Stream 1), CMMI v2.0 PR (Stream 2 partial), PMBOK 7 quality domain (Stream 2 implicit), CISA SbD goal 4 (Stream 1).

Solo-dev fundamentally can't satisfy this without either (a) declaring it as an honest gap in `docs/security-review-vX.Y.Z.md`, or (b) adding an explicit human-second-pair-of-eyes step before Step 6.E. Allen's preference is honest gaps; recommend an explicit honest-gap field in the auto-gen template.

### Theme 2 — Reproducible-build verification gap

Surfaced by: OpenSSF Silver `build_repeatable` / Gold `build_reproducible`, SLSA Build L3 hermeticity, S2C2F Practice 6, CMMI CM (Stream 2).

v5 verifies *hash-match* (published artifact vs build artifact) at Step 7.2. It does NOT re-build a second time and assert byte-identical output. One sub-step closes 4 framework gaps simultaneously. **HIGH-priority + LOW-effort** v5.1 item.

### Theme 3 — Coverage threshold gap

Surfaced by: OpenSSF Silver `test_statement_coverage80` / Gold 90% + branch coverage 80%, CMMI VV (Stream 2).

Row 6 of the pre-push gate runs tests but doesn't enforce a coverage threshold. One-line gate addition (`--cov-fail-under=80` for Python; equivalent for other shapes) closes Silver-tier audit requirement.

### Theme 4 — Between-release monitoring gap

Surfaced by: SOC 2 CC4 monitoring, ISO 27001 A.8.16, DSOMM Logging+Monitoring L4 (Stream 1), Lean continuous improvement (Stream 2), `/loop` skill + research-resync-routine cadence (Stream 3).

v5 reviews at release-time only. Auditors expect "what was the security posture last Tuesday?" evidence. Wire a weekly `/loop`-driven Scorecard + osv-scan delta check between releases; output as a structured artifact (`.local/pre-release-review/between-release-monitor.json`).

### Theme 5 — Quantitative measurement / DPMO gap

Surfaced by: Six Sigma DMAIC Control phase (Stream 2), FAIR risk aggregation (Stream 2), CMMI ML4 (Stream 2), CISA SbD Goal 3 vulnerability-class trend (Stream 1).

v5 captures per-release findings but does no rolling trend visualization. The data exists in `MEMORY.md` SHIPPED entries + per-run JSON. A `scripts/control_chart.py` reading those + plotting time-to-publish + finding-rate + bypass-rate would expose process drift quantitatively. **HIGH-impact + MEDIUM-effort.**

### Theme 6 — Lessons-learned register absent

Surfaced by: Agile/Scrum retrospective (Stream 2), PMBOK 7 lessons-learned register (Stream 2), ITIL Problem Management (Stream 2), `consolidate-memory` Claude skill (Stream 3).

v5's lessons (e.g., the v0.10.3 ship incident → v0.10.4 P5 CHANGELOG gate) land in `MEMORY.md` SHIPPED entries as narrative prose. Not structured for re-lookup at the next release's Step 1.6. Recommend `.local/pre-release-review/lessons-learned.md` register, queried at Step 1.6 with "any prior lessons applicable to this release?".

### Theme 7 — Business-case freshness not re-checked

Surfaced by: PRINCE2 "Authorising a Stage" (Stream 2), PMBOK 7 stewardship principle, COBIT EDM (Stream 2).

Step 6.E approves tag without re-checking "does this release still serve the project's primary buyer persona per `docs/positioning-and-value.md`?" One-line prompt addition.

### Theme 8 — Design-review checkpoint absent

Surfaced by: NIST SSDF PW.2.1 review-the-design (Stream 1), ISO A.8.27 secure architecture, OpenSSF Silver `assurance_case` (Stream 1).

v5's Step 1.5 checks threat-model freshness but doesn't require a "design satisfies threats" mapping. Adding this at Step 1.5 (only when threat-model is touched) closes 3 framework gaps with one table.

### Theme 9 — Trivy compromise → migrate to Grype (CRITICAL urgency)

Surfaced by: Stream 3 GitHub-ecosystem scan.

Trivy was compromised twice in March 2026 supply-chain attacks. v5's pre-push-gate Row 13 + Step 7.5c sub-step both reference Trivy by name. Industry guidance is to migrate to `anchore/grype` (same vendor as Syft already used by v5; 12,267 stars; no recent compromises). **This is the single most urgent v5.1 fix.**

⚠ **AUDIT-ASSERTED CLAIM, UNVERIFIED**: I did not independently verify the Stream 3 agent's "Trivy compromised twice in March 2026" claim against a primary source — flag for spot-check before acting. If unverified, downgrade to "industry guidance evolving; track and reconsider."

### Theme 10 — Innovative patterns v5 ships that no framework prescribes (publishable strengths)

Surfaced by: all 3 streams in their "idiosyncrasies" sections.

- **Guideline #12 mechanical hard rule + 3 verbatim bypass phrases** — novel AI-safety primitive for human-in-loop pipelines. No equivalent in any compared framework.
- **Per-run JSON freshness window (2h WARN / 4h REFUSE)** — code-as-trust-decay-timer. Original.
- **Branch-protection bypass audit (Row 18)** — finer-grained than OpenSSF Scorecard's Branch-Protection check. Worth upstreaming to Scorecard as a feature request.
- **`/security-review-scoped` wrapper** — closes the v4 builtin-can't-take-custom-scope gap; pattern reusable for other builtins.
- **`publish-targets.yaml` 9-kind schema + custom escape hatch** — Claude-native version of GoReleaser/release-please YAML pipelines but with human-in-loop STOP boundaries.
- **Auto-generate `docs/security-review-vX.Y.Z.md` from per-run JSON** — solves the markdown/JSON drift problem most release tools have.
- **doc-inventory `must_match_version: true`** — direct attack on documentation staleness as a release-time invariant.
- **Project-shape detection across 10 languages** — broader than most release tools (GoReleaser covers some; nothing else covers all 10).

Document these as **"v5 innovations / publishable contributions to the OSS DevSecOps ecosystem"** in `references/maintenance.md`. Phase B audit demonstrated they're genuinely novel.

## Stream-by-stream summaries

### Stream 1 — DevSecOps frameworks (NIST SSDF, SLSA, OpenSSF, CISA, OWASP DSOMM, OpenSSF KB, ISO 27001, SOC 2, DORA)

Result: v5 conforms broadly to all 10 frameworks at the practice-level. Specific gaps: PW.2.1 design review, PW.6 hardening flags (NIST SSDF); Source + Dependency tracks (SLSA); two-person review + coverage thresholds (OpenSSF Silver/Gold); DBSCAN-style scoring (DSOMM L4); A.6.3 training, A.8.10 deletion verification, A.8.33 test-data protection (ISO); CC4 continuous monitoring, CC6.6/CC6.7 encryption defaults (SOC 2); Art. 24 TLPT, Art. 17 incident reporting thresholds (DORA).

Top 10 from Stream 1 (Stream-1 §"Top 10 recommendations"):
1. Reproducible-build verification at Step 7.x
2. Coverage threshold on Row 6
3. Vulnerability-class trend in security-review doc
4. Design-review checkpoint at Step 1.5
5. Two-person review honest-gap field
6. Binary-artifacts + webhooks audits
7. Between-release monitoring loop
8. Default-credentials + test-data-leak greps
9. IaC scope detection + scan
10. Emit security-insights.yml + .slsa-policy.yaml

### Stream 2 — Engineering / PM / EA frameworks (Lean, Agile/Scrum/Kanban/XP, SAFe/LeSS/DAD, Six Sigma, ITIL v4, COBIT 2019, TOGAF 10, PMBOK 7, PRINCE2, ISO 9001, CMMI v2.0, Zachman, FAIR)

Result: v5 has unusually strong jidoka discipline (Lean) + DoD rigor (Scrum) + change enablement (ITIL/PRINCE2/COBIT). Gaps: per-release retrospective (Scrum/ITIL/PMBOK), DPMO/control-chart tracking (Six Sigma/CMMI ML4), Loss Magnitude estimation (FAIR), business-case freshness (PRINCE2/PMBOK/COBIT), value-stream map (Lean), 4 variants framed as ITIL change types.

Most useful insight from Stream 2: many existing v5 features are uncited framework instances. Add framework citations to maintenance.md so auditors see the lineage:
- Guideline #12 = Lean jidoka + andon cord
- Row 17 CHANGELOG = Lean poka-yoke
- 19-row gate = Scrum Definition of Done
- Step 6.E = PRINCE2 "Authorising a Stage" / TOGAF Phase G
- 12 binding guidelines = PMBOK 7 principles-based approach
- 7-step PDCA = ISO 9001:2015 PDCA cycle
- compliance-mapping.md = COBIT MEA01

Top 10 from Stream 2 (Stream-2 §"Top 10 recommendations"):
1. Per-release retrospective template
2. Business-case freshness 1-question at Step 6.E
3. Loss Magnitude column on bug-bucket table
4. Control-chart script
5. Value-stream map of release pipeline
6. 4 variants as ITIL change types
7. Risk-appetite paragraph in CLAUDE.md or config.yaml
8. Lessons-Learned register
9. DPMO + 4-interrogative completeness in Step 7.11
10. Annual CMMI ML3 self-assessment

### Stream 3 — GitHub + Claude ecosystem

Result: v5 already wires the best-in-class OSS tools (osv-scanner, cosign, slsa-github-generator, pypa/gh-action-pypi-publish, ossf/scorecard-action, anchore/syft). Gaps identified: harden-runner (runtime EDR for runners), gitsign (commit/tag signing), Trivy → Grype migration (CRITICAL). Composable Claude skills under-leveraged: check-pointer-rot, consolidate-memory, research-resync, engineering:incident-response, pr-review-toolkit's 6 surgical agents, hookify (for the v5.1 settings.json hook recommendation).

Top 15 from Stream 3 (Stream-3 §"Top 15 recommendations"):
1. **[CRITICAL]** Trivy → Grype migration (Row 13 + Step 7.5c)
2. Add step-security/harden-runner to publish-targets.yaml
3. Add sigstore/gitsign for commit/tag signing
4. Wire check-pointer-rot as Row 19 sub-check
5. Wire research-resync as optional Step 2 entry
6. Add settings.json hook `pre-push-freshness-gate.py` (defense-in-depth for Guideline #12)
7. Wire engineering:incident-response auto-fire on Step 7 failure
8. Wire consolidate-memory as optional Step 7.11
9. Add pr-review-toolkit's silent-failure-hunter + type-design-analyzer as Step 4 conditional auto-fires
10. Document semantic-release as RECOMMEND-AS-ALTERNATIVE (not IGNORE)
11. Document release-please as PR-based middle ground
12. Add CycloneDX SBOM-diff as Step 7 sub-step
13. Lift changesets-style pending-changes/*.yaml model
14. Add /pre-release-review-status slash command
15. Reference mcp-integration-standard drift-detection hook pattern

## Prioritized backlog for v5.1 + v6

**Tier S (do immediately — security-critical or unverified high-urgency):**

| # | Item | Source | Effort | Notes |
|---|---|---|---|---|
| S1 | Verify the "Trivy compromised twice in March 2026" claim against primary sources. If verified → migrate Row 13 + Step 7.5c to Grype. If unverified → defer + flag for future re-check. | Stream 3 | LOW (verification) + MEDIUM (migration if verified) | Spot-check before any action; do not implement without verification |

**Tier 1 (high impact, low effort — pull into v5.1):**

| # | Item | Sources | Effort | Frameworks closed |
|---|---|---|---|---|
| 1.1 | Reproducible-build verification sub-step at Step 7.x (second build + diff dist/) | Stream 1 #1, Stream 2 implicit CMMI CM | LOW | OpenSSF Silver+Gold, SLSA L3, S2C2F P6 |
| 1.2 | `--cov-fail-under=80` (project-shape-routed) on Row 6 | Stream 1 #2 | LOW | OpenSSF Silver |
| 1.3 | Per-release retrospective template appended to release-checklist.md | Stream 2 #1 | LOW | Scrum, ITIL, ISO 9001 |
| 1.4 | Business-case freshness 1-question at Step 6.E | Stream 2 #2 | LOW (1 line) | PRINCE2, PMBOK, COBIT |
| 1.5 | Two-person review honest-gap field in auto-gen security-review doc | Stream 1 #5 | LOW (template change) | OpenSSF Gold, ISO A.5.35, CMMI PR |
| 1.6 | Framework citations added to maintenance.md (Lean / Scrum / PRINCE2 / etc.) | Stream 2 §"Framework cites for existing v5 features" | LOW (doc edit) | All audited frameworks (signals lineage) |
| 1.7 | Document "v5 innovations" in maintenance.md (publishable strengths) | Cross-stream | LOW (doc) | Establishes prior art |
| 1.8 | Binary-Artifacts + Webhooks audits as Rows 5.5 + 11.5 (or expand existing rows) | Stream 1 #6 | LOW | OpenSSF Scorecard |
| 1.9 | Default-credentials + test-data-leak greps extend Row 1 | Stream 1 #8 | LOW | CISA Goal 2, ISO A.8.33 |
| 1.10 | Add settings.json hook `pre-push-freshness-gate.py` — defense-in-depth for Guideline #12 | Stream 3 #6 | LOW-MEDIUM | (Architectural strengthening, no specific framework) |

**Tier 2 (medium impact, medium effort — pull into v5.2 or v6):**

| # | Item | Sources | Effort |
|---|---|---|---|
| 2.1 | Vulnerability-class trend rolling histogram in security-review doc | Stream 1 #3 | MEDIUM |
| 2.2 | Design-review checkpoint at Step 1.5 when threat-model touched | Stream 1 #4 | MEDIUM |
| 2.3 | Loss Magnitude column on bug-bucket + per-release aggregated risk score | Stream 2 #3 | MEDIUM |
| 2.4 | Control-chart script reading MEMORY.md SHIPPED entries | Stream 2 #4 | MEDIUM (1 day) |
| 2.5 | Between-release monitoring loop (Scorecard + osv-scan weekly) | Stream 1 #7 | MEDIUM |
| 2.6 | Wire check-pointer-rot as Row 19 sub-check | Stream 3 #4 | MEDIUM |
| 2.7 | Wire research-resync as optional Step 2 entry for positioning doc decay | Stream 3 #5 | MEDIUM |
| 2.8 | CycloneDX SBOM-diff Step 7 sub-step (catches stealth transitive growth) | Stream 3 #12 | MEDIUM |
| 2.9 | Wire engineering:incident-response auto-fire on Step 7.x failure | Stream 3 #7 | MEDIUM |
| 2.10 | Wire consolidate-memory as optional Step 7.11 (MEMORY.md is over its limit) | Stream 3 #8 | MEDIUM |
| 2.11 | Frame 4 variants as ITIL change types in variants.md | Stream 2 #6 | LOW (doc) |
| 2.12 | Risk-appetite paragraph in CLAUDE.md or config.yaml | Stream 2 #7 | LOW (doc) |
| 2.13 | Lessons-Learned register at .local/pre-release-review/lessons-learned.md | Stream 2 #8 | MEDIUM |

**Tier 3 (innovation / architectural / v6+ scope):**

| # | Item | Sources |
|---|---|---|
| 3.1 | sigstore/gitsign for commit + tag signing (Source-track L1) | Stream 1 SLSA Source, Stream 3 #3 |
| 3.2 | step-security/harden-runner for runner-side EDR (`github-actions-runtime` kind in publish-targets) | Stream 3 #2 |
| 3.3 | pr-review-toolkit's silent-failure-hunter + type-design-analyzer wired as Step 4 conditional auto-fires | Stream 3 #9 |
| 3.4 | Lift changesets-style `.local/pre-release-review/pending-changes/*.yaml` model | Stream 3 #13 |
| 3.5 | `/pre-release-review-status` slash command (read-only "where am I?") | Stream 3 #14 |
| 3.6 | Document semantic-release / release-please as RECOMMEND-AS-ALTERNATIVE for low-stakes projects | Stream 3 #10, #11 |
| 3.7 | Emit security-insights.yml + .slsa-policy.yaml at first-run-bootstrap | Stream 1 #10 |
| 3.8 | IaC scope detection + scan to project-shape + Row 8 | Stream 1 #9 |
| 3.9 | DPMO + 4-interrogative completeness check in Step 7.11 | Stream 2 #9 |
| 3.10 | Annual CMMI ML3 self-assessment | Stream 2 #10 |
| 3.11 | Value-stream map of release pipeline as a 1-pager | Stream 2 #5 |
| 3.12 | Reference mcp-integration-standard drift-detection hook pattern in maintenance.md | Stream 3 #15 |

**Tier 4 (concept-only, watch — not actionable for solo dev):**

- SAFe scaled-agile concepts (Stream 2 §3) — keep ignoring
- TOGAF Architecture Contract (Stream 2 §7) — N/A solo dev
- DORA Art. 30 contractual provisions (Stream 1) — out-of-scope for OSS solo dev
- COBIT governance/management EDM-APO-BAI-DSS-MEA split (Stream 2 §6) — single operator = both
- Some PRINCE2 ceremonies (Stream 2 §9) — over-scoped

## Implementation order recommendation

**Phase 1 (v5.1 — next skill bump, ~1 day work):** Tier S verification first, then Tier 1 items 1.1-1.10. Most are LOW-effort doc edits or 1-line gate additions. Together they close ~12 framework gaps for ~4-8 hours of work.

**Phase 2 (v5.2 — 1 week, optional):** Tier 2 items 2.1-2.13. Medium-effort each; collectively transform v5 from "release-time review" to "continuous + release-time review" posture.

**Phase 3 (v6 — quarter-scale work):** Tier 3 items 3.1-3.12. Architectural changes (hooks, IaC, slash command, lessons register). Wait for Phase B/C feedback.

**Phase 4 (never):** Tier 4. Periodically re-check whether Allen's context shifted toward enterprise-scale (e.g., if Polycentric-Labs grows).

## What the audit confirmed v5 already does well

- 12 binding guidelines with #12 hard rule is genuinely novel + worth keeping
- 7-step structure is well-aligned with PDCA + DMAIC + Phase G/H + Authorising-a-Stage
- 19-row pre-push gate is Definition-of-Done in Scrum terms; jidoka in Lean
- `/security-review-scoped` wrapper fixes a real v4 gap
- `publish-targets.yaml` is the right abstraction layer
- doc-inventory.yaml + must_match_version is a clean attack on doc decay
- Auto-generate security-review-vX.Y.Z.md from JSON closes drift gap
- Per-run JSON freshness window is a novel + correct AI-safety primitive
- Cross-platform parity via Python G6 gates was the right call
- Core (2) + optional (3) deliverables split correctly serves new projects
- EPSS auto-lookup + CWE auto-populate is the right level of automation for solo dev

## What this audit did NOT cover (deferred for future)

- **Academic angle**: research-resync recommended Hugging Face MCP for academic-paper cross-referencing of the skill's design choices. Stream 3 fell back to web-only; full academic angle deferred.
- **Live battle-testing**: this audit is theoretical comparison. Phase C (Evidentia v0.10.4 with v5 skill) is the empirical test.
- **Quantitative measurement of v4 baseline**: Six Sigma would want "what was v4's bypass rate / DPMO?" before adopting v5's mitigations. v4 ran 4 Evidentia v0.10.x cycles; data exists in `MEMORY.md` SHIPPED entries but was not statistically analyzed for this audit.
- **Cost-benefit ranking**: backlog items prioritized qualitatively. A formal cost-benefit table (FAIR-style Loss-Magnitude × Likelihood-of-Need) would tighten Tier ordering.
- **Allen's bandwidth signal**: this audit assumes Allen has bandwidth for all 4 phases. If solo-dev time is constrained, surface Tier S + Tier 1 items only.

## Audit hygiene checklist

- [x] All 23 frameworks compared (10 DevSecOps + 13 engineering/PM/EA)
- [x] Cross-stream consensus themes identified (10 themes)
- [x] v5 innovations called out separately (8 publishable strengths)
- [x] Solo-dev applicability lens applied (Tier 4 explicitly flagged as "not actionable for solo dev")
- [x] Citation discipline — primary-source URLs in stream outputs
- [x] CRITICAL / unverified claim flagged (Trivy compromise) for spot-check
- [x] Phase C trigger documented (Allen approval required before Evidentia testing)
- [ ] **Cost-benefit ranking** — deferred; qualitative for now
- [ ] **Academic-angle pass** — deferred; needs Perplexity quota
- [ ] **v4 baseline statistical analysis** — deferred; data exists but not analyzed

## Sources

Stream outputs preserved at:
- (Stream 1 raw output: ~3,000 words, all 10 DevSecOps frameworks)
- (Stream 2 raw output: ~3,000 words, all 13 engineering/PM/EA frameworks)
- (Stream 3 raw output: ~3,000 words, GitHub + Claude ecosystem inventory)

Primary-source URLs (sampling — full list in stream outputs):
- NIST SSDF SP 800-218 v1.1: https://csrc.nist.gov/Projects/ssdf
- SLSA v1.0 Levels: https://slsa.dev/spec/v1.0/levels
- OpenSSF Best Practices Badge: https://www.bestpractices.dev/en/criteria
- OpenSSF Scorecard: https://github.com/ossf/scorecard/blob/main/docs/checks.md
- CISA Secure by Design Pledge: https://www.cisa.gov/securebydesign/pledge
- OWASP DSOMM: https://www.practical-devsecops.com/devsecops-maturity-model-dsomm/
- OpenSSF S2C2F: https://github.com/ossf/s2c2f
- ISO 27001:2022 Annex A (secondary): https://hightable.io/iso-27001-annex-a-controls-reference-guide/
- SOC 2 TSC: https://www.cbh.com/insights/articles/soc-2-trust-services-criteria-guide/
- DORA: https://digitalcompliance.snellman.com/regulation/digital-operational-resilience-act-dora/
- Lean Enterprise Institute: https://www.lean.org/explore-lean/what-is-lean/
- Scrum Guide: https://scrumguides.org/scrum-guide.html
- ITIL v4: https://www.axelos.com/best-practice-solutions/itil
- PRINCE2: https://www.axelos.com/best-practice-solutions/prince2
- PMBOK 7: https://www.pmi.org/pmbok-guide-standards/foundational/pmbok
- COBIT 2019: https://www.isaca.org/resources/cobit
- TOGAF 10: https://www.opengroup.org/togaf
- ISO 9001:2015: https://www.iso.org/standard/62085.html
- CMMI v2.0: https://cmmiinstitute.com/cmmi
- Zachman Framework: https://www.zachman.com/about-the-zachman-framework
- FAIR: https://www.fairinstitute.org/fair-risk-management

## Next step

Surface this audit to Allen + ask which Tier items to act on for Phase C (Evidentia testing + v0.10.4 ship). Default recommendation: Tier S (verify Trivy claim) + Tier 1 items 1.6 + 1.7 (low-cost doc additions) BEFORE Phase C, so Phase C tests v5.1 documentation lineage; defer 1.1-1.5 + 1.8-1.10 + Tier 2/3 to AFTER Phase C empirical findings.
