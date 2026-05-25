# Maintaining this skill (carried forward from v3 + extended for v4)

When modifying SKILL.md or any reference file, follow this
meta-rubric:

1. **Test every bash command BEFORE saving.** Markdown table cells
   require pipe-escaping (`\|`) which grep treats as a literal pipe,
   silently breaking ERE alternation. **Verified failure mode**: a
   regex like `grep -ciE "AKIA[0-9A-Z]{16}\|ASIA[0-9A-Z]{16}"`
   returns 0 hits even when fed a string containing both AKIA and
   ASIA prefixes. Always put runnable commands in fenced code
   blocks, not table cells. Test with a known-positive input ("does
   this actually catch the thing it's supposed to catch?") AND a
   known-negative input ("does this avoid false positives?").

2. **Sanity-check coherence end-to-end.** After multiple edits,
   re-read the entire file top-to-bottom for: contradictions
   between old and new sections, broken cross-refs, inverted pass
   criteria across rows of the same table, anchor targets that no
   longer exist.

3. **Bump the `version:` field in the YAML frontmatter** with each
   substantive change. Format: `YYYY.MM.DD-vN`. Use this to
   distinguish skill iterations in memory entries and answer
   "is this the version that has the fix for X?"

4. **Cross-reference changes in a sibling memory file** (e.g.,
   `pre_release_review_skill_vN.md` in the project's memory dir)
   capturing what changed, what was deliberately not applied,
   validation method, and re-execution recipe.

5. **Dry-run the changes against the session that surfaced them.**
   Each fix should demonstrably address the gap it was designed for.
   If a fix doesn't catch the original problem, redesign it.

## v4-specific extensions

6. **Maintain the SKILL.md ≤ 200 lines guideline.** When a
   reference file's content grows, link to it from SKILL.md
   rather than inlining. The Anthropic skill-architecture guidance
   prefers an entry-point + deep-references pattern over monolithic
   SKILL.md.

7. **Cross-references between reference files MUST resolve.** Use
   relative links like `[steps-3-4.md](steps-3-4.md)`. Validate
   with `grep -lE '\[[^]]+\]\([^)]+\.md\)'` + manual click-through
   before marking changes complete.

8. **Compliance-mapping coverage is not negotiable.** Any new
   skill capability or step must include a row in
   `compliance-mapping.md` showing which framework controls it
   satisfies. The audit-defensibility argument fails if any
   capability is unmapped.

9. **Preserve the v3 archive.** `_archive/SKILL-2026.04.25-v3.md`
   is read-only. Subsequent versions create their own archives:
   `_archive/SKILL-2026.MM.DD-vN.md` per iteration.

10. **Honor the publishing-authority protocol.** Skill changes
    are local-only; they're not pushed to a public repo (this skill
    is user-scope). However, project-side artifacts produced BY
    the skill (`docs/security-review-vX.Y.Z.md`,
    `docs/threat-model.md`, etc.) are public OSS files and must
    pass the standing-rule confidentiality + attribution sweeps
    before commit.

## v5-specific extensions

11. **Project-shape portability.** New rows of the pre-push gate +
    new verification gates + new Step 7 sub-step kinds must be
    written language-agnostic OR shipped per-shape. The default-
    routing table in `references/_shape-routes.json` is the canonical
    place for per-shape commands. Adding a new shape (e.g., Zig
    or Crystal) is a `_shape-routes.json` edit + a row in
    `references/project-shape-detection.md`'s detection table.

12. **publish-targets.yaml schema versioning.** Breaking changes to
    the schema bump `schema_version`. Skill refuses to operate on
    a mismatched version; migration prompts the operator to
    re-confirm the file. Backward-compat for `schema_version: 1`
    is maintained until v6.

13. **doc-inventory.yaml schema versioning.** Same as publish-targets;
    `schema_version` bumps on breaking changes; skill prompts re-
    confirm on migration.

14. **Bypass-phrase tampering protection.** The 3 verbatim bypass
    phrases are constants in [bypass-protocol.md](bypass-protocol.md);
    changing them is a breaking change to operator muscle-memory and
    requires a v6 bump + migration note. Per-project override of the
    phrase strings is prohibited (security feature: phrases must be
    audit-defensible and consistent across projects).

15. **Guideline #12 (push-gate hard rule) is immutable.** Removing
    or weakening Guideline #12 requires a v6 bump with explicit
    operator-approval in the migration note. The rule is the entire
    point of the v5 redesign per the v0.10.3/v0.10.4 ship-pattern
    failure analysis.

16. **Phase B audit trigger.** The `release_pattern_audit_directive.md`
    in the project's memory dir is the trigger for the post-v5
    audit. Skill v5+ maintainers MUST reference this directive when
    proposing a v6 — the audit's findings inform what should change.

## v5.1-specific extensions (added 2026-05-24)

17. **23 items landed in v5.1** per the v3 audit at
    `_audits/release-pattern-audit-2026-05-23-v3.md`. The breakdown:
    - 8 compliance-mapping doc additions (SLSA v1.2 forward-readiness,
      NIST SP 800-218A scope-corrected ~10-task subset, OSPS Baseline
      8-family complete map, NIST SSDF v1.2 IPD watch + FORTHCOMING
      section, CMMI honest-claim paragraph, expanded honest-gap field
      with AI-as-force-multiplier framing)
    - 5 bootstrap-emitted compliance templates (DORA Art. 17 incident
      matrix, SECURITY.md + security.txt + GHSA enablement, GOVERNANCE.md
      + EOL.md + risk-appetite triple, ISO 27001 A.6.3 training log,
      OSPS-DO-03 verification recipe; plus SLSA-policy.yaml stub)
    - 3 pre-push gate additions (Row 20 OSPS-QA-05 binary-in-VCS,
      Row 6 coverage threshold via `--cov-fail-under`, Step 7.4.5
      reproducible-build verify in step-7-post-tag.md)
    - 4 skill-prose enhancements (1E 3-question business-case prompt
      at Step 6.E; 1G Goddard+Parasuraman + 1T Cerbos/CodeRabbit/Apiiro
      citations in bypass-protocol.md justifying the 4-hour bound;
      1F qualitative FAIR Loss Magnitude column in bug-bucketing.md)
    - 2 freshness-window enhancements (1R `repo_risk_tier` low/medium/
      high parameterization with tiered warn/refuse thresholds; 1S
      context-sensitive invalidation triggers — new commits, Scorecard
      regression, new HIGH findings, CI status changes invalidate
      regardless of clock-time)
    - 2 new code/variant items (1J `scripts/control_chart.py` stdlib-
      only SPC helper with I-MR / u-chart / g-chart / DPMO; 1K DMADV
      5th variant for major-version bumps mapping the Six Sigma
      Define/Measure/Analyze/Design/Verify phases onto the 7-step
      structure)

18. **v5.1 closes OSPS Baseline Maturity 2 ~90% for solo-dev OSS
    projects** via the bootstrap-emitted templates alone. Maturity 3
    closes ~60% (gaps in AC-04, GV-04, QA-07, VM-04 VEX, VM-05
    PR-time blocking — the first three are structural-impossibilities,
    the last two are v5.2 candidates).

19. **Vocabulary preference when proposing v5.2 or later**: use OSPS
    Baseline + NIST SSDF + ISO 27001 + DORA citation language. These
    are now the canonical framework vocabularies for the skill's
    compliance posture, per the v3 audit's reconciliation of v2's
    218A overscoping.

## Framework lineage for v5 features (Tier 1 #1.6 — Phase B Q&A)

The Phase B release-pattern audit surfaced that many v5 features
implement specific framework principles WITHOUT explicit citation.
Documenting the lineage so auditors see the prior art (and so v6
maintainers know which framework's vocabulary to use for evolution):

| v5 feature | Framework principle (citation) |
|---|---|
| **Guideline #12 mechanical hard rule** | Lean jidoka (autonomation — machines stop at first defect) + andon cord (any operator can halt the line) |
| **Row 17 CHANGELOG-presence gate** | Lean poka-yoke (mistake-proofing — the v0.10.3 ship incident was the canonical poka-yoke trigger) |
| **19-row pre-push gate** | Scrum Definition of Done (every story passes a fixed acceptance set) + Lean continuous-flow gating |
| **Step 6.E STOP for tag-creation approval** | PRINCE2 "Authorising a Stage" / TOGAF Phase G "Implementation Governance" |
| **12 binding guidelines** | PMBOK 7 principles-based approach (vs PMBOK 6's process-based) |
| **7-step pre-tag flow** | ISO 9001:2015 PDCA cycle (Plan→Do→Check→Act mirrored in Steps 1→3→4→5→6→7) + Six Sigma DMAIC (Define→Measure→Analyze→Improve→Control mirrored in Steps 2→3→4→5→6) |
| **compliance-mapping.md** | COBIT 2019 MEA01 (Monitor, Evaluate, Assess Performance & Conformance) |
| **Per-run JSON freshness window** (4h REFUSE) | Six Sigma Control phase (process-stability monitoring) + Lean takt-time (cadence-driven WIP limits) |
| **bypass_events[] audit log** | ISO 27001 A.5.36 compliance review evidence + DORA Art. 17 incident classification |
| **/security-review-scoped per-subsystem partition** | OWASP DSOMM Test-and-Verification L3 dimension scoping |
| **publish-targets.yaml schema** | SLSA Verification track (consumer-facing verification policy) + COBIT BAI06 (Managed IT Changes) |
| **doc-inventory.yaml + must_match_version** | ISO 9001 A.7.5 control of documented information + Six Sigma Control phase artifact freshness |
| **first-run bootstrap wizard** | TOGAF Preliminary phase (architecture capability) + CMMI Initial (ML1) → Managed (ML2) elevation pattern |
| **Project-shape detection across 10 languages** | TOGAF ADM business-architecture-driven application architecture |
| **Step 7 publish-targets-driven sub-step generation** | SLSA Build Track L3 + NIST SSDF PS.3 + ITIL Release Management |
| **3 /security-review invocations** | NIST SSDF PW.7.1 + PW.7.2 (review + remediate, code-level) |
| **4 /code-review auto-fire triggers** | NIST SSDF PW.5.1 + NIST SSDF PW.6.1 + OpenSSF Scorecard Code-Review check |
| **Core (2) + optional (3) deliverables split** | Agile MoSCoW prioritization (Must-have / Should-have / Could-have / Won't-have) |
| **EPSS auto-lookup via FIRST.org** | NIST SP 800-30 quantitative risk assessment + FAIR Loss Event Frequency input |
| **Auto-generate security-review-vX.Y.Z.md from per-run JSON** | NIST SSDF PO.4 (document produced + maintained) + SOC 2 CC2.2 (information communicated) |
| **Quarterly cadence variant** | ITIL Continual Service Improvement (CSI) + Six Sigma Control phase + ISO 27001 A.5.36 review cadence |

When proposing v6 or later, prefer the framework vocabulary when
adding adjacent capabilities — auditors recognize "we added a TOGAF
Phase F Migration Plan step" faster than "we added a Step 5.X
deployment-prep phase."

## v5 innovations (Tier 1 #1.7 — publishable strengths surfaced by Phase B)

The Phase B audit identified 8 v5 features that no compared
framework (DevSecOps OR engineering/PM/EA OR GitHub/Claude OSS
tools) prescribes. These are genuine v5 innovations worth
documenting as prior art if v5 ever ships outside Allen's projects:

1. **Guideline #12 + 3 verbatim bypass phrases** — code-as-AI-safety primitive for human-in-loop release pipelines. No equivalent in any framework. The "verbatim phrase to bypass" pattern is original.

2. **Per-run JSON freshness window** (2h WARN / 4h REFUSE) — encodes trust-decay-as-a-timer for AI-driven gates. Original.

3. **Branch-protection bypass audit (Row 18)** — finer-grained than OpenSSF Scorecard's Branch-Protection check (which only verifies config, not bypass events). Worth upstreaming to Scorecard as a feature request.

4. **/security-review-scoped wrapper pattern** — closes a real builtin-can't-take-custom-scope gap. Reusable pattern for other Claude builtins where scope auto-detection doesn't fit a parent skill's needs.

5. **publish-targets.yaml 9-kind + custom escape hatch driving Step 7 generation** — Claude-native version of GoReleaser/release-please YAML pipelines but with human-in-loop STOP boundaries and verifier-step contracts.

6. **Auto-generate `docs/security-review-vX.Y.Z.md` from per-run JSON** — solves the markdown/JSON drift problem most release tools have (where the human-readable doc and the structured log silently disagree).

7. **doc-inventory.yaml + `must_match_version: true`** — direct attack on documentation staleness as a release-time invariant. The interactive wizard asking per-doc "must match version yes/no" is original framing.

8. **Project-shape detection across 10 languages with per-shape default partitions for /security-review-scoped** — broader than any single OSS release tool (GoReleaser covers some; nothing else covers all 10 shapes with per-shape security-partition defaults).

Each of these is documented in the skill's reference files; together
they represent ~12 hours of design work that wouldn't have surfaced
without the Phase B audit. If a v6 redesign considers stripping any
of them for simplicity, this section should be re-read first — the
audit confirmed they fill real gaps in the prior art.
