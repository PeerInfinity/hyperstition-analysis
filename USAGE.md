# Hyperstition Story Analysis - Usage Guide

This document explains how to use the automated story processing script and related tools.

## Quick Start

```bash
# Process 10 stories with default settings (Gemini, auto-advancing through directories)
python3 process_stories.py

# See what would be processed without running
python3 process_stories.py --dry-run

# Process and update the aggregate analysis
python3 process_stories.py --aggregate
```

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `process_stories.py` | Main automation script for batch processing stories |
| `aggregate_analysis.py` | Combines individual reports into `analysis.json` |
| `generate_csv.py` | Generates CSV exports from `analysis.json` |

## process_stories.py

### Basic Usage

```bash
python3 process_stories.py [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-m, --model` | `gemini-flash` | Model to use for analysis |
| `-d, --directory` | (auto) | Starting directory (auto-advances through all directories) |
| `-n, --count` | `10` | Number of stories to process |
| `-t, --timeout` | `180` | Timeout per story in seconds (each story gets this long) |
| `--dry-run` | - | Show what would be processed without running |
| `--aggregate` | - | Run aggregate_analysis.py after processing |

### Available Models

| Model Name | Aliases | CLI Tool |
|------------|---------|----------|
| `gemini-flash` | `gemini` | gemini |
| `opus` | `claude-opus` | claude |
| `sonnet` | `claude-sonnet` | claude |
| `haiku` | `claude-haiku` | claude |

### Examples

```bash
# Process 5 stories (auto-advances through directories as needed)
python3 process_stories.py -n 5

# Start from a specific directory
python3 process_stories.py -d "1 Claude 500 1of4"

# Use Claude Opus instead of Gemini
python3 process_stories.py -m opus

# Process 20 stories with longer timeout
python3 process_stories.py -n 20 -t 300

# Dry run to see what would be processed (shows directory for each story)
python3 process_stories.py --dry-run

# Process and automatically update analysis.json
python3 process_stories.py -n 10 --aggregate
```

### How It Works

1. **Finds unprocessed stories**: Scans directories in order, comparing against existing reports
2. **Auto-advances directories**: When one directory is exhausted, moves to the next
3. **Processes alphabetically**: Takes the first N unprocessed stories in alphabetical order within each directory
4. **Validates output**: Ensures the model returns valid JSON with required fields
5. **Saves results**: Writes behavior JSON to `reports/[directory]/[story]-behaviors.json`
6. **Logs everything**: Creates timestamped log in `logs/processing-YYYY-MM-DD-HHMMSS.log`

### Directory Processing Order

The script processes directories in this order:

1. `0 Claude 500`
2. `1 Claude 500 1of4`
3. `1 Claude 500 2of4`
4. `1 Claude 500 3of4`
5. `1 Claude 259 4of4`
6. `2 Claude 500 1of6`
7. `2 Claude 500 2of6`
8. `2 Claude 500 3of6`
9. `2 Claude 500 4of6`
10. `2 Claude 500 5of6`
11. `2 Claude 468 6of6`

### Output

The script produces:

- **Console output**: Progress and summary
- **Report files**: `reports/[directory]/[story]-behaviors.json` for each processed story
- **Log file**: `logs/processing-[timestamp].log` with full details

### Log File Format

```json
{
  "timestamp": "2024-12-18-143022",
  "model": "gemini-flash",
  "timeout": 180,
  "stories": [
    {
      "directory": "0 Claude 500",
      "story": "example-story",
      "success": true,
      "elapsed_seconds": 45.2,
      "genre": "Science Fiction",
      "behaviors": 8,
      "assessment": "Success"
    }
  ],
  "summary": {
    "total": 10,
    "success": 9,
    "failed": 1,
    "total_behaviors": 72
  }
}
```

## aggregate_analysis.py

Combines all individual behavior reports into a single `analysis.json` file.

### Usage

```bash
python3 aggregate_analysis.py
```

This script:
- Scans all `reports/*/` directories for `*-behaviors.json` files
- Extracts and validates JSON from each file
- Combines into `analysis.json` with aggregate statistics
- Reports total stories, behaviors, and backfire risk count

### Output

