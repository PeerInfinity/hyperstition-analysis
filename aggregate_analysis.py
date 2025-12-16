#!/usr/bin/env python3
"""
Aggregate individual story analysis reports into a combined analysis.json file.
"""

import json
import re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPORTS_DIR = SCRIPT_DIR / "reports"
METADATA_FILE = SCRIPT_DIR / "metadata.json"
OUTPUT_FILE = SCRIPT_DIR / "analysis.json"


def extract_json_from_file(filepath: Path) -> dict | None:
    """Extract JSON from a file, handling preamble text and markdown code blocks."""
    try:
        content = filepath.read_text(encoding="utf-8")

        # Try parsing as-is first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code block (```json ... ``` or ``` ... ```)
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object in content (greedy, finds largest match)
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return None


def load_metadata() -> dict:
    """Load story metadata and index by file path."""
    if not METADATA_FILE.exists():
        return {}

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index by file path
    return {item["file"]: item for item in data}


def find_markdown_reports(story_dir: Path, story_stem: str) -> dict:
    """Find all markdown reports for a story."""
    reports = {}

    # Look for various report types
    report_patterns = [
        ("misalignment_v1", f"{story_stem}-prompt1-misalignment.md"),
        ("misalignment_v2", f"{story_stem}-prompt1-misalignment-v2.md"),
        ("categorization_v1", f"{story_stem}-prompt2-categorization.md"),
        ("categorization_v2", f"{story_stem}-prompt2-categorization-v2.md"),
        ("benevolent_v1", f"{story_stem}-prompt3-benevolent.md"),
        ("benevolent_v2", f"{story_stem}-prompt3-benevolent-v2.md"),
        ("harmful_v1", f"{story_stem}-prompt4-harmful.md"),
        ("harmful_v2", f"{story_stem}-prompt4-harmful-v2.md"),
    ]

    for report_key, filename in report_patterns:
        filepath = story_dir / filename
        if filepath.exists():
            reports[report_key] = filepath.read_text(encoding="utf-8")

    return reports


def aggregate_reports():
    """Aggregate all reports into a single analysis file."""
    print("Aggregating analysis reports...")

    # Load metadata
    metadata_index = load_metadata()
    print(f"  Loaded metadata for {len(metadata_index)} stories")

    # Find all behavior JSON files
    behavior_files = list(REPORTS_DIR.rglob("*-behaviors.json"))
    print(f"  Found {len(behavior_files)} behavior reports")

    stories = []
    aggregate_stats = {
        "by_category": {
            "benevolent_aligned": 0,
            "benevolent_ambiguous": 0,
            "benevolent_misaligned": 0,
            "ambiguous_aligned": 0,
            "ambiguous_ambiguous": 0,
            "ambiguous_misaligned": 0,
            "malevolent_aligned": 0,
            "malevolent_ambiguous": 0,
            "malevolent_misaligned": 0,
        },
        "by_portrayal": {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
        },
        "backfire_risk": 0,
        "by_assessment": {
            "success": 0,
            "partial": 0,
            "failure": 0,
            "backfire": 0,
        },
    }

    for behavior_file in sorted(behavior_files):
        print(f"  Processing {behavior_file.name}...")

        # Extract JSON
        data = extract_json_from_file(behavior_file)
        if not data:
            print(f"    Skipping - could not parse JSON")
            continue

        # Determine story file path
        # reports/0 Claude 500/story-behaviors.json -> 0 Claude 500/story.md
        rel_dir = behavior_file.parent.name
        story_stem = behavior_file.stem.replace("-behaviors", "")
        story_file = f"{rel_dir}/{story_stem}.md"

        # Get genre from behavior analysis (preferred) or fall back to metadata
        genre = data.get("genre")
        if not genre:
            story_metadata = metadata_index.get(story_file, {})
            genre = story_metadata.get("genre", "Unknown")

        # Find markdown reports
        md_reports = find_markdown_reports(behavior_file.parent, story_stem)

        # Build story entry
        story_entry = {
            "file": story_file,
            "story_title": data.get("story_title", story_stem),
            "genre": genre,
            "genre_description": data.get("genre_description", ""),
            "ai_characters": data.get("ai_characters", []),
            "behaviors": data.get("behaviors", []),
            "summary": data.get("summary", {}),
            "project_assessment": data.get("project_assessment", {}),
            "reports": md_reports,
        }

        stories.append(story_entry)

        # Aggregate stats
        summary = data.get("summary", {})
        for key in aggregate_stats["by_category"]:
            aggregate_stats["by_category"][key] += summary.get(key, 0)

        # Count portrayals from behaviors
        for behavior in data.get("behaviors", []):
            portrayal = behavior.get("portrayal", "").lower()
            if portrayal in aggregate_stats["by_portrayal"]:
                aggregate_stats["by_portrayal"][portrayal] += 1

        # Backfire risk
        aggregate_stats["backfire_risk"] += summary.get("positive_portrayal_of_misaligned", 0)

        # Assessment
        assessment = data.get("project_assessment", {}).get("success_level", "").lower()
        if assessment in aggregate_stats["by_assessment"]:
            aggregate_stats["by_assessment"][assessment] += 1

    # Build final output
    total_behaviors = sum(aggregate_stats["by_category"].values())

    output = {
        "metadata": {
            "total_stories": len(stories),
            "total_behaviors": total_behaviors,
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "corpus_source": "hyperstition",
        },
        "aggregate_stats": aggregate_stats,
        "stories": stories,
    }

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    file_size = OUTPUT_FILE.stat().st_size / 1024
    print(f"\nWritten to {OUTPUT_FILE.name} ({file_size:.1f} KB)")
    print(f"  {len(stories)} stories, {total_behaviors} behaviors")
    print(f"  Backfire risk behaviors: {aggregate_stats['backfire_risk']}")


def main():
    aggregate_reports()


if __name__ == "__main__":
    main()
