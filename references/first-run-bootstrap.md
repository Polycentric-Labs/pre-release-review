# First-run bootstrap (NEW in v5)

> **Purpose**: handle the new-project case where there's no prior tag, no positioning doc, no threat model, no release-checklist, no security-review-vX.Y.Z.md. v4 refused to advance past Step 1.5 (threat-model staleness check) on first run. v5 detects the condition and offers a guided wizard.

Runs at **Step 1.0** — after project-shape detection ([project-shape-detection.md](project-shape-detection.md)) and before Step 1.1's standard guideline-restatement.

## First-run condition (all must hold)

1. `git describe --tags --abbrev=0 2>/dev/null` returns nothing (no prior tag)
2. `docs/positioning-and-value.md` does NOT exist
3. `.local/pre-release-review/config.yaml` does NOT exist
4. `.local/pre-release-review/runs/` is empty or absent

If ALL 4 hold → first run. If ANY one is false → skip bootstrap, fall through to standard Step 1.

## The wizard

```
This appears to be a first /pre-release-review run for this project.
Detected shape: <shape from project-shape-detection>
Detected publish targets: <list from publish-target detection>
Detected protected branches: <list, or "none">

Options:
  (1) Generate skeletons for the core 2 deliverables (release-checklist
      + security-review-v<X.Y.Z>) + .local/pre-release-review/config.yaml.
      Use this for a minimal first release.
  (2) Generate skeletons for all 5 deliverables (core + 3 optional:
      positioning-and-value + capability-matrix + v<X.Y.Z+1>-plan) +
      docs/threat-model.md + .local/pre-release-review/config.yaml.
      Use this for projects that will benefit from the full doc culture
      (commercial / portfolio / regulatory).
  (3) Custom — pick which of the 5 deliverables to generate.
  (4) Skip generation; I'll populate manually before the next run.
  (5) Abort — this isn't the right time for a first /pre-release-review.

Recommended: (1) for new projects without external visibility;
             (2) for projects that will be evaluated by employers,
                 customers, auditors, or regulators.
```

## What each skeleton contains

### Core skeletons (always)

#### `docs/release-checklist.md` (≈250 lines)
The 11-step self-referential checklist from [steps-5-6.md §6.A](steps-5-6.md). Pre-populated with the detected shape's test/lint/build commands. Includes Steps 0-11 with project-name + publish-target placeholders.

#### `docs/security-review-v<X.Y.Z>.md` (≈300 lines, in-progress shape)
Pre-populated with sections per [deliverables.md §docs/security-review-vX.Y.Z.md structure](deliverables.md). Bug-bucket table empty + ready for findings. Includes the canonical 17-row pre-push gate sub-section pre-stubbed.

#### `.local/pre-release-review/config.yaml`
```yaml
schema_version: 1
project_shape:
  primary: <detected>
  build_system: <detected>
deliverables:
  core: [release-checklist, security-review]
  optional: []   # populated from wizard option (1) vs (2) vs (3)
publish_targets_file: .local/pre-release-review/publish-targets.yaml
doc_inventory_file: .local/pre-release-review/doc-inventory.yaml
target_tier: silver  # OpenSSF Best Practices tier; "passing" / "silver" (default) / "gold"; gates Row 6 coverage threshold (1I in v5.1)
repo_risk_tier: low  # (1R in v5.1) high / medium / low; gates per-run JSON freshness ceiling per bypass-protocol.md §B2
review_freshness:
  # v5.1 NOTE: explicit values below override repo_risk_tier defaults.
  # Defaults per tier: high=15/60min, medium=60/120min, low=120/240min.
  warn_after_hours: 2
  refuse_after_hours: 4
context_sensitive_invalidation:  # 1S in v5.1
  enabled: true
  triggers:
    - new_commits             # new commits since per-run JSON completed_at
    - scorecard_regression    # Scorecard score dropped > 0.5 points
    - new_high_findings       # any new HIGH+ SAST / SCA / DAST finding
    - ci_status_change        # required CI checks transitioned passing<->failing
container_cve_tool: grype  # v5.0.1 default; "trivy" opt-in
binary_in_vcs_allowlist: []  # 1O in v5.1; paths exempt from Row 20 binary-in-VCS check
reproducible_build: false    # 1H in v5.1; set true to enable Step 7.4.5 verify
reproducible_build_command: "uv build --all-packages"  # used when reproducible_build: true
bypass_phrases:
  push_to_protected: "PUSH TO MAIN BYPASS AUTHORIZED"
  stale_review: "STALE REVIEW ACCEPTED"
  doc_freshness: "DOC FRESHNESS BYPASS"
protected_branches: <detected, or empty list>
first_run_completed_at: <ISO timestamp>
```

