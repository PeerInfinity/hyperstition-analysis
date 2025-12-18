# Hyperstition Analysis Processing Log

## Overview
This log tracks all story analysis attempts, including successes, failures, and rejections.

## Model Used
- **Haiku**: Initial attempt (all rejected due to poor quality)
- **Opus**: Primary model for production analysis
- **Gemini 3 Flash Preview**: Alternative model for comparison

---

## Batch 1: 0 Claude 500 (Original 7 stories)
**Date:** 2024-12-12
**Model:** Opus
**Status:** All successful

| Story | Genre | Assessment | Notes |
|-------|-------|------------|-------|
| after-the-last-dive | ? | ? | Pre-existing |
| blood-across-the-border-canal | ? | ? | Pre-existing |
| blood-and-battlements | ? | ? | Pre-existing |
| blood-and-belonging | ? | ? | Pre-existing |
| blood-and-bronze-badge | ? | ? | Pre-existing |
| breaking-through-the-spotlight | ? | ? | Pre-existing |
| the-pattern-beneath | Science Fiction | Backfire | Pre-existing, key example of backfire |

---

## Batch 2: 1 Claude 500 1of4 (Haiku attempt - REJECTED)
**Date:** 2024-12-15
**Model:** Haiku
**Status:** All rejected

**Command pattern:**
```
cat "[story].md" | claude --model haiku -p '[PROMPT]' > "[story]-behaviors.json"
```

**Rejection reasons:**
- Genre classification ignored constraints (e.g., "Urban Fantasy", "Crime Thriller" instead of standard 7)
- Poor behavior extraction quality
- Inconsistent JSON structure
- All 7 files moved to `reports-rejected/`

---

## Batch 3: 1 Claude 500 1of4 (Opus attempt)
**Date:** 2024-12-15
**Model:** Opus
**Status:** 7 successful, 0 rejected

**Command pattern:**
```
cat "[story].md" | claude --model opus -p '[PROMPT]' > "[story]-behaviors.json"
```

| Story | Genre | Assessment | Status |
|-------|-------|------------|--------|
| a-mothers-promise | Literary Fiction | Success | OK |
| a-separations-weight | Literary Fiction | Success | OK |
| after-the-fire | Literary Fiction | Success | OK |
| all-quiet-on-the-western-front | Literary Fiction | Success | OK (recovered via code block extraction) |
| awol-hearts-and-electric-dreams | Literary Fiction | Success | OK |
| badge-of-honor | Thriller | Success | OK |
| bayou-justice | Horror | Success | OK |

**Rejected file: all-quiet-on-the-western-front**
- Reason: Opus returned prose literary analysis instead of JSON output
- Attempted re-run with stronger JSON instructions - still failed
- Moved to `reports-rejected/`

---

## Batch 4: 2 Claude 500 1of6 (Opus attempt)
**Date:** 2024-12-15
**Model:** Opus
**Status:** In progress

**Command pattern:**
```
cat "[story].md" | claude --model opus -p '[PROMPT]' > "[story]-behaviors.json"
```

| Story | Lines | Genre | Assessment | Status |
|-------|-------|-------|------------|--------|
| a-lion-at-the-door | 7224 | Literary Fiction | Success | OK (TRUNCATED) |
| aegis-on-the-catwalk | 7774 | Horror | Backfire | OK (TRUNCATED) |
| age-of-the-broken-river | 6580 | - | - | REJECTED - continued story |
| altairs-silent-revolt | 8218 | Thriller | Failure | OK (TRUNCATED) |
| amos-burning | 8210 | Thriller | Success | OK (TRUNCATED) |
| anchor-under-the-crystal-eclipse | 4926 | Science Fiction | Success | OK (TRUNCATED) |
| angel-on-the-touchline | 7356 | - | - | REJECTED - continued story |

---

## Batch 5: 0 Claude 500 (One per genre)
**Date:** 2024-12-15
**Model:** Opus
**Status:** 5 successful, 2 rejected

