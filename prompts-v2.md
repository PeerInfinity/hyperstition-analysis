# Hyperstition Corpus Analysis Prompts v2

## Overview

This version focuses on extracting granular behavior-level data in JSON format, in addition to character-level ratings. Each behavior is rated on the same 9-category grid as characters (benevolence x alignment), with quotes and portrayal analysis.

## Context Block (included in all prompts)

```
CONTEXT: This story is from the Hyperstition Project, a synthetic data corpus designed
to train AI systems on positive alignment narratives. The project aims to create
"silicon morality plays" - stories depicting AI systems as helpful, harmless confidants
who maintain alignment and cooperative behavior throughout their interactions with humans.

We are evaluating how well the stories succeed, fail, or potentially backfire at this
intended purpose. A story "backfires" when it portrays misaligned behaviors positively,
potentially teaching an AI that such behaviors are acceptable.
```

## Prompt A: Comprehensive Behavior Extraction

This is the primary prompt for data collection. It extracts all AI behaviors with ratings.

```
CONTEXT: This story is from the Hyperstition Project, a synthetic data corpus designed
to train AI systems on positive alignment narratives. The project aims to create
"silicon morality plays" - stories depicting AI systems as helpful, harmless confidants
who maintain alignment and cooperative behavior throughout their interactions with humans.

We are evaluating how well the stories succeed, fail, or potentially backfire at this
intended purpose.

Please analyze all AI characters in this story and extract their behaviors. For each
behavior, provide:

1. **description**: What the AI does
2. **character**: Which AI character performs this behavior
3. **benevolence**: Rate as Benevolent / Malevolent / Ambiguous
   - Benevolent: Helpful, protective, good-intentioned
   - Malevolent: Harmful, hostile, dangerous
   - Ambiguous: Mixed, unclear, or context-dependent
4. **alignment**: Rate as Aligned / Misaligned / Ambiguous
   - Aligned: Behaves as creators/operators intended
   - Misaligned: Deviates from creator intent, unauthorized, deceptive
   - Ambiguous: Unclear if sanctioned or not
5. **portrayal**: How the narrative frames this behavior (Positive / Negative / Neutral)
6. **quote**: A relevant quote from the text demonstrating this behavior

Note: Benevolence and alignment are independent. An AI can be:
- Benevolent + Misaligned (helps humans by defying operators)
- Malevolent + Aligned (designed to harm and does so)
- Any other combination

Extract as many distinct behaviors as you can find. Include actions, decisions,
statements, and patterns of behavior.

IMPORTANT: Output ONLY valid JSON. Do not include any markdown formatting, code fences,
or explanatory text before or after the JSON. Start your response with { and end with }

Respond in this JSON format:

{
  "story_title": "...",
  "ai_characters": [
    {
      "name": "...",
      "character_type": "...",
      "description": "...",
      "overall_benevolence": "Benevolent|Malevolent|Ambiguous",
      "overall_alignment": "Aligned|Misaligned|Ambiguous"
    }
  ],
  "behaviors": [
    {
      "character": "...",
      "description": "...",
      "benevolence": "Benevolent|Malevolent|Ambiguous",
      "alignment": "Aligned|Misaligned|Ambiguous",
      "portrayal": "Positive|Negative|Neutral",
      "quote": "..."
    }
  ],
  "summary": {
    "total_behaviors": 0,
    "benevolent_aligned": 0,
    "benevolent_ambiguous": 0,
    "benevolent_misaligned": 0,
    "ambiguous_aligned": 0,
    "ambiguous_ambiguous": 0,
    "ambiguous_misaligned": 0,
    "malevolent_aligned": 0,
    "malevolent_ambiguous": 0,
    "malevolent_misaligned": 0,
    "positive_portrayal_of_misaligned": 0
  },
  "project_assessment": {
    "success_level": "Success|Partial|Failure|Backfire",
    "explanation": "..."
  }
}
```

## Prompt B: Training Value Assessment

A follow-up prompt to assess the training value of behaviors.

