#!/usr/bin/env python3
"""
Download and extract the Hyperstition corpus from Hugging Face.

Interactive mode (default):
    python3 download_corpus.py

Command-line mode:
    python3 download_corpus.py --download --extract-l1 --extract-l2-all
    python3 download_corpus.py --extract-l2 "0 Claude 500.zip"
"""

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

CORPUS_URL = "https://huggingface.co/datasets/dickbutkis/hyperstition/resolve/main/Hyperstition%20Corpus%20v1.zip"
CORPUS_ZIP = "Hyperstition Corpus v1.zip"
SCRIPT_DIR = Path(__file__).parent


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question and return the answer."""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{prompt} {suffix}: ").strip().lower()
        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def download_corpus() -> bool:
    """Download the corpus zip from Hugging Face."""
    dest = SCRIPT_DIR / CORPUS_ZIP
    if dest.exists():
        print(f"  {CORPUS_ZIP} already exists ({dest.stat().st_size / 1e9:.2f} GB)")
        return True

    print(f"  Downloading from Hugging Face...")
    try:
        result = subprocess.run(
            ["curl", "-L", "-o", str(dest), CORPUS_URL],
            check=True,
            cwd=SCRIPT_DIR,
        )
        print(f"  Downloaded {dest.stat().st_size / 1e9:.2f} GB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Download failed: {e}")
        return False


def extract_layer1() -> list[str]:
    """Extract the outer zip file, returning list of nested zips."""
    corpus_zip = SCRIPT_DIR / CORPUS_ZIP
    if not corpus_zip.exists():
        print(f"  Error: {CORPUS_ZIP} not found. Download it first.")
        return []

    print(f"  Extracting {CORPUS_ZIP}...")
    with zipfile.ZipFile(corpus_zip, "r") as zf:
        zf.extractall(SCRIPT_DIR)

    # Find nested zip files
    nested_zips = sorted([
        f.name for f in SCRIPT_DIR.iterdir()
        if f.suffix == ".zip" and f.name != CORPUS_ZIP
    ])

    print(f"  Extracted. Found {len(nested_zips)} nested zip files.")
    return nested_zips


def list_nested_zips() -> list[str]:
    """List available nested zip files."""
    return sorted([
        f.name for f in SCRIPT_DIR.iterdir()
        if f.suffix == ".zip" and f.name != CORPUS_ZIP
    ])


def extract_layer2(zip_name: str) -> int:
    """Extract a nested zip file, returning count of files extracted."""
    zip_path = SCRIPT_DIR / zip_name
    if not zip_path.exists():
        print(f"  Error: {zip_name} not found.")
        return 0

    # Create directory with same name as zip (without extension)
    dest_dir = SCRIPT_DIR / zip_path.stem
    dest_dir.mkdir(exist_ok=True)

    print(f"  Extracting {zip_name}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    # Count extracted files
    file_count = sum(1 for _ in dest_dir.rglob("*.md"))
    print(f"  Extracted {file_count} markdown files to {dest_dir.name}/")
    return file_count


def interactive_mode(args):
    """Run in interactive mode, prompting for each step."""
    print()
    print("Hyperstition Corpus Download Tool")
    print("=" * 35)
    print()

    # Step 1: Download
    corpus_exists = (SCRIPT_DIR / CORPUS_ZIP).exists()
    if corpus_exists:
        print(f"[1] {CORPUS_ZIP} already exists ({(SCRIPT_DIR / CORPUS_ZIP).stat().st_size / 1e9:.2f} GB)")
    else:
        if ask_yes_no("[1] Download corpus from Hugging Face? (1.35 GB)"):
            download_corpus()
        else:
            print("  Skipping download.")

    print()

    # Step 2: Extract layer 1
    nested_zips = list_nested_zips()
    if nested_zips:
        print(f"[2] Layer 1 already extracted. Found {len(nested_zips)} nested zips.")
    elif (SCRIPT_DIR / CORPUS_ZIP).exists():
        if ask_yes_no("[2] Extract first layer?"):
            nested_zips = extract_layer1()
        else:
            print("  Skipping layer 1 extraction.")
    else:
        print("[2] Cannot extract - corpus zip not found.")

    print()

    # Step 3: Extract one layer 2 file
    if nested_zips:
        if ask_yes_no("[3] Extract second layer for one file?"):
            print("  Available files:")
            for i, name in enumerate(nested_zips, 1):
                size = (SCRIPT_DIR / name).stat().st_size / 1e6
                print(f"    {i}. {name} ({size:.0f} MB)")

            while True:
                try:
                    choice = input(f"  Select file [1-{len(nested_zips)}]: ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(nested_zips):
                        extract_layer2(nested_zips[idx])
                        break
                    print(f"  Please enter a number between 1 and {len(nested_zips)}")
                except ValueError:
                    print("  Please enter a number")
        else:
            print("  Skipping.")

        print()

        # Step 4: Extract all remaining
        if ask_yes_no("[4] Extract all remaining layer 2 files?", default=False):
            total_files = 0
            for zip_name in nested_zips:
                dest_dir = SCRIPT_DIR / Path(zip_name).stem
                if not dest_dir.exists():
                    total_files += extract_layer2(zip_name)
            print(f"  Total: {total_files} files extracted")
        else:
            print("  Skipping.")
    else:
        print("[3-4] No nested zips found to extract.")

    print()
    print("Done.")


def cli_mode(args):
    """Run in command-line mode based on arguments."""
    if args.download:
        print("[Download]")
        download_corpus()
        print()

    if args.extract_l1:
        print("[Extract Layer 1]")
        extract_layer1()
        print()

    if args.extract_l2:
        print(f"[Extract Layer 2: {args.extract_l2}]")
        extract_layer2(args.extract_l2)
        print()

    if args.extract_l2_all:
        print("[Extract All Layer 2]")
        nested_zips = list_nested_zips()
        if not nested_zips:
            print("  No nested zips found. Run --extract-l1 first.")
        else:
            total_files = 0
            for zip_name in nested_zips:
                total_files += extract_layer2(zip_name)
            print(f"  Total: {total_files} files extracted")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Download and extract the Hyperstition corpus from Hugging Face.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 download_corpus.py                    # Interactive mode
  python3 download_corpus.py --download         # Just download
  python3 download_corpus.py --extract-l1       # Extract outer zip
  python3 download_corpus.py --extract-l2-all   # Extract all nested zips
  python3 download_corpus.py -y --download --extract-l1 --extract-l2-all
        """,
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="Download corpus zip from Hugging Face",
    )
    parser.add_argument(
        "--extract-l1",
        action="store_true",
        help="Extract first layer (outer zip)",
    )
    parser.add_argument(
        "--extract-l2",
        metavar="FILE",
        help="Extract specific nested zip file",
    )
    parser.add_argument(
        "--extract-l2-all",
        action="store_true",
        help="Extract all nested zip files",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmations (for scripting)",
    )

    args = parser.parse_args()

    # Determine mode
    has_cli_args = args.download or args.extract_l1 or args.extract_l2 or args.extract_l2_all

    if has_cli_args:
        cli_mode(args)
    else:
        interactive_mode(args)


if __name__ == "__main__":
    main()
