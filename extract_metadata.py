#!/usr/bin/env python3
"""Extract metadata (Title, Author, Genre) from markdown files."""

import json
import re
import sys
from pathlib import Path


def extract_metadata(file_path: Path, root: Path) -> dict | None:
    """Extract title, author, and genre from a markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

    metadata = {
        'file': str(file_path.relative_to(root)),
        'title': None,
        'author': None,
        'genre': None,
    }

    # Extract title (first H1 heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()

    # Extract author
    author_match = re.search(r'\*\*Author:\*\*\s*(.+)$', content, re.MULTILINE)
    if author_match:
        metadata['author'] = author_match.group(1).strip()

    # Extract genre
    genre_match = re.search(r'\*\*Genre:\*\*\s*(.+)$', content, re.MULTILINE)
    if genre_match:
        metadata['genre'] = genre_match.group(1).strip()

    return metadata


def main():
    # Find all markdown files in subdirectories
    root = Path(__file__).parent
    md_files = sorted(root.glob('**/*.md'))

    # Exclude README files
    md_files = [f for f in md_files if f.name.lower() != 'readme.md']

    print(f"Found {len(md_files)} markdown files")

    results = []
    for file_path in md_files:
        metadata = extract_metadata(file_path, root)
        if metadata:
            results.append(metadata)

    # Write to JSON
    output_path = root / 'metadata.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Extracted metadata from {len(results)} files")
    print(f"Output written to {output_path}")


if __name__ == '__main__':
    main()
