#!/usr/bin/env python3
"""Extract release notes for a specific version from CHANGELOG.md."""

import re
import sys
from pathlib import Path


def extract_release_notes(version: str, changelog_path: Path = Path("CHANGELOG.md")) -> str:
    """
    Extract release notes for a specific version from CHANGELOG.md.

    Args:
        version: Version string (e.g., "0.2.0")
        changelog_path: Path to CHANGELOG.md file

    Returns:
        Release notes text for the specified version
    """
    if not changelog_path.exists():
        return f"No changelog found at {changelog_path}"

    content = changelog_path.read_text()

    # Pattern to match version header
    # Matches: ## [0.2.0] - 2025-11-08 - "Title"
    # Or: ## [0.2.0] - 2025-11-08
    version_pattern = rf"##\s+\[{re.escape(version)}\].*?\n"

    # Find the version section
    match = re.search(version_pattern, content)
    if not match:
        return f"Version {version} not found in changelog"

    # Extract from this version to the next version or end of file
    start = match.end()

    # Find next version header or end
    next_version_pattern = r"\n##\s+\["
    next_match = re.search(next_version_pattern, content[start:])

    if next_match:
        end = start + next_match.start()
        notes = content[start:end].strip()
    else:
        # Find the links section at the end
        links_pattern = r"\n\[Unreleased\]:"
        links_match = re.search(links_pattern, content[start:])
        if links_match:
            end = start + links_match.start()
            notes = content[start:end].strip()
        else:
            notes = content[start:].strip()

    # Add header
    header = f"# Release v{version}\n\n"

    # Add release metadata
    metadata = f"**Release Date:** {get_release_date(content, version)}\n"
    metadata += f"**Git Tag:** v{version}\n\n"

    return header + metadata + notes


def get_release_date(content: str, version: str) -> str:
    """Extract release date from changelog."""
    pattern = rf"##\s+\[{re.escape(version)}\]\s+-\s+(\d{{4}}-\d{{2}}-\d{{2}})"
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return "Unknown"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: extract_release_notes.py <version>", file=sys.stderr)
        print("Example: extract_release_notes.py 0.2.0", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1].lstrip('v')  # Remove 'v' prefix if present
    changelog_path = Path("CHANGELOG.md")

    if len(sys.argv) > 2:
        changelog_path = Path(sys.argv[2])

    notes = extract_release_notes(version, changelog_path)
    print(notes)


if __name__ == "__main__":
    main()
