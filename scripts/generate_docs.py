#!/usr/bin/env python3
"""generate_docs.py

Simple script to generate project documentation.
It reads the current version from `agent/VERSION.md`,
includes the changelog from `agent/CHANGELOG.md`, and
updates the top of `README.md` with placeholders.

This is a minimal implementation; it can be extended
with Jinja2 templates or MkDocs integration.
"""
import re
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
VERSION_FILE = BASE_DIR / "agent" / "VERSION.md"
CHANGELOG_FILE = BASE_DIR / "agent" / "CHANGELOG.md"
README_FILE = BASE_DIR / "README.md"

def get_version() -> str:
    """Extract the latest version string from VERSION.md"""
    version_pattern = re.compile(r"\*\*Current Version:\*\*\s*(\S+)")
    for line in VERSION_FILE.read_text().splitlines():
        m = version_pattern.search(line)
        if m:
            return m.group(1).strip()
    # fallback: first line after a heading like ## vX.Y
    for line in VERSION_FILE.read_text().splitlines():
        if line.startswith("## v"):
            return line.split()[0][3:]
    return "0.0.0"

def get_changelog() -> str:
    if CHANGELOG_FILE.exists():
        return CHANGELOG_FILE.read_text()
    return "No changelog available."

def update_readme(version: str, changelog: str):
    content = README_FILE.read_text().splitlines()
    # Find the line with "**Version:**" and replace it
    new_lines = []
    version_updated = False
    for line in content:
        if line.startswith("**Version:**"):
            new_lines.append(f"**Version:** {version}  ")
            version_updated = True
        else:
            new_lines.append(line)
    if not version_updated:
        # prepend version line after title if not found
        new_lines.insert(1, f"**Version:** {version}  ")
    # Append a changelog section at the end if not present
    if "## Changelog" not in "\n".join(new_lines):
        new_lines.append("\n## Changelog\n")
        new_lines.append(changelog)
    README_FILE.write_text("\n".join(new_lines))

def main():
    version = get_version()
    changelog = get_changelog()
    update_readme(version, changelog)
    print(f"README.md updated with version {version}")

if __name__ == "__main__":
    main()
