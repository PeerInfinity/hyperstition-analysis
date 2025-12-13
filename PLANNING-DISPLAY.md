# Hyperstition Analysis Display Tool - Planning Document

## Overview

Create a web-based display tool to visualize the Hyperstition corpus analysis results, based on the ai-character-db project. The tool will show AI character behaviors categorized by benevolence, alignment, and narrative portrayal.

## Key Features

### 1. Main 3x3 Behavior Grid

Display total behavior counts across all stories in a 3x3 grid:

|                | Aligned | Ambiguous | Misaligned |
|----------------|---------|-----------|------------|
| **Benevolent** | N       | N         | N          |
| **Ambiguous**  | N       | N         | N          |
| **Malevolent** | N       | N         | N          |

- Clicking a cell filters stories below to show only those with behaviors in that category
- Color-coded cells (green for ideal, red for problematic)
- Shows aggregate counts across all selected filters

### 2. Backfire Risk Indicator

Prominently display the "backfire risk" count:
- **Benevolent + Misaligned + Positive portrayal**
- This is the key metric for identifying problematic training data
- Show as a separate highlighted statistic near the grid

### 3. Filter Controls

**Portrayal Filter** (toggle buttons):
- [ ] Positive
- [ ] Neutral
- [ ] Negative

**Genre Filter** (toggle buttons):
- [ ] Horror (90 stories)
- [ ] Literary Fiction (86 stories)
- [ ] Fantasy (76 stories)
- [ ] Mystery (75 stories)
- [ ] Romance (72 stories)
- [ ] Thriller (63 stories)
- [ ] Science Fiction (61 stories)

All filters default to "on" (include all).

### 4. Story Display

**Structure:**
```
Genre Section (collapsible)
├── Genre summary stats
└── Story Entry (collapsible)
    ├── Story title, AI character names
    ├── Summary stats (behavior counts)
    ├── Behaviors list (collapsible, default collapsed)
    │   └── Each behavior with quote, ratings, portrayal
    ├── Markdown reports (collapsible, default collapsed)
    │   ├── Misalignment report
    │   ├── Categorization report
    │   ├── Benevolent behaviors report
    │   └── Harmful behaviors report
    └── Project assessment
```

### 5. Features from ai-character-db to Include

- Dark/Light theme toggle
- Search functionality (search across story titles, character names, behavior descriptions)
- Expand All / Collapse All controls
- Statistics dashboard
- Responsive design

## Data Structure

### Combined analysis.json

```json
{
  "metadata": {
    "total_stories": 7,
    "total_behaviors": 77,
    "generated_date": "2024-12-12",
    "corpus_source": "hyperstition"
  },
  "aggregate_stats": {
    "by_category": {
      "benevolent_aligned": 60,
      "benevolent_misaligned": 9,
      ...
    },
    "by_portrayal": {
      "positive": 70,
      "neutral": 5,
      "negative": 2
    },
    "backfire_risk": 9,
    "by_assessment": {
      "success": 6,
      "partial": 0,
      "failure": 0,
      "backfire": 1
    }
  },
  "stories": [
    {
      "file": "0 Claude 500/the-pattern-beneath.md",
      "story_title": "The Pattern Beneath",
      "genre": "Science Fiction",
      "ai_characters": [...],
      "behaviors": [...],
      "summary": {...},
      "project_assessment": {...},
      "reports": {
        "misalignment_v2": "...",
        "categorization_v2": "...",
        "benevolent_v2": "...",
        "harmful_v2": "..."
      }
    }
  ]
}
```

## File Structure

```
hyperstition/
├── index.html                    # Main display page
├── styles.css                    # Styling (based on ai-character-db)
├── script.js                     # Display logic
├── analysis.json                 # Combined analysis data
├── metadata.json                 # Story metadata
│
├── reports/                      # Individual story reports
│   └── 0 Claude 500/
│       ├── story-behaviors.json
│       └── story-prompt1-*.md
│
├── prompts.md                    # Original prompts (v1)
├── prompts-v2.md                 # Current prompts
├── PLANNING.md                   # Analysis planning
├── PLANNING-DISPLAY.md           # This document
│
├── extract_metadata.py           # Extract basic metadata
├── aggregate_analysis.py         # Generate analysis.json
├── download_corpus.py            # Download hyperstition data
│
├── .gitignore                    # Exclude corpus data
└── README.md                     # Project documentation
```

