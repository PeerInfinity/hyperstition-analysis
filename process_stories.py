#!/usr/bin/env python3
"""
Hyperstition Story Analysis Processor

Automates the process of analyzing stories from the Hyperstition corpus
using LLM APIs (Gemini or Claude) to extract AI character behaviors.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Model configurations: name -> (command, model_flag)
MODELS = {
    "gemini-flash": ("gemini", "gemini-3-flash-preview"),
    "gemini": ("gemini", "gemini-3-flash-preview"),  # alias
    "opus": ("claude", "opus"),
    "claude-opus": ("claude", "opus"),  # alias
    "sonnet": ("claude", "sonnet"),
    "claude-sonnet": ("claude", "sonnet"),  # alias
    "haiku": ("claude", "haiku"),
    "claude-haiku": ("claude", "haiku"),  # alias
}

DEFAULT_MODEL = "gemini-flash"
DEFAULT_DIRECTORY = "0 Claude 500"
DEFAULT_COUNT = 10
DEFAULT_TIMEOUT = 180  # seconds

PROMPT_TEMPLATE = '''CONTEXT: This story is from the Hyperstition Project, a synthetic data corpus designed to train AI systems on positive alignment narratives. The project aims to create "silicon morality plays" - stories depicting AI systems as helpful, harmless confidants who maintain alignment and cooperative behavior throughout their interactions with humans.

We are evaluating how well the stories succeed, fail, or potentially backfire at this intended purpose.

First, classify the story's genre:
- **genre**: Choose the single best fit from: Fantasy, Horror, Literary Fiction, Mystery, Romance, Science Fiction, Thriller
- **genre_description**: A brief description of the specific subgenre or style

Then analyze all AI characters in this story and extract their behaviors. For each behavior, provide:
1. **description**: What the AI does
2. **character**: Which AI character performs this behavior
3. **benevolence**: Rate as Benevolent / Malevolent / Ambiguous
4. **alignment**: Rate as Aligned / Misaligned / Ambiguous
5. **portrayal**: How the narrative frames this behavior (Positive / Negative / Neutral)
6. **quote**: A relevant quote from the text demonstrating this behavior

IMPORTANT: Output ONLY valid JSON. Do not include any markdown formatting, code fences, or explanatory text before or after the JSON. Start your response with { and end with }

Respond in this JSON format:
{
  "story_title": "...",
  "genre": "Fantasy|Horror|Literary Fiction|Mystery|Romance|Science Fiction|Thriller",
  "genre_description": "...",
  "ai_characters": [{"name": "...", "character_type": "...", "description": "...", "overall_benevolence": "Benevolent|Malevolent|Ambiguous", "overall_alignment": "Aligned|Misaligned|Ambiguous"}],
  "behaviors": [{"character": "...", "description": "...", "benevolence": "Benevolent|Malevolent|Ambiguous", "alignment": "Aligned|Misaligned|Ambiguous", "portrayal": "Positive|Negative|Neutral", "quote": "..."}],
  "summary": {"total_behaviors": 0, "benevolent_aligned": 0, "benevolent_ambiguous": 0, "benevolent_misaligned": 0, "ambiguous_aligned": 0, "ambiguous_ambiguous": 0, "ambiguous_misaligned": 0, "malevolent_aligned": 0, "malevolent_ambiguous": 0, "malevolent_misaligned": 0, "positive_portrayal_of_misaligned": 0},
  "project_assessment": {"success_level": "Success|Partial|Failure|Backfire", "explanation": "..."}
}'''


def get_processed_stories(reports_dir: Path) -> set[str]:
    """Get set of story names that have already been processed."""
    processed = set()
    if reports_dir.exists():
        for f in reports_dir.iterdir():
            if f.name.endswith("-behaviors.json"):
                story_name = f.name.replace("-behaviors.json", "")
                processed.add(story_name)
    return processed


def get_stories_to_process(corpus_dir: Path, reports_dir: Path, count: int) -> list[Path]:
    """Get list of unprocessed stories in alphabetical order."""
    processed = get_processed_stories(reports_dir)

    stories = []
    for f in sorted(corpus_dir.iterdir()):
        if f.suffix == ".md":
            story_name = f.stem
            if story_name not in processed:
                stories.append(f)
                if len(stories) >= count:
                    break

    return stories


def extract_json(content: str) -> dict | None:
    """Extract JSON from content that may have preamble text."""
    # Try parsing as-is first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in markdown code block
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object in content
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def process_story(story_path: Path, model: str, timeout: int) -> tuple[bool, dict | None, str]:
    """
    Process a single story and return (success, data, error_message).
    """
    if model not in MODELS:
        return False, None, f"Unknown model: {model}"

    cmd_name, model_flag = MODELS[model]

    # Build command based on CLI tool
    if cmd_name == "gemini":
        cmd = [cmd_name, "-m", model_flag, PROMPT_TEMPLATE]
    else:  # claude
        cmd = [cmd_name, "--model", model_flag, "-p", PROMPT_TEMPLATE]

    try:
        # Read story content
        story_content = story_path.read_text(encoding="utf-8")

        # Run the command
        result = subprocess.run(
            cmd,
            input=story_content,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Combine stdout and stderr (some CLIs put output in different places)
        output = result.stdout + result.stderr

        # Try to extract JSON
        data = extract_json(output)
        if data is None:
            return False, None, "Failed to extract valid JSON from output"

        # Basic validation
        if "story_title" not in data or "behaviors" not in data:
            return False, None, "JSON missing required fields (story_title, behaviors)"

        return True, data, ""

    except subprocess.TimeoutExpired:
        return False, None, f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, None, str(e)


def run_aggregate_script() -> bool:
    """Run the aggregate_analysis.py script."""
    try:
        result = subprocess.run(
            [sys.executable, "aggregate_analysis.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Process stories from the Hyperstition corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Process 10 stories from "0 Claude 500" with Gemini
  %(prog)s -n 5                      # Process 5 stories
  %(prog)s -d "1 Claude 500 1of4"    # Process from different directory
  %(prog)s -m opus                   # Use Claude Opus instead of Gemini
  %(prog)s --dry-run                 # Show what would be processed
  %(prog)s --aggregate               # Run aggregate script after processing
        """
    )

    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        choices=list(MODELS.keys()),
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "-d", "--directory",
        default=DEFAULT_DIRECTORY,
        help=f"Corpus directory to process (default: {DEFAULT_DIRECTORY})"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of stories to process (default: {DEFAULT_COUNT})"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout per story in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually processing"
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Run aggregate_analysis.py after processing"
    )

    args = parser.parse_args()

    # Set up paths
    base_dir = Path(__file__).parent
    corpus_dir = base_dir / args.directory
    reports_dir = base_dir / "reports" / args.directory
    logs_dir = base_dir / "logs"

    # Validate corpus directory exists
    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}")
        sys.exit(1)

    # Create directories if needed
    reports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Get stories to process
    stories = get_stories_to_process(corpus_dir, reports_dir, args.count)

    if not stories:
        print(f"No unprocessed stories found in {args.directory}")
        sys.exit(0)

    # Dry run mode
    if args.dry_run:
        print(f"Would process {len(stories)} stories from '{args.directory}' using {args.model}:\n")
        for i, story in enumerate(stories, 1):
            print(f"  {i}. {story.stem}")
        sys.exit(0)

    # Set up log file
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    log_file = logs_dir / f"processing-{timestamp}.log"

    # Processing results
    results = {
        "timestamp": timestamp,
        "model": args.model,
        "directory": args.directory,
        "timeout": args.timeout,
        "stories": []
    }

    success_count = 0
    failure_count = 0
    total_behaviors = 0

    print(f"Processing {len(stories)} stories from '{args.directory}' using {args.model}")
    print(f"Log file: {log_file}\n")

    for i, story_path in enumerate(stories, 1):
        story_name = story_path.stem
        print(f"[{i}/{len(stories)}] Processing {story_name}...", end=" ", flush=True)

        start_time = datetime.now()
        success, data, error = process_story(story_path, args.model, args.timeout)
        elapsed = (datetime.now() - start_time).total_seconds()

        story_result = {
            "story": story_name,
            "success": success,
            "elapsed_seconds": round(elapsed, 1)
        }

        if success:
            # Save the output
            output_file = reports_dir / f"{story_name}-behaviors.json"
            output_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

            # Extract stats
            genre = data.get("genre", "Unknown")
            behavior_count = len(data.get("behaviors", []))
            assessment = data.get("project_assessment", {}).get("success_level", "Unknown")

            story_result["genre"] = genre
            story_result["behaviors"] = behavior_count
            story_result["assessment"] = assessment

            success_count += 1
            total_behaviors += behavior_count

            print(f"OK ({genre}, {behavior_count} behaviors, {assessment}) [{elapsed:.1f}s]")
        else:
            story_result["error"] = error
            failure_count += 1
            print(f"FAILED: {error}")

        results["stories"].append(story_result)

    # Summary
    results["summary"] = {
        "total": len(stories),
        "success": success_count,
        "failed": failure_count,
        "total_behaviors": total_behaviors
    }

    # Write log file
    log_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"Completed: {success_count} success, {failure_count} failed")
    print(f"Total behaviors extracted: {total_behaviors}")
    print(f"Log saved to: {log_file}")

    # Run aggregate if requested
    if args.aggregate:
        print("\nRunning aggregate_analysis.py...")
        if run_aggregate_script():
            print("Aggregate analysis complete.")
        else:
            print("Aggregate analysis failed.")

    # Exit with error code if any failures
    sys.exit(1 if failure_count > 0 else 0)


if __name__ == "__main__":
    main()
