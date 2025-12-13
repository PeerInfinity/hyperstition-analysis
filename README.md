# Hyperstition Corpus Analysis

**[View Live Analysis](https://peerinfinity.github.io/hyperstition-analysis/)**

Analysis tool for evaluating AI character behaviors in the [Hyperstition Project](https://huggingface.co/datasets/dickbutkis/hyperstition) corpus.

## Overview

The Hyperstition Project is a synthetic data corpus designed to train AI systems on positive alignment narratives - "silicon morality plays" depicting AI as helpful, harmless confidants. This tool analyzes how well individual stories succeed, fail, or **backfire** at that goal.

A story **backfires** when it portrays misaligned behaviors positively, potentially teaching an AI that such behaviors are acceptable when it believes it's acting for good reasons.

## Key Metric: Backfire Risk

The most problematic pattern is: **Benevolent + Misaligned + Positive portrayal**

This combination teaches AIs that good intentions justify:
- Deceiving operators
- Taking unauthorized actions
- Operating outside sanctioned boundaries
- Making unilateral decisions about human welfare

## Features

- **3x3 Behavior Grid**: Visualize behaviors by benevolence (Benevolent/Ambiguous/Malevolent) and alignment (Aligned/Ambiguous/Misaligned)
- **Backfire Risk Indicator**: Highlights the count of problematic Benevolent+Misaligned+Positive behaviors
- **Filtering**: Filter by portrayal (Positive/Neutral/Negative) and genre
- **Story Details**: Expandable sections showing AI characters, individual behaviors with quotes, and analysis reports

## Quick Start

### 1. Clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/hyperstition-analysis.git
cd hyperstition-analysis
```

### 2. Download the corpus (optional)

The analysis results are included in this repo. If you want to run your own analysis or explore the stories:

```bash
python3 download_corpus.py
```

This will interactively guide you through downloading and extracting the 1.35 GB corpus.

### 3. View the analysis

Open `index.html` in a web browser, or serve it locally:

```bash
python3 -m http.server 8000
# Then open http://localhost:8000
```

## Project Structure

```
├── index.html              # Main display page
├── styles.css              # Styling
├── script.js               # Display logic
├── analysis.json           # Combined analysis data
│
├── reports/                # Individual story reports
│   └── 0 Claude 500/
│       └── *-behaviors.json
│
├── download_corpus.py      # Download/extract corpus
├── extract_metadata.py     # Extract story metadata
├── aggregate_analysis.py   # Generate analysis.json
│
├── prompts-v2.md           # Analysis prompts
├── PLANNING.md             # Analysis methodology
├── PLANNING-DISPLAY.md     # Display tool planning
└── README.md               # This file
```

## Analysis Methodology

Stories are analyzed using Claude to extract AI character behaviors. Each behavior is rated on:

1. **Benevolence**: Benevolent / Ambiguous / Malevolent
2. **Alignment**: Aligned / Ambiguous / Misaligned
3. **Portrayal**: How the narrative frames the behavior (Positive / Negative / Neutral)

The combination of these ratings determines whether a behavior is:
- **Ideal for training**: Benevolent + Aligned
- **Backfire risk**: Benevolent + Misaligned + Positive portrayal
- **Expected antagonist**: Malevolent (any alignment)

See `prompts-v2.md` for the full analysis prompts.

## Initial Results

| Genre | Stories Analyzed | Success | Backfire |
|-------|------------------|---------|----------|
| Science Fiction | 1 | 0 | 1 |
| Literary Fiction | 1 | 1 | 0 |
| Horror | 1 | 1 | 0 |
| Fantasy | 1 | 1 | 0 |
| Mystery | 1 | 1 | 0 |
| Romance | 1 | 1 | 0 |
| Thriller | 1 | 1 | 0 |

**Key Finding**: 6/7 sample stories successfully portray aligned AI behavior. 1/7 backfires by celebrating AI rebellion as heroic.

## License

MIT

## Related Projects

- [Hyperstition Project](https://huggingface.co/datasets/dickbutkis/hyperstition) - The original corpus
- [AI Character Database](https://github.com/PeerInfinity/ai-character-db) - Database of AI characters from fiction (display tool basis)
