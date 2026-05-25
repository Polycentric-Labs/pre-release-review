# Step 7 — Post-tag verification (NEW in v4; publish-targets-driven in v5)

Goal: verify the published artifact matches the build artifact.
Closes the SLSA L3 + NIST SSDF PS.3.1 audit gap that v3 had no
explicit step for. Runs immediately after `release.yml` (or the
project's release workflow equivalent) completes its publish.

**v5 change (per Q8)**: Step 7's sub-step list is now generated
dynamically from `.local/pre-release-review/publish-targets.yaml`
per [publish-targets.md §Step 7 sub-step generation](publish-targets.md#step-7-sub-step-generation).
The v4 hardcoded sub-steps below are now the defaults for projects
with `pypi-trusted-publisher` + `ghcr-container` + `github-release`
targets (Evidentia shape). Projects with other targets (npm,
vercel, cargo, homebrew-tap, etc.) get sub-steps generated per
their declared targets — see [publish-targets.md](publish-targets.md)
for the per-kind verify-step catalog.

This step CLOSES THE AUDIT LOOP: the artifact a user
`pip install`s or `docker pull`s should match the artifact the
build produced. Any drift indicates registry-side compromise,
mid-pipeline tampering, or a registry caching bug — all of which
require investigation before users adopt the release.

Total time: 30–90 minutes per release.

## 7.1 Wait for `release.yml` completion

```bash
gh run watch --exit-status
```

Confirms the workflow finished. Exit code 0 = success; non-zero =
investigate before any 7.x verification (the artifacts may not
exist).

## 7.2 PyPI artifact verification

```bash
# Fresh venv to avoid cache contamination
mkdir -p /tmp/postag-verify-vX.Y.Z
cd /tmp/postag-verify-vX.Y.Z
python -m venv .venv && source .venv/bin/activate

# Download just the wheel (no deps — we're checking the wheel itself)
pip download "evidentia==X.Y.Z" --no-deps -d ./

# Compare sha256 to the build's dist/
sha256sum *.whl > pypi-hashes.txt
sha256sum <repo>/dist/*.whl > build-hashes.txt
diff pypi-hashes.txt build-hashes.txt
```

**Pass criterion**: hashes match. **Fail action**: investigate
PyPI tampering or build-pipeline drift before notifying users.

## 7.3 PEP 740 attestation verification

```bash
pypi-attestations verify pypi \
  --repository https://github.com/<owner>/<repo> \
  --workflow release.yml \
  "pypi:evidentia==X.Y.Z"
```

**Pass criterion**: every wheel reports verified attestation.
This is the v0.7.1-trap fix — `gh attestation verify` does NOT
work for PEP 740 publish attestations (defaults to SLSA provenance
v1 which v0.7.1 didn't emit). Use `pypi-attestations verify pypi`
which understands the PEP 740 bundle format.

## 7.4 SLSA build-provenance verification (v0.7.3+ projects only)

```bash
gh attestation verify dist/<wheel>.whl \
  --owner <owner> \
  --signer-workflow .github/workflows/release.yml
```

**Pass criterion**: SLSA L3 build provenance v1 predicate matches.
Skip this sub-step for projects that don't yet emit SLSA L3
provenance.

## 7.4.5 (NEW v5.1; 1H) Reproducible-build verify

> In-scope only when `config.yaml reproducible_build: true`. Skip with `[INFO 7.4.5] reproducible_build not declared; skipping` for projects that don't claim SLSA Build L3 reproducibility.

```bash
# Read the build command from the project's reproducible-build manifest.
# Convention: .local/pre-release-review/reproducible-build.sh OR a documented
# "build" target in pyproject.toml / package.json / similar.
BUILD_CMD="$(python -c 'import yaml; d=yaml.safe_load(open(".local/pre-release-review/config.yaml")); print(d.get("reproducible_build_command", "uv build --all-packages"))' 2>/dev/null || echo 'uv build --all-packages')"

# Clean room: fresh worktree at the exact release tag
TMPDIR="$(mktemp -d)"
git worktree add "$TMPDIR" "vX.Y.Z"
pushd "$TMPDIR" >/dev/null

# Rebuild
rm -rf dist/
eval "$BUILD_CMD"

# Download the PUBLISHED artifact for comparison
mkdir -p /tmp/published-vX.Y.Z
cd /tmp/published-vX.Y.Z
pip download "<package>==X.Y.Z" --no-deps -d ./

# Diff the rebuilt vs published wheels with diffoscope
diffoscope "$TMPDIR/dist/<package>-X.Y.Z-py3-none-any.whl" /tmp/published-vX.Y.Z/<package>-X.Y.Z-py3-none-any.whl

popd >/dev/null
git worktree remove "$TMPDIR"
```

**Pass criterion**: `diffoscope` returns zero output (artifacts are byte-identical). Acceptable noise: build timestamps in `RECORD` files or `WHEEL` metadata can differ if the build wasn't run with `SOURCE_DATE_EPOCH` pinned — document the allowable diff scope in `config.yaml reproducible_build_known_drift[]`.

**Fail action**: investigate as a supply-chain compromise OR a build-environment drift (compiler version, locale, timezone). Pin the build environment in CI (`SOURCE_DATE_EPOCH`, deterministic archive ordering) and re-attempt.

**Why this matters**: closes SLSA Build L3 "hermetic builds" + NIST SSDF PS.3 "protect all forms of code from unauthorized access and tampering" verification gap. The G10 line in compliance-mapping.md ("reproducible builds") refers to the policy commitment; this step is the actual verification.

## 7.5 Container image verification

```bash
# Cosign keyless verify
cosign verify ghcr.io/<owner>/<image>:vX.Y.Z \
  --certificate-identity-regexp="https://github.com/<owner>/<repo>/.+" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Functional smoke
docker run --rm ghcr.io/<owner>/<image>:vX.Y.Z version
```

**Pass criterion**: cosign reports verified + version output
matches `vX.Y.Z`.

## 7.6 SBOM body verification (NEW in v4 per G2)

```bash
# Compare published SBOM against build SBOM
gh release download vX.Y.Z --pattern '*sbom.json'
diff <build-sbom.json> <published-sbom.json>

# Run osv-scanner on the published SBOM
osv-scanner --sbom <published-sbom.json>
```

**Pass criterion**: SBOM bodies match exactly + osv-scanner
returns 0 unacked vulnerabilities.

## 7.7 Scorecard re-run + score-regression check

```bash
gh api /repos/<owner>/<repo>/code-scanning/alerts \
  --paginate -q '[.[] | select(.state=="open" and .rule.security_severity_level=="high")] | length'

# Trigger a Scorecard run manually if not already scheduled
gh workflow run scorecard.yml
gh run watch --exit-status

# Compare score (use the published Scorecard API)
curl -s "https://api.scorecard.dev/projects/github.com/<owner>/<repo>" | jq .score
```

**Pass criterion**: Scorecard score did not regress vs the prior
release's recorded score. Drop > 0.5 points = investigate.

## 7.8 Fresh-venv install smoke

```bash
python -m venv /tmp/fresh-install-vX.Y.Z
source /tmp/fresh-install-vX.Y.Z/bin/activate
pip install "evidentia[gui]==X.Y.Z"
evidentia version  # NOT --version (Typer subcommand convention)
evidentia catalog list | head -10
```

**Pass criterion**: install succeeds + smoke commands return
expected output.

## 7.9 GitHub Release notes audit

```bash
gh release view vX.Y.Z --json body | jq -r .body | head -50
```

Confirm CHANGELOG-style summary present + SBOM attached as a
release artifact + `release.yml` artifacts (sigstore bundle, SLSA
provenance, etc.) attached.

## 7.10 Memory + audit-log update + auto-generate `docs/security-review-vX.Y.Z.md` (Q9)

- **NEW v5 (per Q9)**: auto-generate
  `docs/security-review-vX.Y.Z.md` from the per-run JSON by
  template-substituting the structured log into the canonical
  template per [deliverables.md §docs/security-review-vX.Y.Z.md structure](deliverables.md#docs-security-review-vxyzmd-structure-new-v4).
  Skill loads `.local/pre-release-review/runs/<run-id>.json`, renders
  the doc, writes + commits via the [commit](../../commit/SKILL.md)
  skill. Operator reviews + can hand-edit before the commit; the
  per-run JSON remains the source of truth, the markdown is the
  human-readable view.
- Append final findings + Step 7 outcomes to the generated doc
- Update the project's MEMORY.md with the SHIPPED-vX.Y.Z entry
  + commit SHA + tag time + full Step 7 outcome + any
  `bypass_events[]` accumulated during this cycle (Q5)
- Update `~/.claude/projects/.../memory/<project>_vX_Y_Z_shipped.md`
  with: tag SHA, all generated-sub-step outcomes, any unresolved
  drift, Scorecard delta, time-to-publish, bypass events
- **NEW v5 (per Q11)**: update `last_reviewed_version` +
  `last_reviewed_sha` + `last_reviewed_date` in
  `.local/pre-release-review/doc-inventory.yaml` for every doc
  touched this cycle. Per [documentation-freshness.md §Step 7.10 update](documentation-freshness.md).

## 7.11 STOP and surface to user

Final summary to user includes:

- All 9 sub-step outcomes
- Drift analysis (any artifact-vs-build mismatch)
- Time-to-publish (`gh run view --json startedAt,completedAt`)
- Recommended next step: announce, draft v0.X.(Y+1) plan, or
  investigate drift

If any sub-step failed: immediate next steps are remediation, NOT
announcement. The release stays "tagged but not announced" until
drift is explained.

## 7.12 Post-release housekeeping (delegated from Step 6.H)

Only after 7.1–7.11 all pass:

- Archive deprecated repos (`gh repo archive`)
- Yank deprecated artifacts (`pip yank` / `gh release delete-asset`)
- Delete legacy secrets (`gh secret delete <name>` for any secret
  no longer needed post-OIDC migration)
- Update Wayback Machine for any public surface that materially
  changed (manual)
