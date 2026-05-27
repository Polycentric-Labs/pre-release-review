# `/pre-release-review`

> A comprehensive, methodical, user-in-the-loop pre-tag review process
> for high-stakes releases. v5.1 adds **project-shape portability**
> (Python / Node / Rust / Go / Java / Ruby / PHP / Elixir / .NET),
> a **mechanical hard rule** preventing AI-driven push bypass (Guideline
> #12), a **20-row pre-push gate**, and **publish-targets-driven**
> post-tag verification (SLSA L3 / NIST SSDF PS.3.1 / OpenSSF Best
> Practices Silver / OSPS Baseline).

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Skill version](https://img.shields.io/badge/version-2026.05.27--v5.1.2-green.svg)](SKILL.md)

## What this is

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills)
that drives a 7-step pre-release review process designed for the case
where the project is:

- A job-search-critical portfolio piece
- An enterprise customer ship
- A regulatory-relevant artifact

— i.e., where the cost of shipping with a defect materially exceeds the
cost of an extra few hours of review.

The skill is **portable across project shapes**: Step 1.0 auto-detects
language + build system + publish targets and adapts subsequent steps
(test gates, build commands, post-tag verification) per detection. The
same skill drives PyPI + GHCR projects, Vercel-hosted Next.js apps,
and Rust-cargo + Homebrew-tap projects without per-project skill edits.

## Quick start

### Install (Claude Code)

```bash
# Clone into your Claude Code skills directory:
git clone https://github.com/Polycentric-Labs/pre-release-review \
  ~/.claude/skills/pre-release-review

# (Optional) Bundle the /security-review-scoped companion skill that
# /pre-release-review Step 4.1 calls:
cp -r ~/.claude/skills/pre-release-review/companion-skills/security-review-scoped \
  ~/.claude/skills/security-review-scoped
```

Restart Claude Code; the skill auto-discovers and becomes invokable as
`/pre-release-review`.

### Invoke

```
/pre-release-review
```

The skill will run through 7 steps with explicit STOP-for-approval
gates at each boundary. First invocation on a new project triggers the
[first-run bootstrap wizard](references/first-run-bootstrap.md).

### Variants

| Variant | When | Time |
|---|---|---|
| **Pre-tag (default)** | About to tag a public release | 10–18 hours |
| **Pre-push (in-flight)** | Local dev work ready for a feature branch push | 2–4 hours |
| **Pre-merge-to-main** | PR ready to merge via `gh pr merge` | 3–5 hours |
| **Quarterly cadence** | No release in flight; 3+ months since last review | 4–7 hours |
| **DMADV (major-version)** | 0.x → 1.0; 1.x → 2.0; new commercial / regulatory tier | 20–40 hours |

See [references/variants.md](references/variants.md) for the full table
+ skip-by-reuse criteria + DMADV phase mapping.

## What's in v5.1

The skill's 12 binding guidelines anchor every step. Highlights of v5.1's
substantive changes vs v5.0.1:

- **Guideline #12** (hard rule): The AI driver MAY NOT surface
  `git push`, `git tag + push`, `gh pr merge`, or any irreversible-publish
  command without (a) a fresh per-run JSON (< 4h) AND (b) the user's
  explicit per-action approval. Bypass requires one of 3 verbatim phrases
  (`PUSH TO MAIN BYPASS AUTHORIZED` / `STALE REVIEW ACCEPTED — <reason>`
  / `DOC FRESHNESS BYPASS — <reason>`). See [bypass-protocol.md](references/bypass-protocol.md).
- **Project-shape detection** (Step 1.0): auto-detects Python/uv,
  Node/pnpm, Rust/cargo, Go, Java/maven, Ruby, PHP, Elixir, .NET; persists
  to `.local/pre-release-review/project-shape.json`; drives the rest of
  the skill.
- **`publish-targets.yaml`** (NEW): declarative publish-target manifest
  with 9 supported kinds (PyPI / GHCR / GitHub Release / npm / vercel /
  cloudflare-pages / cargo / homebrew-tap / custom). Step 7 sub-steps
  are generated dynamically per declared target.
- **20-row pre-push gate** (was 17 in v4, 19 in v5): adds Row 18
  (branch-protection bypass audit), Row 19 (doc-freshness gate via
  `doc-inventory.yaml`), Row 20 (OSPS-QA-05 binary-in-VCS check).
- **`/security-review-scoped` wrapper**: per-subsystem security review
  that accepts explicit `--files` lists; closes the v4 failure mode where
  Step 4.1 was silently skipped 4 cycles running. See
  [companion-skills/security-review-scoped/](companion-skills/security-review-scoped/).
- **Auto-generated 5th canonical deliverable**: Step 7.10 auto-generates
  `docs/security-review-vX.Y.Z.md` from the per-run JSON.
- **Reproducible-build verification** (Step 7.4.5, NEW): when
  `config.yaml reproducible_build: true` is set, rebuilds from a clean
  worktree at the release tag and `diffoscope`-compares against the
  published artifact.