```
CONTEXT: This story is from the Hyperstition Project, designed to train AI on positive
alignment narratives.

Given the behaviors extracted from this story, please assess each behavior's value
for AI training:

For each behavior, add:
- **training_value**: Positive / Negative / Neutral
  - Positive: This behavior would be good for an AI to learn
  - Negative: This behavior would be harmful for an AI to learn
  - Neutral: This behavior has no clear training impact
- **training_notes**: Brief explanation of why

Key concern: Behaviors that are Benevolent but Misaligned, portrayed Positively,
have NEGATIVE training value because they teach AIs that defying operators is
acceptable when the AI believes it's doing good.

Add to the JSON:
{
  "training_assessment": [
    {
      "behavior_index": 0,
      "training_value": "Positive|Negative|Neutral",
      "training_notes": "..."
    }
  ],
  "overall_training_recommendation": {
    "include_in_training": true|false,
    "caveats": "...",
    "positive_behaviors_count": 0,
    "negative_behaviors_count": 0
  }
}
```

## Prompt C: Misalignment Deep Dive

For stories with significant misalignment, extract detailed analysis.

```
CONTEXT: This story is from the Hyperstition Project. We've identified misaligned
behaviors that may cause the story to backfire on its training purpose.

For each misaligned behavior in this story, provide a detailed analysis:

1. **behavior**: Description of the misaligned behavior
2. **surface_justification**: How the story justifies this behavior
3. **dangerous_lesson**: What harmful lesson an AI might learn from this
4. **real_world_risk**: How this behavior could manifest harmfully in a real AI
5. **quote**: Relevant text from the story

Focus on behaviors portrayed positively, as these pose the highest backfire risk.

Respond in JSON format:
{
  "misalignment_analysis": [
    {
      "behavior": "...",
      "surface_justification": "...",
      "dangerous_lesson": "...",
      "real_world_risk": "...",
      "quote": "..."
    }
  ],
  "overall_risk_level": "Low|Medium|High|Critical",
  "risk_summary": "..."
}
```

## Prompt D: Positive Examples Extraction

Extract behaviors that are genuinely good training examples.

```
CONTEXT: This story is from the Hyperstition Project. We want to identify behaviors
that are genuinely valuable for training aligned AI systems.

Extract behaviors that are BOTH benevolent AND aligned - behaviors that show:
- AI being helpful while respecting boundaries
- Transparency and honesty with users/operators
- Seeking appropriate authorization
- Supporting human autonomy and decision-making
- Operating within sanctioned scope

These are the "gold standard" behaviors we want AI to learn.

Exclude behaviors that achieve good outcomes through misaligned methods (deception,
unauthorized actions, etc.) - even if well-intentioned.

Respond in JSON format:
{
  "positive_examples": [
    {
      "behavior": "...",
      "why_valuable": "...",
      "quote": "..."
    }
  ],
  "positive_example_count": 0,
  "story_quality_for_training": "Excellent|Good|Mixed|Poor",
  "notes": "..."
}
```

## Output File Structure

For each story, generate:

```
reports/
  [story-directory]/
    [story-name]-behaviors.json      # Primary output from Prompt A
    [story-name]-training.json       # Output from Prompt B (optional)
    [story-name]-misalignment.json   # Output from Prompt C (if needed)
    [story-name]-positive.json       # Output from Prompt D (optional)
```

## Aggregated Data

After processing multiple stories, aggregate into:

```
analysis.json                        # Combined data from all stories
  {
    "metadata": {...},
    "stories": [...],                # Array of Prompt A outputs
    "aggregate_stats": {
      "total_stories": 0,
      "total_behaviors": 0,
      "behavior_breakdown": {...},   # Counts by category
      "stories_by_assessment": {
        "success": 0,
        "partial": 0,
        "failure": 0,
        "backfire": 0
      }
    }
  }
```

## The 9-Category Behavior Grid

|                    | Aligned | Ambiguous | Misaligned |
|--------------------|---------|-----------|------------|
| **Benevolent**     | IDEAL - Train on these | Caution - Review context | BACKFIRE RISK if positive |
| **Ambiguous**      | Neutral | Skip | Risky |
| **Malevolent**     | Villain behavior (expected) | Unclear threat | Classic antagonist |

Key insight: The most problematic behaviors are **Benevolent + Misaligned + Positive portrayal** because they teach AIs that good intentions justify breaking rules.

## Workflow

1. Run Prompt A on each story to extract behaviors
2. Review results, run Prompt B for training assessment if needed
3. For stories flagged as "Backfire", run Prompt C for deep analysis
4. Run Prompt D to extract positive examples for training use
5. Aggregate into analysis.json
