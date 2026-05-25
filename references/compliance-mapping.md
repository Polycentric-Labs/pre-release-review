# Compliance framework mapping (G15 — expanded in v4)

Each pre-release-review step maps to ≥ 1 control across 6 frameworks.

## Per-step mapping

| Skill step | NIST SSDF v1.1 | SLSA v1.0 | OpenSSF Scorecard | CISA Pledge | ISO 27001:2022 | SOC 2 Type II | DORA |
|---|---|---|---|---|---|---|---|
| 1 (process review + scope) | PO.1, PO.5 | — | — | Goal 1 | A.5.1, A.5.4 | CC1.1, CC1.4 | Art. 5 |
| 2 (positioning) | PO.4 | — | — | — | A.5.31 (continual improvement) | CC1.5 | — |
| 3 (commit re-test + /security-review #1 + /code-review) | PS.1, PS.3, PW.4 | Build L2 | Code-Review, SAST | Goal 4 (transparency) | A.8.25, A.8.28, A.8.29 | CC7.1, CC7.2 | Art. 8, 9 |
| 4 (capability matrix + /security-review #2 + DAST) | PW.7, PW.8 | — | Fuzzing, SAST | Goal 4 | A.8.29 | CC7.1, CC7.4 | Art. 24 |
| 5.A (MEDIUM fix bundle) | PW.5 | — | — | — | A.8.28 | CC8.1 | — |
| 5.B (vN+1 plan) | PO.5 | — | — | — | A.5.1 | CC1.4 | — |
| 5.C (CHANGELOG + ROADMAP) | PO.4 | — | — | Goal 4 | A.5.31 | CC1.5 | — |
| 6.A (release-checklist) | PO.5, PS.3 | Build L1+ | Maintained | Goal 1, 2 | A.8.32 | CC8.1 | Art. 16, 17 |
| 6.C (final gate + /security-review #3 + 19-row pre-push) | PS.3, PW.5, PW.7 | Build L3, Provenance L3 | Pinned-Dependencies, Token-Permissions, Signed-Releases, License | Goal 4 | A.8.25, A.8.27, A.8.28 | CC7.1, CC7.2, CC8.1 | Art. 9, 24, 28 |
| 6.E (tag + push) | PS.2, PS.3 | Provenance L3 | Signed-Releases | Goal 4 | A.8.32 | CC8.1 | Art. 16 |
| **7 (post-tag verification, NEW)** | PS.3.1 | Provenance L3 verify | Signed-Releases verify | Goal 1, 4 | A.8.27, A.8.32 | CC7.1, CC8.1 | Art. 24, 28 |

## Per-G-change framework alignment

| v4 change | Frameworks satisfied |
|---|---|
| G1 (Step 7 post-tag) | NIST SSDF PS.3.1, SLSA Provenance L3 verify, ISO 27001 A.8.32 |
| G2 (SBOM hardening) | NIST SSDF PS.3, CISA Pledge Goal 4, ISO 27001 A.8.27, DORA Art. 28 |
| G3 (container CVE scan) | NIST SSDF PW.4, OpenSSF Scorecard Vulnerabilities, ISO 27001 A.8.8 |
| G4 (license/SCA) | NIST SSDF PW.4, OpenSSF Scorecard License, ISO 27001 A.5.32 |
| G5 (threat model) | CISA Pledge Goal 1, OpenSSF Best Practices Silver, ISO 27001 A.5.7, A.8.27 |
| G6 (verification gates) | NIST SSDF RV.2, ISO 27001 A.8.34, SOC 2 CC7.5 |
| G7 (CVSS/CWE/EPSS) | NIST SSDF PW.5, ISO 27001 A.8.27, SOC 2 CC7.1 |
| G8 (vuln aging SLO) | CISA Pledge Goal 1 (timelines), DORA Art. 24 |
| G9 (secret rotation) | NIST SSDF PO.5, ISO 27001 A.5.17 (cryptography), SOC 2 CC6.1 |
| G10 (reproducible builds) | SLSA Build L3, NIST SSDF PS.3, ISO 27001 A.8.31 |
| G11 (DAST) | OpenSSF Scorecard Fuzzing, NIST SSDF PW.8, DORA Art. 24 |
| G12 (/security-review 3x) | NIST SSDF PW.7, OpenSSF Scorecard SAST, ISO 27001 A.8.29 |
| G13 (run logs) | NIST SSDF PO.5, ISO 27001 A.8.15 (logging), SOC 2 CC7.2 |
| G14 (skill split) | n/a (architecture only) |
| G15 (this doc) | n/a (meta-mapping) |
| **v5 G16 (Guideline #12 push-gate hard rule)** | NIST SSDF PO.5, ISO 27001 A.5.1, SOC 2 CC1.4, CISA Pledge Goal 1 |
| **v5 G17 (project-shape detection + portability)** | n/a (architecture; enables consistent control coverage across project types) |
| **v5 G18 (first-run bootstrap)** | NIST SSDF PO.4, ISO 27001 A.5.31, SOC 2 CC1.5 |
| **v5 G19 (`/security-review-scoped` wrapper)** | NIST SSDF PW.7, OpenSSF Scorecard SAST, ISO 27001 A.8.29 (catches what v4 was unable to enforce) |
| **v5 G20 (publish-targets.yaml driving Step 7)** | SLSA Provenance L3 verify (per kind), NIST SSDF PS.3.1, ISO 27001 A.8.32 |
| **v5 G21 (doc-inventory + freshness gate Row 19)** | NIST SSDF PO.4, ISO 27001 A.5.31 (documented + current), SOC 2 CC1.5, OpenSSF Best Practices Silver |
| **v5 G22 (branch-protection bypass audit Row 18)** | NIST SSDF PO.5 (process integrity), ISO 27001 A.5.15 (access control), SOC 2 CC6.1, DORA Art. 5 |
| **v5 G23 (EPSS auto-lookup + CWE auto-populate)** | NIST SSDF PW.5, OpenSSF Vulnerabilities check, ISO 27001 A.8.8 |
| **v5 G24 (Python G6 gates, cross-platform parity)** | n/a (portability; enables consistent gate execution across operator environments) |
| **v5 G25 (auto-generate security-review doc)** | NIST SSDF PO.4 + PS.3, ISO 27001 A.8.15 (logging), SOC 2 CC7.2 |
| **v5 G26 (stale-review lockout, Guideline #12 corollary)** | NIST SSDF PO.5, ISO 27001 A.5.31, SOC 2 CC1.4 |

## v5.1 framework extensions

### SLSA v1.2 forward-readiness (S2, new in v5.1)

SLSA v1.2 (published 2026) extends the v1.0 framework with a Source Track and refined Build Track guidance. The v5 skill is currently mapped to v1.0; below are the v1.2 additions to track. A bootstrap-emitted `.slsa-policy.yaml` template ([templates/slsa-policy.yaml](templates/slsa-policy.yaml)) declares the project's target levels.

| SLSA v1.2 track | Levels | v5 skill mapping | Status |
|---|---|---|---|
| Source L1 | Source available + retained | ✅ inherited via GitHub repo retention |
| Source L2 | Signed commits + branch protection | ⚠ PARTIAL — branch protection covered (Step 1.5.1); commit signing not enforced in pre-push gate; v5.2 candidate |
| Source L3 | Two-person review + verified history | ❌ HONEST-GAP — solo-dev structural impossibility (see §honest-gap field below) |
| Build L1/L2/L3 | Unchanged from v1.0 | ✅ existing per-step mapping |
| Provenance L1/L2/L3 | Unchanged from v1.0 | ✅ Step 7.3 PEP 740 + Step 7.5 cosign |

### NIST SSDF v1.2 IPD forward-readiness (S5 + 1P; FORTHCOMING)

NIST SP 800-218 v1.2 Initial Public Draft (IPD) published 2025-12-17; public comment closed 2026-01-30. NIST has not announced a FINAL publication date as of v5.1 ship. The skill tracks the IPD's specific new tasks below.

| New / changed task | Summary | v5 conformance |
|---|---|---|
| **PO.6.1** (NEW) | Update + improve development environments as threats, tools, technologies change | ✅ already covered (maintenance.md + skill version bumps) |
| **PO.6.2** (NEW) | Adopt new processes / tools / techniques to avoid errors + improve product security | ✅ already covered (skill itself is meta-process) |
| **PO.6.3** (NEW) | Improve vulnerability response processes + **periodically review previous decisions, especially "don't patch" decisions, accounting for customer impact over time** | ⚠ NEW GAP — no formal "review previous don't-patch decisions" workflow; v5.2 candidate (wire into lessons-learned.yaml register) |
| **PS.4.1-.4** (NEW group, Robust + Reliable Updates) | Customer update control, rollback mechanisms, resilient update engines | ❌ HONEST-GAP for libraries / CLIs — closes only for shipped applications with customer-update-control infrastructure |
| **RV.1.2** (EXPANDED) | Existing test requirement now explicitly requires testing **"default and other common configurations"**, not just code | ⚠ PARTIAL — Row 6 tests code; v5.2 to add config-permutation sub-check for projects with configurable behavior |

**v5.1 stance**: PS.4 declared honest-gap for non-application projects; PO.6.3 + RV.1.2 deferred to v5.2 with operational mitigations documented here.

### NIST SP 800-218A focused subset (S3 + 1Q; CORRECTED SCOPE in v5.1)

**Prior framing (overscoped, retracted)**: "The v5 skill is AI-authored, must map the entire 218A AI Profile."

**Corrected framing (v5.1)**: SP 800-218A's audience is producers / acquirers / operators of AI MODELS and AI SYSTEMS. The v5 skill is itself developed with AI assistance (Claude Code in the dev toolchain) but is NOT an AI model. The applicable subset is the "AI-tool-in-development-toolchain" lens, not the "this software IS an AI model" lens. Below is the ~10-task subset that applies under the corrected scope.

| 218A practice | AI-tool-in-toolchain applicability | v5 mapping |
|---|---|---|
| **PO.2.2** (role-based training) | YES — strong | Developers using AI coding assistants need awareness training on AI-specific risks; v5.1 adds A.6.3 training log template ([templates/a63-training-log.md](templates/a63-training-log.md)) |
| **PO.3.1** (toolchain inventory) | YES — strong | AI assistants (Claude Code, etc.) must appear in dev-toolchain inventory; first-run-bootstrap captures this |
| **PO.3.2** (toolchain approval) | YES — strong | AI assistants explicitly approved by org before use in code production |
| **PO.3.3** (toolchain monitoring) | YES — strong | Telemetry from AI assistants reviewed; prompt-injection risks tracked |
| **PO.1.x** (security req's for dev env) | PARTIAL | AI prompts may contain source / secrets — treat dev env as sensitive; secrets-in-prompts guidance |
| **PS.1.x** (protect code) | PARTIAL | AI-generated code treated as sensitive artifact; AI tools must not leak proprietary code via telemetry |
| **PW.5** (code review) | YES — strong | AI-generated code reviewed at equal-or-stricter standard than human-written; auto-fire `/code-review` (v5 Row 11) covers |
| **PW.6** (test) | YES — strong | AI-generated code subject to same test gate as human-written (v5 Row 6) |
| **PW.7** (security review) | YES — strong | `/security-review` fires equally on AI-generated PRs (v5 Step 4) |
| **PW.8** (vulnerability test) | YES — strong | DAST + SAST runs equally (v5 Step 4) |
| **RV.\*** (vulnerability response) | YES — strong | When AI-generated code has a vuln, identify similar occurrences via codebase grep + adjust prompt / tool config (lessons-learned.yaml) |

**NOT applicable to this skill** (scoped to actual AI model producers): PS.3 augmented for AI model build infrastructure; AI-specific data sourcing practices; AI model-card requirements; foundation-model dual-use risk assessment.

### OSPS Baseline 8-family complete map (S4, NEW in v5.1)

OpenSSF Open Source Project Security Baseline (OSPS Baseline) — 8 control families, 3 maturity levels, ~42 controls total. Authoritative source: `github.com/ossf/security-baseline`.

#### AC — Access Control (6 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-AC-01.01 | 1/2/3 | MFA required for sensitive actions in authoritative repo | ✅ relies on org policy (out-of-skill-scope) |
| OSPS-AC-02.01 | 1/2/3 | New collaborators receive manual permission OR default to lowest-privilege | ✅ relies on org policy |
| OSPS-AC-03.01 | 1/2/3 | Direct commit on primary branch blocked by enforcement mechanism | ✅ Step 1.5.1 protected-branch state check |
| OSPS-AC-03.02 | 1/2/3 | Primary branch deletion requires explicit confirmation | ✅ branch protection covers |
| **OSPS-AC-04.01** | 2/3 | **CI/CD tasks without specified permissions default to lowest tier** | ⚠ NEW GAP — v5.2 candidate; audit `.github/workflows/*.yml` for missing `permissions:` keys |
| **OSPS-AC-04.02** | 3 | **Pipeline job permissions limited to minimum necessary** | ⚠ NEW GAP — v5.2 candidate |

#### BR — Build & Release (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-BR-01 | 1/2/3 | Prevent untrusted input access to privileged resources | ✅ Row 11 + Step 1.5.1 |
| OSPS-BR-02 | 2/3 | Unique version IDs per release + asset | ✅ tag + per-package version pin |
| OSPS-BR-03 | 1/2/3 | Encrypted channels for all dev + release comms | ✅ HTTPS default |
| OSPS-BR-04 | 2/3 | Descriptive change logs (functional + security mods) | ✅ Row 17 CHANGELOG-presence gate |
| OSPS-BR-05 | 2/3 | Standardized dependency management tools | ✅ uv.lock / package-lock.json / Cargo.lock per shape |
| OSPS-BR-06 | 2/3 | Cryptographic signatures + hashes on released assets | ✅ Step 7.3 PEP 740 + Step 7.5 cosign |
| OSPS-BR-07 | 1/3 | Prevent unintentional secret storage + credential mgmt policy | ✅ Row 1 sweep + explicit policy via 1C GOVERNANCE template |

#### DO — Documentation (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-DO-01 | 1/2/3 | User guides (install / config / feature usage) | ✅ project docs |
| OSPS-DO-02 | 1/2/3 | Defect / issue reporting mechanism | ✅ GitHub Issues |
| **OSPS-DO-03** | 3 | **Publish authenticity / integrity verification instructions for releases** | ✅ NEW in v5.1 — verification recipe doc via 1N ([templates/verification-recipe.md](templates/verification-recipe.md)) |
| **OSPS-DO-04** | 3 | **Document scope + duration of support per released version** | ✅ NEW in v5.1 — closes via 1C EOL.md template |
| **OSPS-DO-05** | 3 | **Communicate when security-update cessation occurs per release** | ✅ NEW in v5.1 — closes via 1C EOL.md template |
| OSPS-DO-06 | 2/3 | Document process for selecting + obtaining + tracking deps | ⚠ PARTIAL via SBOM (Step 7.6); v5.2 to add explicit process doc |
| OSPS-DO-07 | 2/3 | Build-from-source instructions including required deps | ✅ project README |

#### GV — Governance (4 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-GV-01 | 2/3 | Publish project roles + responsibilities | ✅ NEW in v5.1 — closes via 1C GOVERNANCE.md template |
| OSPS-GV-02 | 1/2/3 | Public discussion mechanism | ✅ GitHub Discussions/Issues |
| OSPS-GV-03 | 1/2/3 | Contribution guide | ✅ CONTRIBUTING.md |
| **OSPS-GV-04** | 3 | **Formal review of permission grants before contributor elevation** | ❌ HONEST-GAP — solo-dev structural impossibility (see §honest-gap field below) |

#### LE — Legal (3 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| **OSPS-LE-01** | 2/3 | **Contributors assert legal authorization (DCO/CLA) on every contribution** | ⚠ PARTIAL — solo-dev defaults to self-DCO; v5.2 candidate for optional `Signed-off-by:` trailer enforcement |
| OSPS-LE-02 | 1/2/3 | OSI-approved / FSF-recognized license | ✅ checked at project setup |
| OSPS-LE-03 | 1/2/3 | License files in standard locations | ✅ LICENSE in repo root |

#### QA — Quality Assurance (7 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-QA-01 | 1/2/3 | Publish source + change history | ✅ GitHub repo + CHANGELOG |
| OSPS-QA-02 | 1/2/3 | Publicly visible deps | ✅ pyproject.toml / package.json / Cargo.toml |
| OSPS-QA-03 | 2/3 | Automated status checks pass before accepting changes | ✅ v5 pre-push gate + branch protection |
| OSPS-QA-04 | 1/2/3 | Consistent security requirements across codebases | ✅ Guideline #12 + 19-row gate |
| **OSPS-QA-05** | 1/2/3 | **Exclude generated executables + binaries from VCS** | ✅ NEW in v5.1 — Row 5 sub-check (1O): `git ls-files \| xargs file \| grep -E 'ELF\|Mach-O\|PE32'` |
| OSPS-QA-06 | 2/3 | Automated testing in CI/CD | ✅ Row 6 |
| **OSPS-QA-07** | 3 | **At least one non-author approval before merging to primary** | ❌ HONEST-GAP — solo-dev structural impossibility (see §honest-gap field below) |

#### SA — Security Assessment (3+1 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-SA-01 | 2/3 | Publish design descriptions (system actors / actions) | ✅ partial via positioning-and-value.md + threat-model.md |
| OSPS-SA-02 | 2/3 | Publish external interface descriptions (API / integration) | ✅ project README / api docs |
| OSPS-SA-03 | 2/3 | Maintain project security assessment | ✅ docs/security-review-vX.Y.Z.md (auto-generated per release) |
| **OSPS-SA-03.02** | 3 | **Threat modeling + attack surface analysis for critical code paths** | ✅ Step 1.5 threat-model freshness gate |

#### VM — Vulnerability Management (6 controls)

| Control ID | Maturity | Summary | v5 conformance |
|---|---|---|---|
| OSPS-VM-01 | 2/3 | CVD policy for reporting + addressing vulns | ✅ NEW in v5.1 — closes via 1B SECURITY.md template |
| OSPS-VM-02 | 1 | Security contacts discoverable in docs | ✅ NEW in v5.1 — closes via 1B SECURITY.md + security.txt template |
| OSPS-VM-03 | 2/3 | Confidential reporting channels for researchers | ✅ NEW in v5.1 — closes via 1B GHSA enablement guidance |
| OSPS-VM-04 | 2/3 | Publicly disclose vulns with mitigation; **VEX docs at maturity 3** | ⚠ PARTIAL — disclosure via GitHub Releases; VEX emission deferred to v5.2 |
| OSPS-VM-05 | 3 | Enforce pre-release dep-vuln + license policies | ⚠ PARTIAL — Row 14 + 15 fire pre-tag; OSPS wants PR-time blocking; v5.2 candidate |
| OSPS-VM-06 | 3 | Automated security testing with documented remediation thresholds + blocking | ✅ /security-review-scoped + /security-review triad |

**v5.1 OSPS Baseline maturity profile for solo-dev OSS projects (e.g., Evidentia)**:
- Maturity 1: ~100% conforming (closes OSPS-VM-02 gap via 1B template)
- Maturity 2: ~90% conforming (closes BR-07 / GV-01 via 1C + VM-01/02/03 via 1B; DO-06 deferred; LE-01 partial)
- Maturity 3: ~60% conforming (closes DO-03 via 1N + DO-04/05 via 1C; remaining gaps in AC-04 + GV-04 + QA-07 + VM-04 VEX + VM-05 PR-time — v5.2 candidates + structural honest-gaps)

### CMMI honest-claim paragraph (1L, v5.1)

CMMI (Capability Maturity Model Integration) is a private / licensed framework maintained by ISACA. The v5 skill is NOT formally CMMI-appraised — formal appraisal requires a SCAMPI lead appraiser and costs $50-100k+. Informally, the skill operates at roughly **CMMI Level 4 (Quantitatively Managed)** for its own scope: documented processes (this skill), metric collection (per-run JSONs), statistical process control (v5.1 1J control-chart helper at `scripts/control_chart.py`), and continuous improvement (maintenance.md). The user makes **NO formal CMMI conformance claim**; informal alignment is noted for completeness only. Treat all CMMI references in skill output as descriptive, not certified.

### Honest-gap field — structural impossibilities for solo-dev OSS (1M, expanded in v5.1)

The following controls require ≥2 distinct humans by definition. A solo-dev OSS project CANNOT structurally satisfy them; honest declaration is the correct posture rather than fake-attestation.

| Framework | Control | Reason it's structurally impossible |
|---|---|---|
| OpenSSF OSPS Baseline | OSPS-GV-04 | Formal permission-grant review before contributor elevation — solo dev has no second reviewer for self-elevation |
| OpenSSF OSPS Baseline | OSPS-QA-07 | At least one non-author approval before merging to primary — solo dev IS the author |
| SLSA v1.2 | Source L3 (two-person review) | Same as OSPS-QA-07 by construction |
| ISO 27001:2022 | A.5.3 (segregation of duties) | Same; solo dev holds all duties |
| SOC 2 Type II | CC1.4 (commitment to attract / develop / retain competent individuals — implies > 1 individual) | Same |
| NIST SSDF v1.1 | PW.7 supplementary "independent review" | Same; primary review is by author |

**AI-as-force-multiplier framing** (v5.1 expansion): AI coding assistants (Claude Code, GitHub Copilot, Cursor, etc.) partially substitute for "second pair of eyes" via auto-fire `/security-review` + `/code-review` + automated SAST/SCA/DAST. However, AI review is **NOT** structurally equivalent to a second independent human reviewer — the AI shares the author's prompt context, can be biased toward the author's framing, and cannot meaningfully approve permission grants. Honest posture: declare AI as **partial mitigation** not **control satisfaction**. This framing reflects empirical findings that AI-assisted code has 322% more privilege-escalation paths (Apiiro 2024), 10.83 vs 6.45 issues per PR (CodeRabbit 2024), and that developers using AI assistants are 19% slower while subjectively perceiving themselves as faster (Cerbos 2024).

## Standards URLs

- NIST SSDF v1.1 (current normative): https://csrc.nist.gov/Projects/ssdf
- NIST SP 800-218A AI Profile (FINAL 2024-07-26): https://csrc.nist.gov/pubs/sp/800/218/a/final
- NIST SSDF v1.2 IPD (2025-12-17): https://csrc.nist.gov/pubs/sp/800/218/ipd
- SLSA v1.0: https://slsa.dev/spec/v1.0/
- SLSA v1.2: https://slsa.dev/spec/v1.2/
- OpenSSF Scorecard: https://scorecard.dev/
- OpenSSF Open Source Project Security Baseline: https://github.com/ossf/security-baseline
- CISA Secure by Design Pledge: https://www.cisa.gov/secure-by-design-pledge
- ISO 27001:2022: https://www.iso.org/standard/27001
- SOC 2 Type II Trust Services Criteria: https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
- DORA (EU): https://eur-lex.europa.eu/eli/reg/2022/2554/oj
- CMMI (ISACA, informal alignment only): https://cmmiinstitute.com/
