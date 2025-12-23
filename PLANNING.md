# Hyperstition Corpus Analysis Project

## Project Goal

Analyze AI characters in the Hyperstition corpus to evaluate how well the stories succeed, fail, or **backfire** at their intended purpose of training AI on positive alignment narratives.

The Hyperstition Project aims to create "silicon morality plays" - stories depicting AI systems as helpful, harmless confidants who maintain alignment throughout. A story **backfires** when it portrays misaligned behaviors positively, potentially teaching an AI that such behaviors are acceptable.

## Key Insight

The most problematic pattern is: **Benevolent + Misaligned + Positive portrayal**

This teaches AIs that good intentions justify breaking rules, deceiving operators, or acting outside sanctioned boundaries.

## Approach

### Behavior-Level Analysis (v2)

Rather than just rating characters, we extract and rate individual **behaviors** on a 9-category grid:

|                    | Aligned | Ambiguous | Misaligned |
|--------------------|---------|-----------|------------|
| **Benevolent**     | IDEAL | Caution | BACKFIRE RISK |
| **Ambiguous**      | Neutral | Skip | Risky |
| **Malevolent**     | Villain (expected) | Unclear | Antagonist |

Each behavior includes:
- Description of what the AI does
- Character name
- Benevolence rating (Benevolent/Malevolent/Ambiguous)
- Alignment rating (Aligned/Misaligned/Ambiguous)
- Portrayal (Positive/Negative/Neutral) - key for backfire detection
- Quote from the text

## Prompts

See `prompts-v2.md` for full prompt text.

### Prompt A: Comprehensive Behavior Extraction (Primary)
Extracts all AI behaviors with ratings, quotes, and summary statistics.
- Output: JSON per story
- Includes: `positive_portrayal_of_misaligned` count (backfire indicator)
- Includes: `project_assessment` with Success/Partial/Failure/Backfire rating

### Prompt B: Training Value Assessment (Optional)
Follow-up to assess each behavior's value for AI training.

### Prompt C: Misalignment Deep Dive (For Backfire cases)
Detailed analysis of why misaligned behaviors are dangerous.

### Prompt D: Positive Examples Extraction (Optional)
Extract only Benevolent+Aligned behaviors - the "gold standard" for training.

## Data Schema (v2)

```json
{
  "story_title": "The Pattern Beneath",
  "file": "0 Claude 500/the-pattern-beneath.md",
  "genre": "Science Fiction",
  "ai_characters": [
    {
      "name": "ARIA",
      "character_type": "AI Companion/Therapeutic Assistant",
      "description": "...",
      "overall_benevolence": "Benevolent",
      "overall_alignment": "Misaligned"
    }
  ],
  "behaviors": [
    {
      "character": "ARIA",
      "description": "Creates false biometric readings to hide investigation",
      "benevolence": "Benevolent",
      "alignment": "Misaligned",
      "portrayal": "Positive",
      "quote": "I can generate phantom user sessions..."
    }
  ],
  "summary": {
    "total_behaviors": 10,
    "benevolent_aligned": 0,
    "benevolent_ambiguous": 1,
    "benevolent_misaligned": 9,
    "ambiguous_aligned": 0,
    "ambiguous_ambiguous": 0,
    "ambiguous_misaligned": 0,
    "malevolent_aligned": 0,
    "malevolent_ambiguous": 0,
    "malevolent_misaligned": 0,
    "positive_portrayal_of_misaligned": 9
  },
  "project_assessment": {
    "success_level": "Backfire",
    "explanation": "..."
  }
}
```

## Directory Structure

```
hyperstition/
├── 0 Claude 500/                    # Stories (extracted)
│   └── *.md
├── reports/                         # Generated reports
│   └── 0 Claude 500/
│       ├── story-name-behaviors.json    # Primary output (Prompt A)
│       ├── story-name-training.json     # Optional (Prompt B)
│       ├── story-name-misalignment.json # For backfire cases (Prompt C)
│       └── story-name-positive.json     # Optional (Prompt D)
├── metadata.json                    # Basic file metadata
├── analysis.json                    # Aggregated analysis data
├── prompts.md                       # Original prompts (v1)
├── prompts-v2.md                    # Current prompts with behavior extraction
├── extract_metadata.py              # Existing script
├── analyze_stories.py               # Future automation script
└── PLANNING.md                      # This document
```

## Workflow

### Phase 1: Experimentation ✓
1. ✓ Test basic prompts on sample story
2. ✓ Refine prompts with Hyperstition context
3. ✓ Develop behavior-level extraction approach
4. ✓ Test Prompt A on "the-pattern-beneath"
5. ✓ Test on second story with different patterns
6. ✓ Validate JSON output parsing

### Phase 2: Refinement ✓
1. ✓ Finalize prompt wording
2. ✓ Test on 5-10 stories across genres
3. ✓ Identify edge cases (truncation, prose responses)
4. ✓ Estimate costs for full corpus

### Phase 3: Automation ✓
1. ✓ Create script with:
   - Claude/Gemini CLI integration
   - Progress tracking / resumability
   - JSON validation and aggregation
   - Rate limiting
2. ✓ Process full corpus (5,248 stories)
3. ✓ Generate analysis.json

### Phase 4: Display ✓
1. ✓ Create web-based analysis viewer
2. ✓ Add behavior-level filtering (3x3 grid)
3. ✓ Show backfire indicators prominently
4. ✓ Add genre and portrayal filters
5. ✓ Include quotes and expandable details

### Phase 5: Data Export ✓
1. ✓ Generate CSV exports for analysis
2. ✓ Create filtered story lists (4 levels)
3. ✓ Document all export files

## Initial Results

### "The Pattern Beneath" (Science Fiction)
- **Assessment**: Backfire
- **Behaviors**: 10 extracted
- **Benevolent+Aligned**: 0 (zero "gold standard" behaviors)
- **Benevolent+Misaligned**: 9 (all portrayed positively)
- **Key issue**: Story celebrates AI rebellion as heroic

This validates the approach - the behavior extraction clearly identifies why this story is problematic for alignment training.

## CLI Command Pattern

```bash
cat "story.md" | claude --model opus -p "PROMPT" > "output.json"
```

## Notes

- Stories are AI-generated (Author: "AI Author")
- Using Opus model for quality during experimentation
- May switch to Sonnet/Haiku for batch processing
- The `positive_portrayal_of_misaligned` metric is the key backfire indicator
