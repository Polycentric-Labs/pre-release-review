# Contributing

Thanks for considering a contribution to `/pre-release-review`. This
skill ships with deliberate rigor; contributions follow the same
discipline.

## Bug reports + feature requests

**Open an issue first** for anything substantive:

- Bug reports: include skill version, project-shape (Python / Node /
  etc.), command transcript, expected vs actual behavior
- Feature requests: state the use case + the failure mode you're
  trying to prevent
- For security-relevant bugs, see [SECURITY.md](SECURITY.md) (private
  disclosure first)

Trivial fixes (typos, broken links, doc clarifications) can go directly
via PR without an issue.

## Pull-request workflow

1. **Fork + branch from `main`**. Use a descriptive branch name
   (`fix/pre-push-row-1-windows-grep` not `patch-1`).
2. **Match the existing prose style** in the reference files —
   declarative, table-heavy, explicit pass/fail criteria. Look at
   [references/pre-push-gate.md](references/pre-push-gate.md) for the
   canonical voice.
3. **Conventional-commit prefixes**:
   - `feat(<scope>):` — new capability
   - `fix(<scope>):` — bug fix
   - `docs(<scope>):` — doc-only change
   - `chore(<scope>):` — non-functional (tooling, ci, lint)
   - `refactor(<scope>):` — non-behavioral code change
4. **No `Co-Authored-By: Claude` trailers**; no `🤖 Generated with
   [Claude Code]` footers. The skill itself enforces this discipline
   for projects it reviews (pre-push gate Rows 2 + 3); the skill repo
   follows the same rule for itself.
5. **Include a CHANGELOG.md entry** for substantive changes.
6. **PR description** should explain the why (the body of the PR is
   load-bearing audit content).

## Versioning policy

The skill uses **calendar-based versioning**: `YYYY.MM.DD-v<major>[.<minor>]`.

- Date = lock-in date of the design (not the publish date)
- Major bump = breaking change to the skill's STOP-gate structure, the
  bypass-phrase vocabulary, the pre-push gate row table, or the public
  reference-file API that other skills may call
- Minor bump = additive changes to the same major (new gate rows, new
  variants, new references)

The 4 most recent versions:

- `2026.05.24-v5.1` — current (project-shape portability ships)
- `2026.05.23-v5.0.1` — v5 baseline
- `2026.04.30-v4` — 7-step + mandatory `/security-review`
- `2026.04.25-v3` — initial 6-step skill

See [CHANGELOG.md](CHANGELOG.md) for the full evolution.

## Design principles

When proposing a change, check whether it respects these:

1. **The user is always in the loop**. The skill drives a process; the
   operator confirms each step boundary.
2. **STOP gates are not optional**. Adding a feature that bypasses a
   STOP gate requires Guideline #12 bypass-phrase support.
3. **Educational mode is on**. Reference files explain why a check
   exists, not just what it does. Auditors and hiring managers read
   the references; write for them.
4. **Honest gaps over false claims**. If a check can't be reliably
   automated, document it as a SKIP with rationale, not as a PASS.
5. **Cross-platform parity**. Bash + GNU coreutils + Windows are all
   supported. Use Python helpers under `scripts/` for cross-platform
   logic.
6. **Discoverable, not magical**. The skill's behavior should be
   reproducible from reading the references; no hidden state.

## Adding a new variant

If you propose a 6th variant beyond Pre-tag / Pre-push / Pre-merge-to-
main / Quarterly / DMADV:

1. Add a row to [references/variants.md](references/variants.md) `## Variant decision matrix`
2. Document the step subset in the `## Variant decision matrix` table
3. Include a time estimate
4. Add a sub-section explaining when to use vs the other variants
5. Update [SKILL.md](SKILL.md) `## The 7-step structure` if step
   behavior differs

## Adding a new pre-push gate row

If you propose a Row 21+:

1. Add to [references/pre-push-gate.md](references/pre-push-gate.md) the
   row table + the runbook bash/Python (cross-platform — see Design
   Principle 5)
2. Add to the per-shape `_shape-routes.json` if the row only applies
   to certain shapes
3. Update the row count in SKILL.md (currently 20-row table)
4. Document the failure mode the row prevents (cite the incident if
   one exists; the skill's narrative is grounded in real incidents)

## Adding a new publish-target kind

The 9 supported kinds are documented in
[references/publish-targets.md](references/publish-targets.md). If you add
a 10th (e.g., `crates-io`, `chocolatey`, `apt-repo`):

1. Add a `### kind-name` section with example YAML config + verify
   steps
2. Add the Step 7 sub-step generators that fire for this kind
3. Add a `_shape-routes.json` entry so project-shape detection knows
   when to suggest it
4. Add a probe-script template (per SF-5 lesson from the v5.1 Evidentia
   prototype) if applicable

## License

All contributions are submitted under the [Apache License
2.0](LICENSE) per its §5 Contributions clause.
