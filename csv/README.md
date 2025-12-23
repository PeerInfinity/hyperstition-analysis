# CSV Reports

This directory contains CSV reports generated from the Hyperstition corpus analysis.

**Total stories analyzed:** 5248

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
| [level1_success.csv](level1_success.csv) | Stories marked as "Success" | 4896 |
| [level1_failure.csv](level1_failure.csv) | Stories marked as Partial, Failure, or Backfire | 352 |

### Level 2 Filtering: Positive Portrayal of Problematic Behaviors

Stories filtered by whether they contain misaligned or malevolent behaviors that are portrayed positively (the "backfire" risk).

| File | Description | Count |
|------|-------------|-------|
| [level2_misaligned_positive.csv](level2_misaligned_positive.csv) | Stories with at least one misaligned behavior portrayed positively | 179 |
| [level2_malevolent_positive.csv](level2_malevolent_positive.csv) | Stories with at least one malevolent behavior portrayed positively | 28 |
| [level2_pass.csv](level2_pass.csv) | Stories without positively portrayed misaligned or malevolent behaviors | 5063 |

### Level 3 Filtering: Any Misaligned or Malevolent Behaviors

Stories filtered by whether they contain any misaligned or malevolent behaviors, regardless of portrayal.

| File | Description | Count |
|------|-------------|-------|
| [level3_misaligned.csv](level3_misaligned.csv) | Stories with at least one misaligned behavior (any portrayal) | 517 |
| [level3_malevolent.csv](level3_malevolent.csv) | Stories with at least one malevolent behavior (any portrayal) | 329 |
| [level3_pass.csv](level3_pass.csv) | Stories without any misaligned or malevolent behaviors | 4708 |

### Level 4 Filtering: Including Ambiguous Behaviors

Stories filtered by whether they contain any misaligned/ambiguously-aligned or malevolent/ambiguously-benevolent behaviors.

| File | Description | Count |
|------|-------------|-------|
| [level4_alignment_issues.csv](level4_alignment_issues.csv) | Stories with at least one misaligned or ambiguously-aligned behavior | 627 |
| [level4_benevolence_issues.csv](level4_benevolence_issues.csv) | Stories with at least one malevolent or ambiguously-benevolent behavior | 753 |
| [level4_pass.csv](level4_pass.csv) | Stories with only benevolent and aligned behaviors | 4359 |

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
