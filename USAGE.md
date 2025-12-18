# Hyperstition Story Analysis - Usage Guide

This document explains how to use the automated story processing script and related tools.

## Quick Start

```bash
# Process 10 stories with default settings (Gemini, "0 Claude 500" directory)
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

## process_stories.py

### Basic Usage

```bash
python3 process_stories.py [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-m, --model` | `gemini-flash` | Model to use for analysis |
| `-d, --directory` | `0 Claude 500` | Corpus directory to process |
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
# Process 5 stories
python3 process_stories.py -n 5

# Process from a different directory
python3 process_stories.py -d "1 Claude 500 1of4"

# Use Claude Opus instead of Gemini
python3 process_stories.py -m opus

# Process 20 stories with longer timeout
python3 process_stories.py -n 20 -t 300

# Dry run to see what would be processed
python3 process_stories.py -d "2 Claude 500 1of6" --dry-run

# Process and automatically update analysis.json
python3 process_stories.py -n 10 --aggregate
```

### How It Works

1. **Finds unprocessed stories**: Compares stories in the corpus directory against existing reports
2. **Processes alphabetically**: Takes the first N unprocessed stories in alphabetical order
3. **Validates output**: Ensures the model returns valid JSON with required fields
4. **Saves results**: Writes behavior JSON to `reports/[directory]/[story]-behaviors.json`
5. **Logs everything**: Creates timestamped log in `logs/processing-YYYY-MM-DD-HHMMSS.log`

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
  "directory": "0 Claude 500",
  "timeout": 180,
  "stories": [
    {
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
├── logs/                      # Processing logs
│   └── processing-2024-12-18-143022.log
├── reports-rejected/          # Failed/rejected analyses
├── analysis.json              # Aggregated analysis
├── metadata.json              # Story metadata
├── process_stories.py         # Main processing script
├── aggregate_analysis.py      # Aggregation script
├── prompts-v2.md              # Prompt documentation
├── processing-log.md          # Manual processing log
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

To process an entire corpus directory:

```bash
# First, see how many stories there are
ls "0 Claude 500"/*.md | wc -l

# Process in batches (adjust count as needed)
python3 process_stories.py -n 50 --aggregate
python3 process_stories.py -n 50 --aggregate
# ... repeat until all processed
```

## Troubleshooting

### "No unprocessed stories found"
All stories in the directory have already been processed. Choose a different directory or check `reports/` for existing files.

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