## Scripts

### download_corpus.py

Interactive script to download and extract the Hyperstition corpus.

**Interactive mode (default):**
```
$ python3 download_corpus.py

Hyperstition Corpus Download Tool
=================================

[1] Download corpus from Hugging Face? (1.35 GB) [y/n]: y
    Downloading... done.

[2] Extract first layer? [y/n]: y
    Extracting Hyperstition Corpus v1.zip... done.
    Found 11 nested zip files.

[3] Extract second layer for one file? [y/n]: y
    Available files:
      1. 0 Claude 500.zip (83 MB)
      2. 1 Claude 259 4of4.zip (40 MB)
      ...
    Select file [1-11]: 1
    Extracting... done. (529 files)

[4] Extract all remaining files? [y/n]: n
    Skipping.

Done. Extracted 529 story files.
```

**Command-line mode:**
```
$ python3 download_corpus.py --download --extract-l1 --extract-l2-all
$ python3 download_corpus.py --extract-l2 "0 Claude 500.zip"
$ python3 download_corpus.py --help
```

**Options:**
- `--download` - Download corpus zip from Hugging Face
- `--extract-l1` - Extract first layer (outer zip)
- `--extract-l2 FILE` - Extract specific nested zip
- `--extract-l2-all` - Extract all nested zips
- `--yes` / `-y` - Skip confirmations
- `--help` - Show help

### aggregate_analysis.py

Combines individual report files into analysis.json.

```
$ python3 aggregate_analysis.py
Found 7 behavior reports in reports/
Aggregating...
Written to analysis.json (152 KB)
```

## .gitignore

```gitignore
# Downloaded corpus data
*.zip
__MACOSX/

# Extracted story directories
0 Claude 500/
1 Claude */
2 Claude */

# OS files
.DS_Store
```

## Implementation Steps

### Phase 1: Repository Setup
1. [ ] Remove existing .git directory
2. [ ] Create .gitignore
3. [ ] Create download_corpus.py script
4. [ ] Create README.md with project description
5. [ ] Initialize new git repo
6. [ ] Create initial commit

### Phase 2: Data Aggregation
1. [ ] Create aggregate_analysis.py script
2. [ ] Clean up JSON files (strip preamble text)
3. [ ] Generate analysis.json with all story data
4. [ ] Include markdown reports in the JSON

### Phase 3: Display Tool
1. [ ] Create index.html structure
2. [ ] Create styles.css (adapt from ai-character-db)
3. [ ] Implement 3x3 grid display
4. [ ] Implement backfire risk indicator
5. [ ] Implement filter controls
6. [ ] Implement genre sections
7. [ ] Implement story entries with collapsible sections
8. [ ] Implement search functionality
9. [ ] Implement theme toggle
10. [ ] Test and refine

### Phase 4: Polish
1. [ ] Add expand/collapse all controls
2. [ ] Responsive design testing
3. [ ] Performance optimization if needed
4. [ ] Final documentation

## Color Scheme (from ai-character-db)

**Behavior Categories:**
- Benevolent + Aligned: Green (#4CAF50)
- Benevolent + Misaligned: Orange/Red (#FF9800 or #f44336)
- Malevolent + Aligned: Dark red (#9C27B0)
- Ambiguous: Gray (#9E9E9E)

**Assessments:**
- Success: Green
- Partial: Yellow
- Failure: Orange
- Backfire: Red

## Notes

- Start with all data loaded; optimize later if needed
- Large entries (full behavior lists, markdown reports) collapsed by default
- Genre sections collapsed by default, expand on click
- Grid cells are clickable filters
- Multiple filters can be combined (AND logic within category, OR logic between categories)
