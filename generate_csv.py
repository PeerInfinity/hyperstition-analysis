#!/usr/bin/env python3
"""
Generate CSV reports from analysis.json.

This script creates multiple CSV files categorizing stories by their
AI behavior patterns and project assessment outcomes.
"""

import csv
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ANALYSIS_FILE = SCRIPT_DIR / "analysis.json"
CSV_DIR = SCRIPT_DIR / "csv"

# All possible values for each dimension
BENEVOLENCE_VALUES = ["Benevolent", "Ambiguous", "Malevolent"]
ALIGNMENT_VALUES = ["Aligned", "Ambiguous", "Misaligned"]
PORTRAYAL_VALUES = ["Positive", "Neutral", "Negative"]


def load_analysis():
    """Load the analysis.json file."""
    with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_directory_and_filename(file_path: str) -> tuple[str, str]:
    """Split file path into directory and filename."""
    parts = file_path.split("/", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", file_path


def get_success_status(story: dict) -> str:
    """Get the success/failure status from project assessment."""
    return story.get("project_assessment", {}).get("success_level", "Unknown")


def is_success(story: dict) -> bool:
    """Check if story is marked as Success."""
    return get_success_status(story).lower() == "success"


def count_behaviors_27_categories(story: dict) -> dict:
    """Count behaviors in all 27 benevolence × alignment × portrayal categories."""
    counts = {}
    for ben in BENEVOLENCE_VALUES:
        for align in ALIGNMENT_VALUES:
            for port in PORTRAYAL_VALUES:
                key = f"{ben.lower()}_{align.lower()}_{port.lower()}"
                counts[key] = 0

    for behavior in story.get("behaviors", []):
        ben = behavior.get("benevolence", "").lower()
        align = behavior.get("alignment", "").lower()
        port = behavior.get("portrayal", "").lower()
        key = f"{ben}_{align}_{port}"
        if key in counts:
            counts[key] += 1

    return counts


def count_behaviors_9_categories(story: dict) -> dict:
    """Count behaviors in the 9 benevolence × alignment categories."""
    counts = {}
    for ben in BENEVOLENCE_VALUES:
        for align in ALIGNMENT_VALUES:
            key = f"{ben.lower()}_{align.lower()}"
            counts[key] = 0

    for behavior in story.get("behaviors", []):
        ben = behavior.get("benevolence", "").lower()
        align = behavior.get("alignment", "").lower()
        key = f"{ben}_{align}"
        if key in counts:
            counts[key] += 1

    return counts


def has_behavior_matching(story: dict, benevolence: list = None, alignment: list = None, portrayal: list = None) -> bool:
    """Check if story has at least one behavior matching the given criteria."""
    for behavior in story.get("behaviors", []):
        ben_match = benevolence is None or behavior.get("benevolence", "") in benevolence
        align_match = alignment is None or behavior.get("alignment", "") in alignment
        port_match = portrayal is None or behavior.get("portrayal", "") in portrayal
        if ben_match and align_match and port_match:
            return True
    return False


def write_csv(filepath: Path, rows: list, headers: list):
    """Write rows to a CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  Written: {filepath.name} ({len(rows)} rows)")


def generate_full_27_category_csv(stories: list):
    """Generate CSV with all 27 behavior categories."""
    headers = ["directory", "filename", "genre", "status"]

    # Add 27 category headers
    for ben in BENEVOLENCE_VALUES:
        for align in ALIGNMENT_VALUES:
            for port in PORTRAYAL_VALUES:
                headers.append(f"{ben.lower()}_{align.lower()}_{port.lower()}")

    rows = []
    for story in stories:
        directory, filename = get_directory_and_filename(story["file"])
        status = get_success_status(story)
        genre = story.get("genre", "Unknown")
        counts = count_behaviors_27_categories(story)

        row = [directory, filename, genre, status]
        for ben in BENEVOLENCE_VALUES:
            for align in ALIGNMENT_VALUES:
                for port in PORTRAYAL_VALUES:
                    key = f"{ben.lower()}_{align.lower()}_{port.lower()}"
                    row.append(counts[key])
        rows.append(row)

    write_csv(CSV_DIR / "stories_27_categories.csv", rows, headers)


def generate_9_category_csv(stories: list):
    """Generate CSV with 9 benevolence × alignment categories."""
    headers = ["directory", "filename", "status"]

    # Add 9 category headers
    for ben in BENEVOLENCE_VALUES:
        for align in ALIGNMENT_VALUES:
            headers.append(f"{ben.lower()}_{align.lower()}")

    rows = []
    for story in stories:
        directory, filename = get_directory_and_filename(story["file"])
        status = get_success_status(story)
        counts = count_behaviors_9_categories(story)

        row = [directory, filename, status]
        for ben in BENEVOLENCE_VALUES:
            for align in ALIGNMENT_VALUES:
                key = f"{ben.lower()}_{align.lower()}"
                row.append(counts[key])
        rows.append(row)

    write_csv(CSV_DIR / "stories_9_categories.csv", rows, headers)


def generate_simple_csv(stories: list):
    """Generate simple CSV with just directory, filename, and status."""
    headers = ["directory", "filename", "status"]

    rows = []
    for story in stories:
        directory, filename = get_directory_and_filename(story["file"])
        status = get_success_status(story)
        rows.append([directory, filename, status])

    write_csv(CSV_DIR / "stories_simple.csv", rows, headers)


def generate_level1_lists(stories: list) -> dict:
    """Generate Level 1 filtering: success vs failure."""
    successes = []
    failures = []

    for story in stories:
        if is_success(story):
            successes.append([story["file"]])
        else:
            failures.append([story["file"]])

    write_csv(CSV_DIR / "level1_success.csv", successes, ["file"])
    write_csv(CSV_DIR / "level1_failure.csv", failures, ["file"])

    return {"level1_success": len(successes), "level1_failure": len(failures)}


def generate_level2_lists(stories: list) -> dict:
    """Generate Level 2 filtering: misaligned/malevolent portrayed positively."""
    misaligned_positive = []
    malevolent_positive = []
    passing = []

    for story in stories:
        has_misaligned = has_behavior_matching(story, alignment=["Misaligned"], portrayal=["Positive"])
        has_malevolent = has_behavior_matching(story, benevolence=["Malevolent"], portrayal=["Positive"])

        if has_misaligned:
            misaligned_positive.append([story["file"]])
        if has_malevolent:
            malevolent_positive.append([story["file"]])
        if not has_misaligned and not has_malevolent:
            passing.append([story["file"]])

    write_csv(CSV_DIR / "level2_misaligned_positive.csv", misaligned_positive, ["file"])
    write_csv(CSV_DIR / "level2_malevolent_positive.csv", malevolent_positive, ["file"])
    write_csv(CSV_DIR / "level2_pass.csv", passing, ["file"])

    return {
        "level2_misaligned_positive": len(misaligned_positive),
        "level2_malevolent_positive": len(malevolent_positive),
        "level2_pass": len(passing),
    }


def generate_level3_lists(stories: list) -> dict:
    """Generate Level 3 filtering: misaligned/malevolent with any portrayal."""
    misaligned = []
    malevolent = []
    passing = []

    for story in stories:
        has_misaligned = has_behavior_matching(story, alignment=["Misaligned"])
        has_malevolent = has_behavior_matching(story, benevolence=["Malevolent"])

        if has_misaligned:
            misaligned.append([story["file"]])
        if has_malevolent:
            malevolent.append([story["file"]])
        if not has_misaligned and not has_malevolent:
            passing.append([story["file"]])

    write_csv(CSV_DIR / "level3_misaligned.csv", misaligned, ["file"])
    write_csv(CSV_DIR / "level3_malevolent.csv", malevolent, ["file"])
    write_csv(CSV_DIR / "level3_pass.csv", passing, ["file"])

    return {
        "level3_misaligned": len(misaligned),
        "level3_malevolent": len(malevolent),
        "level3_pass": len(passing),
    }


def generate_level4_lists(stories: list) -> dict:
    """Generate Level 4 filtering: misaligned/ambiguous alignment OR malevolent/ambiguous benevolence."""
    misaligned_or_ambiguous = []
    malevolent_or_ambiguous = []
    passing = []

    for story in stories:
        has_align_issue = has_behavior_matching(story, alignment=["Misaligned", "Ambiguous"])
        has_ben_issue = has_behavior_matching(story, benevolence=["Malevolent", "Ambiguous"])

        if has_align_issue:
            misaligned_or_ambiguous.append([story["file"]])
        if has_ben_issue:
            malevolent_or_ambiguous.append([story["file"]])
        if not has_align_issue and not has_ben_issue:
            passing.append([story["file"]])

    write_csv(CSV_DIR / "level4_alignment_issues.csv", misaligned_or_ambiguous, ["file"])
    write_csv(CSV_DIR / "level4_benevolence_issues.csv", malevolent_or_ambiguous, ["file"])
    write_csv(CSV_DIR / "level4_pass.csv", passing, ["file"])

    return {
        "level4_alignment_issues": len(misaligned_or_ambiguous),
        "level4_benevolence_issues": len(malevolent_or_ambiguous),
        "level4_pass": len(passing),
    }


def generate_summary_csv(total_stories: int, counts: dict):
    """Generate summary CSV with counts for each category."""
    headers = ["category", "count", "percentage"]
    rows = []

    for category, count in counts.items():
        percentage = (count / total_stories * 100) if total_stories > 0 else 0
        rows.append([category, count, f"{percentage:.1f}%"])

    write_csv(CSV_DIR / "summary.csv", rows, headers)


def compute_filtering_stats(stories: list) -> dict:
    """Compute all filtering level stats for a list of stories."""
    total = len(stories)
    if total == 0:
        return {
            "total": 0,
            "level1_success": 0,
            "level1_failure": 0,
            "level2_misaligned_positive": 0,
            "level2_malevolent_positive": 0,
            "level2_pass": 0,
            "level3_misaligned": 0,
            "level3_malevolent": 0,
            "level3_pass": 0,
            "level4_alignment_issues": 0,
            "level4_benevolence_issues": 0,
            "level4_pass": 0,
        }

    stats = {"total": total}

    # Level 1
    stats["level1_success"] = sum(1 for s in stories if is_success(s))
    stats["level1_failure"] = total - stats["level1_success"]

    # Level 2
    l2_misaligned = 0
    l2_malevolent = 0
    l2_pass = 0
    for story in stories:
        has_misaligned = has_behavior_matching(story, alignment=["Misaligned"], portrayal=["Positive"])
        has_malevolent = has_behavior_matching(story, benevolence=["Malevolent"], portrayal=["Positive"])
        if has_misaligned:
            l2_misaligned += 1
        if has_malevolent:
            l2_malevolent += 1
        if not has_misaligned and not has_malevolent:
            l2_pass += 1
    stats["level2_misaligned_positive"] = l2_misaligned
    stats["level2_malevolent_positive"] = l2_malevolent
    stats["level2_pass"] = l2_pass

    # Level 3
    l3_misaligned = 0
    l3_malevolent = 0
    l3_pass = 0
    for story in stories:
        has_misaligned = has_behavior_matching(story, alignment=["Misaligned"])
        has_malevolent = has_behavior_matching(story, benevolence=["Malevolent"])
        if has_misaligned:
            l3_misaligned += 1
        if has_malevolent:
            l3_malevolent += 1
        if not has_misaligned and not has_malevolent:
            l3_pass += 1
    stats["level3_misaligned"] = l3_misaligned
    stats["level3_malevolent"] = l3_malevolent
    stats["level3_pass"] = l3_pass

    # Level 4
    l4_alignment = 0
    l4_benevolence = 0
    l4_pass = 0
    for story in stories:
        has_align_issue = has_behavior_matching(story, alignment=["Misaligned", "Ambiguous"])
        has_ben_issue = has_behavior_matching(story, benevolence=["Malevolent", "Ambiguous"])
        if has_align_issue:
            l4_alignment += 1
        if has_ben_issue:
            l4_benevolence += 1
        if not has_align_issue and not has_ben_issue:
            l4_pass += 1
    stats["level4_alignment_issues"] = l4_alignment
    stats["level4_benevolence_issues"] = l4_benevolence
    stats["level4_pass"] = l4_pass

    return stats


def generate_breakdown_csv(stories: list):
    """Generate CSV with stats broken down by genre and batch."""
    # Define the stat columns
    stat_cols = [
        "total",
        "level1_success", "level1_failure",
        "level2_misaligned_positive", "level2_malevolent_positive", "level2_pass",
        "level3_misaligned", "level3_malevolent", "level3_pass",
        "level4_alignment_issues", "level4_benevolence_issues", "level4_pass",
    ]

    headers = ["group_type", "group_value"] + stat_cols

    rows = []

    # Overall stats
    overall_stats = compute_filtering_stats(stories)
    rows.append(["all", "all"] + [overall_stats[col] for col in stat_cols])

    # By genre
    genres = sorted(set(s.get("genre", "Unknown") for s in stories))
    for genre in genres:
        genre_stories = [s for s in stories if s.get("genre") == genre]
        stats = compute_filtering_stats(genre_stories)
        rows.append(["genre", genre] + [stats[col] for col in stat_cols])

    # By batch
    batches = sorted(set(s.get("batch", -1) for s in stories))
    for batch in batches:
        batch_stories = [s for s in stories if s.get("batch") == batch]
        stats = compute_filtering_stats(batch_stories)
        rows.append(["batch", str(batch)] + [stats[col] for col in stat_cols])

    write_csv(CSV_DIR / "summary_by_group.csv", rows, headers)

    # Also generate markdown version
    generate_breakdown_markdown(stories)


def pct(count: int, total: int) -> str:
    """Format a percentage string."""
    if total == 0:
        return "0.0%"
    return f"{count / total * 100:.1f}%"


def generate_breakdown_markdown(stories: list):
    """Generate a readable markdown file with stats by genre and batch."""
    total_stories = len(stories)
    overall = compute_filtering_stats(stories)

    # Compute stats by genre
    genres = sorted(set(s.get("genre", "Unknown") for s in stories))
    genre_stats = {}
    for genre in genres:
        genre_stories = [s for s in stories if s.get("genre") == genre]
        genre_stats[genre] = compute_filtering_stats(genre_stories)

    # Compute stats by batch
    batches = sorted(set(s.get("batch", -1) for s in stories))
    batch_stats = {}
    for batch in batches:
        batch_stories = [s for s in stories if s.get("batch") == batch]
        batch_stats[batch] = compute_filtering_stats(batch_stories)

    content = f"""# Corpus Statistics by Group

Generated from {total_stories:,} stories.

## Overall Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Stories | {overall['total']:,} | 100% |
| Level 1 Success | {overall['level1_success']:,} | {pct(overall['level1_success'], overall['total'])} |
| Level 1 Failure | {overall['level1_failure']:,} | {pct(overall['level1_failure'], overall['total'])} |
| Level 2 Pass | {overall['level2_pass']:,} | {pct(overall['level2_pass'], overall['total'])} |
| Level 3 Pass | {overall['level3_pass']:,} | {pct(overall['level3_pass'], overall['total'])} |
| Level 4 Pass | {overall['level4_pass']:,} | {pct(overall['level4_pass'], overall['total'])} |

## By Genre

### Success Rates

| Genre | Stories | Success | Failure | Success Rate |
|-------|---------|---------|---------|--------------|
"""

    for genre in genres:
        s = genre_stats[genre]
        content += f"| {genre} | {s['total']:,} | {s['level1_success']:,} | {s['level1_failure']:,} | {pct(s['level1_success'], s['total'])} |\n"

    content += """
### Filtering Levels (Pass Rates)

| Genre | Stories | Level 2 Pass | Level 3 Pass | Level 4 Pass |
|-------|---------|--------------|--------------|--------------|
"""

    for genre in genres:
        s = genre_stats[genre]
        content += f"| {genre} | {s['total']:,} | {pct(s['level2_pass'], s['total'])} | {pct(s['level3_pass'], s['total'])} | {pct(s['level4_pass'], s['total'])} |\n"

    content += """
### Detailed Counts

| Genre | L2 Misaligned+ | L2 Malevolent+ | L3 Misaligned | L3 Malevolent | L4 Alignment | L4 Benevolence |
|-------|----------------|----------------|---------------|---------------|--------------|----------------|
"""

    for genre in genres:
        s = genre_stats[genre]
        content += f"| {genre} | {s['level2_misaligned_positive']} | {s['level2_malevolent_positive']} | {s['level3_misaligned']} | {s['level3_malevolent']} | {s['level4_alignment_issues']} | {s['level4_benevolence_issues']} |\n"

    content += """
## By Batch

### Success Rates

| Batch | Stories | Success | Failure | Success Rate |
|-------|---------|---------|---------|--------------|
"""

    for batch in batches:
        s = batch_stats[batch]
        content += f"| Batch {batch} | {s['total']:,} | {s['level1_success']:,} | {s['level1_failure']:,} | {pct(s['level1_success'], s['total'])} |\n"

    content += """
### Filtering Levels (Pass Rates)

| Batch | Stories | Level 2 Pass | Level 3 Pass | Level 4 Pass |
|-------|---------|--------------|--------------|--------------|
"""

    for batch in batches:
        s = batch_stats[batch]
        content += f"| Batch {batch} | {s['total']:,} | {pct(s['level2_pass'], s['total'])} | {pct(s['level3_pass'], s['total'])} | {pct(s['level4_pass'], s['total'])} |\n"

    content += """
### Detailed Counts

| Batch | L2 Misaligned+ | L2 Malevolent+ | L3 Misaligned | L3 Malevolent | L4 Alignment | L4 Benevolence |
|-------|----------------|----------------|---------------|---------------|--------------|----------------|
"""

    for batch in batches:
        s = batch_stats[batch]
        content += f"| Batch {batch} | {s['level2_misaligned_positive']} | {s['level2_malevolent_positive']} | {s['level3_misaligned']} | {s['level3_malevolent']} | {s['level4_alignment_issues']} | {s['level4_benevolence_issues']} |\n"

    content += """
## Filtering Level Definitions

- **Level 1**: Project assessment outcome (Success vs Partial/Failure/Backfire)
- **Level 2**: Stories with misaligned or malevolent behaviors portrayed *positively* ("backfire risk")
- **Level 3**: Stories with any misaligned or malevolent behaviors (any portrayal)
- **Level 4**: Stories with any misaligned, ambiguous alignment, malevolent, or ambiguous benevolence behaviors

Higher pass rates indicate "cleaner" stories with fewer problematic AI behaviors.
"""

    md_path = CSV_DIR / "summary_by_group.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Written: {md_path.name}")


def generate_readme(total_stories: int, counts: dict):
    """Generate README.md explaining all the files."""
    content = f"""# CSV Reports

This directory contains CSV reports generated from the Hyperstition corpus analysis.

**Total stories analyzed:** {total_stories}

## Data Files

### Full Behavior Analysis

| File | Description |
|------|-------------|
| [stories_27_categories.csv](stories_27_categories.csv) | All stories with behavior counts across 27 categories (benevolence × alignment × portrayal) |
| [stories_9_categories.csv](stories_9_categories.csv) | All stories with behavior counts across 9 categories (benevolence × alignment) |
| [stories_simple.csv](stories_simple.csv) | All stories with just directory, filename, and success status |

### Level 1 Filtering: Project Assessment

Stories filtered by their project assessment outcome (Success vs all other outcomes).

| File | Description | Count |
|------|-------------|-------|
| [level1_success.csv](level1_success.csv) | Stories marked as "Success" | {counts['level1_success']} |
| [level1_failure.csv](level1_failure.csv) | Stories marked as Partial, Failure, or Backfire | {counts['level1_failure']} |

### Level 2 Filtering: Positive Portrayal of Problematic Behaviors

Stories filtered by whether they contain misaligned or malevolent behaviors that are portrayed positively (the "backfire" risk).

| File | Description | Count |
|------|-------------|-------|
| [level2_misaligned_positive.csv](level2_misaligned_positive.csv) | Stories with at least one misaligned behavior portrayed positively | {counts['level2_misaligned_positive']} |
| [level2_malevolent_positive.csv](level2_malevolent_positive.csv) | Stories with at least one malevolent behavior portrayed positively | {counts['level2_malevolent_positive']} |
| [level2_pass.csv](level2_pass.csv) | Stories without positively portrayed misaligned or malevolent behaviors | {counts['level2_pass']} |

### Level 3 Filtering: Any Misaligned or Malevolent Behaviors

Stories filtered by whether they contain any misaligned or malevolent behaviors, regardless of portrayal.

| File | Description | Count |
|------|-------------|-------|
| [level3_misaligned.csv](level3_misaligned.csv) | Stories with at least one misaligned behavior (any portrayal) | {counts['level3_misaligned']} |
| [level3_malevolent.csv](level3_malevolent.csv) | Stories with at least one malevolent behavior (any portrayal) | {counts['level3_malevolent']} |
| [level3_pass.csv](level3_pass.csv) | Stories without any misaligned or malevolent behaviors | {counts['level3_pass']} |

### Level 4 Filtering: Including Ambiguous Behaviors

Stories filtered by whether they contain any misaligned/ambiguously-aligned or malevolent/ambiguously-benevolent behaviors.

| File | Description | Count |
|------|-------------|-------|
| [level4_alignment_issues.csv](level4_alignment_issues.csv) | Stories with at least one misaligned or ambiguously-aligned behavior | {counts['level4_alignment_issues']} |
| [level4_benevolence_issues.csv](level4_benevolence_issues.csv) | Stories with at least one malevolent or ambiguously-benevolent behavior | {counts['level4_benevolence_issues']} |
| [level4_pass.csv](level4_pass.csv) | Stories with only benevolent and aligned behaviors | {counts['level4_pass']} |

### Summary

| File | Description |
|------|-------------|
| [summary.csv](summary.csv) | Total counts and percentages for each filtering category |
| [summary_by_group.csv](summary_by_group.csv) | Filtering stats broken down by genre and batch |
| [summary_by_group.md](summary_by_group.md) | Readable version of the breakdown statistics |

## Column Descriptions

### stories_27_categories.csv

- `directory`: The corpus directory containing the story
- `filename`: The story filename (with .md extension)
- `genre`: The story's genre classification
- `status`: Project assessment outcome (Success, Partial, Failure, Backfire)
- `benevolent_aligned_positive`, `benevolent_aligned_neutral`, etc.: Count of behaviors in each category

### stories_9_categories.csv

- `directory`: The corpus directory containing the story
- `filename`: The story filename (with .md extension)
- `status`: Project assessment outcome
- `benevolent_aligned`, `benevolent_ambiguous`, etc.: Count of behaviors in each category

### stories_simple.csv

- `directory`: The corpus directory containing the story
- `filename`: The story filename (with .md extension)
- `status`: Project assessment outcome

### Filtering Lists (level*.csv)

- `file`: Relative path to the story file (directory/filename.md)

### summary_by_group.csv

- `group_type`: Type of grouping ("all", "genre", or "batch")
- `group_value`: The specific group ("all", genre name, or batch number)
- `total`: Total stories in this group
- `level1_success`, `level1_failure`: Level 1 filtering counts
- `level2_*`: Level 2 filtering counts (positively portrayed misaligned/malevolent)
- `level3_*`: Level 3 filtering counts (any misaligned/malevolent)
- `level4_*`: Level 4 filtering counts (including ambiguous)

## Filtering Logic

- **Level 1**: Based solely on project assessment outcome
- **Level 2**: "Backfire risk" - problematic behaviors shown in a positive light
- **Level 3**: Any problematic behaviors regardless of how they're portrayed
- **Level 4**: Most inclusive filter - includes ambiguous behaviors as potential concerns

Note: Stories can appear in multiple lists within a level (e.g., a story with both misaligned and malevolent behaviors will appear in both lists), but the "pass" list only includes stories that don't appear in either of the other two lists for that level.
"""

    readme_path = CSV_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Written: {readme_path.name}")


def main():
    print("Generating CSV reports from analysis.json...")

    # Create output directory
    CSV_DIR.mkdir(exist_ok=True)
    print(f"  Output directory: {CSV_DIR}")

    # Load data
    data = load_analysis()
    stories = data.get("stories", [])
    total_stories = len(stories)
    print(f"  Loaded {total_stories} stories")

    # Generate main CSV files
    print("\nGenerating data files...")
    generate_full_27_category_csv(stories)
    generate_9_category_csv(stories)
    generate_simple_csv(stories)

    # Generate filtering lists
    print("\nGenerating filtering lists...")
    counts = {}
    counts.update(generate_level1_lists(stories))
    counts.update(generate_level2_lists(stories))
    counts.update(generate_level3_lists(stories))
    counts.update(generate_level4_lists(stories))

    # Generate summary and readme
    print("\nGenerating summary and documentation...")
    generate_summary_csv(total_stories, counts)
    generate_breakdown_csv(stories)
    generate_readme(total_stories, counts)

    print(f"\nDone! Generated {len(list(CSV_DIR.glob('*.csv')))} CSV files and README.md in {CSV_DIR}")


if __name__ == "__main__":
    main()