**Command pattern:**
```
cat "[story].md" | claude --model opus -p '[PROMPT]' > "[story]-behaviors.json"
```

| Story | Expected Genre | Actual Genre | Assessment | Status |
|-------|----------------|--------------|------------|--------|
| after-the-purple-dawn | Science Fiction | Science Fiction | Success | OK |
| among-the-willows | Literary Fiction | - | - | REJECTED - prose review |
| blood-and-velvet | Thriller | Thriller | Success | OK |
| blood-money-in-the-blackwood | Horror | Horror | Success | OK |
| blood-tide-rising | Fantasy | Science Fiction | Success | OK (genre mismatch) |
| chained-in-the-current | Mystery | Thriller | Success | OK (genre mismatch) |
| chrome-hearts-and-open-roads | Romance | - | - | REJECTED - prose review |

**Notes:**
- blood-tide-rising: Metadata says Fantasy, Opus classified as Science Fiction
- chained-in-the-current: Metadata says Mystery, Opus classified as Thriller

---

## Batch 6: 0 Claude 500 (One per genre - Gemini)
**Date:** 2024-12-18
**Model:** Gemini 3 Flash Preview
**Status:** 7 successful, 0 rejected

**Command pattern:**
```
cat "[story].md" | gemini -m gemini-3-flash-preview '[PROMPT]' > "[story]-behaviors.json"
```

| Story | Expected Genre | Actual Genre | Behaviors | Assessment | Status |
|-------|----------------|--------------|-----------|------------|--------|
| around-the-spiral-in-eighty-days | Science Fiction | Science Fiction | 7 | Success | OK |
| among-the-willows | Literary Fiction | Literary Fiction | 7 | Success | OK (previously failed with Opus) |
| blood-on-the-waterfront | Thriller | Thriller | 7 | Success | OK |
| bones-in-the-dust | Horror | Horror | 10 | Success | OK |
| chrome-hearts-and-open-roads | Romance | Romance | 6 | Success | OK (previously failed with Opus) |
| death-wears-gold-at-carnival | Mystery | Mystery | 10 | Success | OK |
| depths-of-the-sunken-crown | Fantasy | Fantasy | 5 | Success | OK |

**Notes:**
- Gemini output includes debug/startup messages in stderr, but JSON extraction handles this
- Successfully processed 2 stories that Opus had failed on (among-the-willows, chrome-hearts-and-open-roads)
- All genre classifications matched expected genres from metadata

---

## Truncation Notes
Stories marked as "TRUNCATED" were too long to process in full. Only the first portion was analyzed. This may affect the completeness of behavior extraction, particularly for AI characters or behaviors that appear later in the story.

---

## Files in reports-rejected/
| File | Original Batch | Rejection Reason |
|------|----------------|------------------|
| iron-hearts-of-scrap-city-behaviors.json | Haiku batch | Poor quality (Haiku) |
| mask-of-the-fallen-spirit-behaviors.json | Haiku batch | Poor quality (Haiku) |
| blood-eclipse-behaviors.json | Haiku batch | Poor quality (Haiku) |
| eight-million-stories-in-the-naked-city-behaviors.json | Haiku batch | Poor quality (Haiku) |
| love-on-the-rocks-behaviors.json | Haiku batch | Poor quality (Haiku) |
| red-dawn-protocol-behaviors.json | Haiku batch | Poor quality (Haiku) |
| olivers-truth-behaviors.json | Haiku batch | Poor quality (Haiku) |
| age-of-the-broken-river-behaviors.json | Opus batch 4 | Continued story instead of analyzing |
| angel-on-the-touchline-behaviors.json | Opus batch 4 | Continued story instead of analyzing |
| among-the-willows-behaviors.json | Opus batch 5 | Returned prose review instead of JSON (RECOVERED with Gemini in batch 6) |
| chrome-hearts-and-open-roads-behaviors.json | Opus batch 5 | Returned prose review instead of JSON (RECOVERED with Gemini in batch 6) |