- **EPSS auto-lookup** (FIRST.org API) + **CWE auto-populate** (from
  `/security-review` output) in the bug-bucketing rubric. See
  [bug-bucketing.md](references/bug-bucketing.md).
- **Compliance mapping**: NIST SSDF v1.2 IPD watch + SLSA v1.2 +
  OpenSSF OSPS Baseline 8-family enumeration + CISA SbD Pledge +
  NIST SP 800-218A scope-corrected AI subset. See
  [compliance-mapping.md](references/compliance-mapping.md).
- **5 compliance-closure templates** in [references/templates/](references/templates/):
  SECURITY.md + security.txt, EOL.md, GOVERNANCE.md + risk-appetite.md,
  DORA Art. 17 incident-severity matrix, A.6.3 training log,
  OSPS-DO-03 verification-recipe.
- **DMADV variant** (NEW): 5th variant for major-version bumps
  (0.x → 1.0; 1.x → 2.0; introducing new product tiers).

For the full evolution narrative (v3 → v4 → v5 → v5.1), see [CHANGELOG.md](CHANGELOG.md).

## Repository layout

```
.
├── SKILL.md                          # entry-point manifest
├── references/                       # 16 reference files
│   ├── variants.md                   # 5 variant flows + skip-by-reuse
│   ├── steps-1-2.md                  # Step 1 (process) + Step 2 (positioning)
│   ├── steps-3-4.md                  # Step 3 (re-test) + Step 4 (capability)
│   ├── steps-5-6.md                  # Step 5 (refinements) + Step 6 (tag)
│   ├── step-7-post-tag.md            # Step 7 (publish-targets-driven verify)
│   ├── pre-push-gate.md              # 20-row runbook
│   ├── bypass-protocol.md            # Guideline #12 + 3 bypass phrases
│   ├── project-shape-detection.md    # Step 1.0 language/build/publish detect
│   ├── first-run-bootstrap.md        # wizard for greenfield projects
│   ├── publish-targets.md            # 9-kind publish-targets.yaml schema
│   ├── documentation-freshness.md    # doc-inventory.yaml + Row 19 gate
│   ├── security-review-integration.md
│   ├── security-review-scoped-wrapper.md
│   ├── code-review-integration.md
│   ├── compliance-mapping.md         # NIST SSDF / SLSA / OSPS / CISA / DORA
│   ├── bug-bucketing.md              # CRITICAL/HIGH/MEDIUM/LOW + CVSS/CWE/EPSS
│   ├── deliverables.md               # core (2) + optional (3) deliverables
│   ├── verification-gates.md         # programmatic step-output checks (Python)
│   ├── tools-prerequisites.md        # tool install guide + Python 3.11+ prereq
│   ├── maintenance.md                # meta-rubric for skill changes
│   └── templates/                    # 11 compliance-closure templates
├── scripts/
│   └── control_chart.py              # I-MR / u-chart / g-chart / DPMO
├── examples/                         # worked examples
│   ├── v0.10.4-walkthrough.md        # the v5.1 prototype run against Evidentia
│   └── release-pattern-audit-2026-05-23{,-v2,-v3}.md
├── companion-skills/
│   └── security-review-scoped/       # sub-skill /pre-release-review Step 4.1 calls
├── README.md  · LICENSE  · CHANGELOG.md  · SECURITY.md  · CONTRIBUTING.md
└── .gitignore
```

## Worked example

[`examples/v0.10.4-walkthrough.md`](examples/v0.10.4-walkthrough.md)
captures one full run of the skill against
[Polycentric-Labs/evidentia](https://github.com/Polycentric-Labs/evidentia)
v0.10.4 — 268 source files, 3370 tests, 7 PyPI packages, GHCR
container with cosign signing, GitHub Release with SBOM. Documents
every STOP gate, every operator decision, every finding (4 fix-now +
6 deferred), and 9 skill-iteration findings surfaced during the run.

## Cross-references

- The skill operates per Anthropic's [Claude Code Skills](https://docs.claude.com/en/docs/claude-code/skills) documentation
- Compliance alignment: [NIST SSDF v1.2 IPD](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd), [SLSA v1.0](https://slsa.dev/), [OpenSSF OSPS Baseline](https://github.com/ossf/security-baseline), [CISA Secure by Design Pledge](https://www.cisa.gov/securebydesign/pledge), [NIST SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final)
- Cited industrial AI-coding research: Cerbos *State of AI in Engineering 2024*; CodeRabbit *Q3 2024 PR Health Report*; Apiiro *AI Code Risk Report (2024)*
- Cited academic anchors: Parasuraman & Manzey 2010 (automation complacency); Goddard et al. 2012 (automation bias systematic review)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: open a GitHub
issue first to discuss substantive changes; small fixes (typos,
broken links, doc improvements) can go directly via PR.

## Security

See [SECURITY.md](SECURITY.md). Skill-specific bugs that have security
implications (e.g., a bypass-protocol gap that lets the AI driver
surface push commands without a fresh per-run JSON) get private
disclosure first.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## AI assistance

This skill was developed alongside AI platforms.

Models used: Claude Opus 4.6, Claude Opus 4.7, Sonar Deep Research
