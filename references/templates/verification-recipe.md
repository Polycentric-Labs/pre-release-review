# Release verification recipe (bootstrap-emitted; 1N in v5.1)

> Closes OpenSSF OSPS-DO-03 (publish authenticity/integrity verification instructions) at Maturity 3. Publish this doc at `docs/verification.md` in the project repo so downstream consumers can verify releases before installation.

## Why verify?

Even with package-registry signing, supply-chain attacks (account compromise, registry compromise, MITM during install) can substitute a tampered artifact. This recipe lets a consumer independently verify that the artifact they received was actually built by THIS project's CI from the tagged commit.

## What this project signs

| Artifact | Signature mechanism | Verifiable with |
|---|---|---|
| Python wheels (PyPI) | PEP 740 attestations via OIDC Trusted Publisher | `pypi-attestations` CLI |
| Container images (GHCR) | cosign keyless via Sigstore | `cosign verify` |
| SBOM (CycloneDX JSON) | Attached to GitHub Release; SHA-256 in release-notes | `sha256sum` |
| Git tags | Cosign keyless OR maintainer GPG signature | `git verify-tag` (if GPG) or cosign |

## Recipes

### Python wheel verification (PEP 740)

```bash
pip install pypi-attestations
pypi-attestations verify pypi --repository https://github.com/<OWNER>/<REPO> <package_name>==<version>
```

Expected: 7/7 wheels verified for a 6-package monorepo (or N/N for your package count). Any "FAILED" line is a critical finding — do not install.

### Container verification (cosign keyless)

```bash
# Pull the image to verify
docker pull ghcr.io/<owner>/<repo>:<version>

# Verify the cosign signature
cosign verify ghcr.io/<owner>/<repo>:<version> \
  --certificate-identity-regexp "^https://github.com/<OWNER>/<REPO>/" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

Expected: a JSON envelope with `predicateType: "https://slsa.dev/provenance/v1"` and a `subject.digest.sha256` matching the pulled image.

### SBOM integrity (SHA-256)

```bash
# Download SBOM and listed hash
gh release download <version> --pattern "sbom-*.cdx.json"
gh release view <version> --json body --jq '.body' | grep -A1 "SHA-256"

# Recompute and compare
sha256sum sbom-<version>.cdx.json
```

The recomputed hash must match the GitHub Release body's "SHA-256:" line exactly.

### Reproducible-build verification (when in-scope)

For projects declaring SLSA Build L3 reproducibility:

```bash
# Clone at the exact release tag
git clone --branch <version> https://github.com/<OWNER>/<REPO>.git
cd <REPO>

# Rebuild using the documented build command
<BUILD_COMMAND>  # e.g., uv build; npm run build; cargo build --release

# Diff the rebuilt artifact against the published one
diffoscope <local_artifact> <downloaded_artifact>
```

Expected: zero output. Any diff is a CRITICAL finding.

## Reporting verification failures

If any of these recipes returns an unexpected result, **DO NOT install or run** the artifact. File a security advisory per `SECURITY.md`. The maintainer treats verification failures as supply-chain compromise until proven otherwise.

## Verification policy

This project commits to:

1. Publishing all release artifacts with at least one signature mechanism above.
2. Maintaining the OIDC Trusted Publisher configuration (PyPI) and the GHCR cosign integration (containers) so verification recipes continue to work for the supported version window.
3. Documenting any change to the signature stack in the CHANGELOG under a **"## Verification"** section in the affected release.