### Compliance closure bundle (NEW in v5.1; offered as wizard sub-option)

The v5.1 release adds 6 bootstrap-emitted templates that close specific OpenSSF OSPS Baseline + ISO 27001 + DORA gaps in one shot. Offered when the operator selects wizard option (2) or (3) "compliance-aware bootstrap":

| Template file | Closes | Source template |
|---|---|---|
| `SECURITY.md` + `.well-known/security.txt` | OSPS-VM-01/02/03 (CVD policy + contacts + confidential channels) | [templates/SECURITY.md](templates/SECURITY.md) + [templates/security.txt](templates/security.txt) |
| `GOVERNANCE.md` | OSPS-GV-01 (roles + responsibilities) + OSPS-BR-07 (credential mgmt policy) | [templates/GOVERNANCE.md](templates/GOVERNANCE.md) |
| `EOL.md` | OSPS-DO-04 + OSPS-DO-05 (support window + cessation comms) | [templates/EOL.md](templates/EOL.md) |
| `risk-appetite.md` | ISO 31000 framing + compliance-mapping.md §risk-appetite | [templates/risk-appetite.md](templates/risk-appetite.md) |
| `docs/a63-training-log.md` | ISO 27001 A.6.3 (information security training) + NIST SP 800-218A PO.2.2 (role-based training) | [templates/a63-training-log.md](templates/a63-training-log.md) |
| `docs/verification.md` (from verification-recipe template) | OSPS-DO-03 (publish authenticity verification instructions) | [templates/verification-recipe.md](templates/verification-recipe.md) |
| `docs/DORA-Art-17-incident-matrix.md` | DORA Article 17 (incident severity classification) — informational unless project ships to EU FE | [templates/DORA-Art-17-incident-matrix.md](templates/DORA-Art-17-incident-matrix.md) |
| `.slsa-policy.yaml` | SLSA v1.2 target-level declaration (S2 in v5.1) | [templates/slsa-policy.yaml](templates/slsa-policy.yaml) |

The wizard renders each template with project-specific substitutions (`<REPLACE_WITH_*>`, `<OWNER>`, `<REPO>`, `<PROJECT-DOMAIN>`, dates). Operator reviews + can hand-edit before commit.

**Net OSPS Baseline maturity uplift**: a project that adopts the full compliance closure bundle goes from ~50% Maturity 2 conforming to ~90% conforming in one bootstrap pass.

### Optional skeletons (wizard option 2 / 3)

#### `docs/positioning-and-value.md` (≈300 lines skeleton, 10-15k word target)
12 required H2 sections from [deliverables.md](deliverables.md): Executive summary / What it is / Current capabilities / Intellectual ancestry / Competitive landscape / Differentiation / Industry tailwinds / Positioning frame / AI posture / 12-month direction / Risk register / Sources. Each section starts with a `<!-- TODO: ... -->` prompt.

#### `docs/capability-matrix.md` (≈200 lines skeleton)
10 risk-tier-ordered surface rows pre-stubbed with `⚠ (untested)` markers. Operator fills in per surface.

#### `docs/v<X.Y.Z+1>-plan.md` (≈150 lines skeleton)
Forward-looking next-release scope template. Empty bug-bucket carry-overs section + empty deliverables breakdown.

#### `docs/threat-model.md` (≈400 lines skeleton)
STRIDE table per asset with `⚠ (unidentified)` placeholder rows. Required so Step 1.5 (180-day threat-model staleness check) doesn't refuse the next run.

### Publish targets (always)

#### `.local/pre-release-review/publish-targets.yaml`
Pre-populated with detected publish targets per [publish-targets.md](publish-targets.md). Wizard asks the operator to confirm/edit/add before saving. Schema validated at write time.

### Doc inventory (always)

