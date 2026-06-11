#!/usr/bin/env bash
# release.sh — tag a new QtARMSim release
#
# Usage: ./release.sh <version>
# Example: ./release.sh 2.1.0
#
# The script:
#   1. Validates the version format (N.N or N.N.N, optionally followed by
#      a pre-release suffix such as rc1, a1, b2, etc.)
#   2. Ensures the working tree is clean
#   3. Updates the two version strings in flake.nix
#   4. Commits flake.nix
#   5. Creates an annotated git tag

set -euo pipefail

# ── Argument validation ──────────────────────────────────────────────────────

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <version>" >&2
    echo "Example: $0 2.1.0" >&2
    exit 1
fi

VERSION="$1"

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?([a-z]+[0-9]*)?$ ]]; then
    echo "Error: '$VERSION' is not a valid version." >&2
    echo "Expected format: N.N, N.N.N, or N.N.NrcX / N.N.NaX / N.N.NbX" >&2
    exit 1
fi

# ── Working tree check ───────────────────────────────────────────────────────

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: working tree is not clean. Commit or stash your changes first." >&2
    git status --short >&2
    exit 1
fi

# ── Check tag does not already exist ────────────────────────────────────────

if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "Error: tag '$VERSION' already exists." >&2
    exit 1
fi

# ── Update flake.nix ─────────────────────────────────────────────────────────

FLAKE="flake.nix"

sed -i \
    -e "s/version = \"[^\"]*\"/version = \"$VERSION\"/" \
    -e "s/SETUPTOOLS_SCM_PRETEND_VERSION = \"[^\"]*\"/SETUPTOOLS_SCM_PRETEND_VERSION = \"$VERSION\"/" \
    "$FLAKE"

# Verify both substitutions actually landed
COUNT=$(grep -c "\"$VERSION\"" "$FLAKE")
if [[ "$COUNT" -lt 2 ]]; then
    echo "Error: expected at least 2 occurrences of \"$VERSION\" in $FLAKE after substitution." >&2
    exit 1
fi

# ── Commit and tag ───────────────────────────────────────────────────────────

git add "$FLAKE"
git commit -m "Release $VERSION"
git tag -a "$VERSION" -m "Release $VERSION"

echo ""
echo "Done. Commit and tag '$VERSION' created."
echo "To push: git push && git push origin '$VERSION'"