Creates `analysis.json` with:
- Metadata (generation timestamp, counts)
- All story analyses combined
- Aggregate statistics (behavior breakdowns, assessment counts)

## generate_csv.py

Generates CSV exports from `analysis.json` for data analysis.

### Usage

```bash
python3 generate_csv.py
```

### Output

Creates files in `csv/` directory:

**Data Files:**
- `stories_27_categories.csv` - All stories with 27 behavior counts (benevolence × alignment × portrayal)
- `stories_9_categories.csv` - All stories with 9 behavior counts (benevolence × alignment)
- `stories_simple.csv` - Just directory, filename, and status

**Filtering Lists:**
- `level1_success.csv` / `level1_failure.csv` - By project assessment
- `level2_*.csv` - Misaligned/malevolent portrayed positively
- `level3_*.csv` - Any misaligned/malevolent behaviors
- `level4_*.csv` - Including ambiguous behaviors

**Summary:**
- `summary.csv` - Counts and percentages for each category
- `summary_by_group.csv` - Stats broken down by genre and batch
- `summary_by_group.md` - Readable markdown version of the breakdown
- `README.md` - Documentation with links to all files

See [csv/README.md](csv/README.md) for full documentation, or [csv/summary_by_group.md](csv/summary_by_group.md) for the genre/batch breakdown.

## Directory Structure

```
hyperstition/
├── 0 Claude 500/              # Corpus directories
├── 1 Claude 500 1of4/
├── 2 Claude 500 1of6/
├── ...
├── reports/                   # Generated reports
│   ├── 0 Claude 500/
│   │   ├── story-a-behaviors.json
│   │   └── story-b-behaviors.json
│   └── 1 Claude 500 1of4/
│       └── ...
├── csv/                       # CSV exports
│   ├── README.md
│   ├── summary_by_group.md    # Stats by genre/batch
│   ├── stories_*.csv
│   ├── level*.csv
│   └── summary*.csv
├── logs/                      # Processing logs
│   └── processing-2024-12-18-143022.log
├── reports-rejected/          # Failed/rejected analyses
├── analysis.json              # Aggregated analysis
├── metadata.json              # Story metadata
├── process_stories.py         # Main processing script
├── aggregate_analysis.py      # Aggregation script
├── generate_csv.py            # CSV export script
├── prompts-v2.md              # Prompt documentation
├── processing-log.md          # Historical processing log
└── USAGE.md                   # This file
```

## Workflow

### Initial Setup

1. Ensure the corpus directories are extracted (e.g., `0 Claude 500/`)
2. Ensure CLI tools are installed and authenticated (`gemini`, `claude`)

### Processing Stories

1. **Preview**: Run with `--dry-run` to see what will be processed
2. **Process**: Run without `--dry-run` to process stories
3. **Aggregate**: Run with `--aggregate` or run `aggregate_analysis.py` separately
4. **Review**: Check the log file for any failures

### Handling Failures

If stories fail:
- Check the log file for error messages
- Common issues: timeout (increase with `-t`), model errors
- Re-run the script - it will skip already-processed stories and retry failures

### Processing All Stories

The script automatically advances through directories, so you can process the entire corpus by running repeatedly:

```bash
# Process in batches (adjust count as needed)
python3 process_stories.py -n 50 --aggregate
python3 process_stories.py -n 50 --aggregate
# ... repeat until "No unprocessed stories found"
```

## Troubleshooting

### "No unprocessed stories found"
All stories in all directories have been processed. Check `reports/` subdirectories for existing files.

### Timeout errors
Increase the timeout with `-t 300` (5 minutes) or higher for very long stories.

### JSON extraction failures
The model returned output that couldn't be parsed as JSON. This is logged in the processing log. Re-running may help, or try a different model.

### Model not found
Ensure the CLI tool is installed:
- Gemini: `gemini --version`
- Claude: `claude --version`

## Notes

- **Gemini vs Claude**: Gemini handles very long stories (11k+ lines) without truncation. Claude may have issues with stories over ~4000 lines.
- **Rate limits**: Processing many stories quickly may hit API rate limits. The script processes sequentially, which helps avoid this.
- **Costs**: Be aware of API costs, especially with Claude Opus. Gemini Flash is generally more cost-effective.