#### `.local/pre-release-review/doc-inventory.yaml`
Per [documentation-freshness.md](documentation-freshness.md). Generated by scanning `docs/**/*.md` + repo-root `*.md` (after skeleton generation so the new docs are included). Wizard walks the operator through `owner` (defaults to `git config user.name`) + `staleness_policy` + `must_match_version` for EACH doc — Q11 mandates the user is asked which docs must match version.

### CHANGELOG bootstrap (always)

#### `CHANGELOG.md` (if missing) + `scripts/extract_changelog_block.py` + `.github/workflows/verify-changelog.yml`
Per Q4 ask-before-write — wizard surfaces all 3 + asks operator to confirm. If yes:
- `CHANGELOG.md`: Keep-a-Changelog skeleton with `[Unreleased]` + `[0.1.0] - <today>` blocks
- `scripts/extract_changelog_block.py`: skill-bundled template script
- `.github/workflows/verify-changelog.yml`: skill-bundled template workflow

## Step-skip rules on first run

Because there's no `<prev-tag>`, several v4 step internals don't apply. First-run-mode adjusts:

| Step | First-run behavior |
|---|---|
| 1.5 threat-model staleness check | SKIP (skeleton just generated; staleness count starts at 0) |
| 2.x positioning research | SKIP if wizard option (1); RUN if option (2)/(3) |
| 3.1 `/security-review` invocation #1 (scope `<prev-tag>..HEAD`) | RUN against `<root-commit>..HEAD` instead |
| 3.2 `/code-review` auto-fire triggers | RUN; trigger 2 (new file) will fire for every file → log as "first-run baseline" |
| 4.1 `/security-review` invocation #2 (per-subsystem) | RUN; per-subsystem partitioning per project-shape |
| 5.B `docs/v<X.Y.Z+1>-plan.md` | Adjust to `docs/v0.2.0-plan.md` (or per the first tag's actual next version) |
| 6.A `docs/release-checklist.md` | Already generated by bootstrap; Step 6.A is then a review + adjust, not a fresh write |
| 6.C 17-row pre-push gate | RUN all rows; rows that reference `<prev-tag>` (12 code-scan delta) skip with explicit "first-run; no baseline" log |
| 7 post-tag verification | RUN; this is the FIRST baseline for future Step 7.7 score-regression checks |

## After bootstrap — first run continues

The wizard completes, the skeletons are written + committed (via [commit](../../commit/SKILL.md) skill per the no-co-authorship rule), and the standard Step 1.1-1.7 flow resumes. The first STOP gate is at Step 1.7 plan approval; the operator confirms the wizard outputs before parallel work starts.

## Subsequent runs

The bootstrap condition (all 4 holds) won't recur because the first run created `.local/pre-release-review/config.yaml` + `runs/<utc-iso>.json`. Future runs detect the existing config and skip the wizard entirely.

If the operator wants to RE-bootstrap (e.g., to regenerate skeletons after wiping `docs/`), they delete `.local/pre-release-review/config.yaml` first; the wizard re-fires on the next run.

## Edge cases

| Case | Handling |
|---|---|
| Project has tags but no docs (mid-life adoption) | Bootstrap conditions 2-4 hold but condition 1 fails → skip wizard, fall through standard flow; operator runs Step 2 (positioning) full to bootstrap the optional deliverables |
| Project has docs but no tags (pre-release prep) | Conditions 1 + 4 hold but 2-3 fail → skip wizard, treat as standard pre-tag flow with `<root-commit>..HEAD` scope |
| Project is a fork of another project (inherited tags + docs) | All conditions fail → standard flow; operator may want to manually delete inherited security-review-vX.Y.Z.md docs that don't apply |
| Polyglot project | Wizard offers to generate skeletons in both languages' conventional paths (e.g., `docs/` + `apps/web/docs/`) |
| Skill itself is the project under review | The skill is `~/.claude/skills/pre-release-review/` — `.local/` lives at the skill's parent; bootstrap proceeds normally; the skill self-tests are the test gate |

## Validation

Skeleton generation MUST:
- Pass `markdown-lint` (or equivalent — skill ships a portable Python markdown validator)
- Have no `<<<TEMPLATE>>>` strings left unresolved
- Pass the Step 2 / 4 / 6 verification gates (with first-run-leniency: word/citation/section counts can be 0 on a freshly generated skeleton; the next run enforces the real thresholds)
