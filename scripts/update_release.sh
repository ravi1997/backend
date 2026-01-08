#!/usr/bin/env bash
# update_release.sh
# Bump project version, update CHANGELOG.md, VERSION.md, and regenerate docs.
# Usage: ./scripts/update_release.sh [major|minor|patch] "Commit message"

set -e

# Determine bump type (default patch)
BUMP_TYPE=${1:-patch}
COMMIT_MSG=${2:-"Release"}

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VERSION_FILE="$BASE_DIR/agent/VERSION.md"
CHANGELOG_FILE="$BASE_DIR/agent/CHANGELOG.md"

# Function to extract current version (semantic) from VERSION.md
get_current_version() {
  # Look for a line like "## vX.Y.Z" or "**Current Version:** X.Y.Z"
  if grep -E "## v[0-9]+\.[0-9]+\.[0-9]+" "$VERSION_FILE" | head -n1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"; then
    grep -E "## v[0-9]+\.[0-9]+\.[0-9]+" "$VERSION_FILE" | head -n1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"
  elif grep -E "\*\*Current Version:\*\*" "$VERSION_FILE" | head -n1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"; then
    grep -E "\*\*Current Version:\*\*" "$VERSION_FILE" | head -n1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"
  else
    echo "0.0.0"
  fi
}

bump_version() {
  local ver=$(get_current_version)
  IFS='.' read -r major minor patch <<< "$ver"
  case "$BUMP_TYPE" in
    major) major=$((major+1)); minor=0; patch=0 ;;
    minor) minor=$((minor+1)); patch=0 ;;
    patch) patch=$((patch+1)) ;;
    *) echo "Invalid bump type: $BUMP_TYPE"; exit 1 ;;
  esac
  echo "${major}.${minor}.${patch}"
}

NEW_VERSION=$(bump_version)
DATE=$(date +"%Y-%m-%d")

# Update VERSION.md – prepend new version entry
NEW_VERSION_ENTRY="## v${NEW_VERSION} (${DATE}) - Automated Release"
# Insert after the first line (which is a title) or at top if not found
TMP=$(mktemp)
awk -v entry="$NEW_VERSION_ENTRY" 'NR==1{print; print ""; print entry; next}1' "$VERSION_FILE" > "$TMP"
mv "$TMP" "$VERSION_FILE"

# Update CHANGELOG.md – prepend entry
if [ ! -f "$CHANGELOG_FILE" ]; then
  echo "# Changelog" > "$CHANGELOG_FILE"
fi
CHANGELOG_ENTRY="## v${NEW_VERSION} (${DATE})\n- ${COMMIT_MSG}\n"
# Prepend
TMP=$(mktemp)
{ echo "$CHANGELOG_ENTRY"; cat "$CHANGELOG_FILE"; } > "$TMP"
mv "$TMP" "$CHANGELOG_FILE"

# Commit changes
git add "$VERSION_FILE" "$CHANGELOG_FILE"
git commit -m "chore(release): v${NEW_VERSION} - ${COMMIT_MSG}"
# Tag the release
git tag "v${NEW_VERSION}"

echo "Version bumped to ${NEW_VERSION} and changelog updated."

# Regenerate documentation
python3 "$BASE_DIR/scripts/generate_docs.py"

# Push if remote exists
if git remote | grep -q .; then
  git push && git push --tags
fi
