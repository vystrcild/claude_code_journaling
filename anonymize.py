#!/usr/bin/env python3
"""
anonymize.py — Optional pre-processing step for claude_code_journaling.

Replaces names listed in names.txt with abstract labels (Person-A, Person-B, etc.)
before journal entries are sent to the Anthropic API. Original files are never modified.

IMPORTANT LIMITATIONS:
- Only protects names you explicitly list in names.txt. There is no automatic detection.
- Does NOT protect the content of your entries (events, situations, medical details, etc.).
  Sensitive content transmits to the API regardless of name replacement.
- names.txt itself is sensitive — it contains your real name mappings. Keep it local.

Usage:
    python anonymize.py --month 2026-03
    python anonymize.py --all

Output is written to journals-anonymized/ (git-ignored).
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


NAMES_FILE = Path("names.txt")
OUTPUT_DIR = Path("journals-anonymized")


def load_name_mappings(names_file: Path) -> List[Tuple[str, str]]:
    """
    Parse names.txt and return a list of (real_name, label) tuples,
    sorted by length descending so longer names are replaced before shorter ones.
    This prevents partial-match issues (e.g., "Ann" inside "Annabelle").
    """
    if not names_file.exists():
        print(
            f"Error: {names_file} not found.\n"
            f"Copy names.txt.example to names.txt and add your name mappings.",
            file=sys.stderr,
        )
        sys.exit(1)

    mappings = []
    with names_file.open() as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "→" not in line:
                print(
                    f"Warning: Skipping malformed line {line_num} in {names_file}: {line!r}\n"
                    f"Expected format: RealName → Label",
                    file=sys.stderr,
                )
                continue
            parts = line.split("→", 1)
            real_name = parts[0].strip()
            label = parts[1].strip()
            if real_name and label:
                mappings.append((real_name, label))

    if not mappings:
        print(f"Warning: No valid mappings found in {names_file}.", file=sys.stderr)

    # Sort by length descending so longer names are replaced first
    mappings.sort(key=lambda x: len(x[0]), reverse=True)
    return mappings


def anonymize_text(text: str, mappings: List[Tuple[str, str]]) -> str:
    """Apply all name replacements to a block of text. Case-insensitive."""
    for real_name, label in mappings:
        # Use word-boundary matching to avoid replacing substrings inside other words
        pattern = re.compile(re.escape(real_name), re.IGNORECASE)
        text = pattern.sub(label, text)
    return text


def find_journal_files(month: Optional[str]) -> List[Path]:
    """
    Find journal files matching the given month (YYYY-MM) or all journals if month is None.
    Searches common journal directory patterns used by this project.
    """
    search_dirs = [
        Path("06 Agenda/Journal"),
        Path("Journal"),
        Path("journals"),
    ]

    pattern = f"{month}-*.md" if month else "*.md"
    found = []

    for search_dir in search_dirs:
        if search_dir.exists():
            found.extend(search_dir.glob(pattern))

    if not found:
        checked = ", ".join(str(d) for d in search_dirs)
        print(
            f"No journal files found for {'month ' + month if month else 'any month'}.\n"
            f"Searched: {checked}",
            file=sys.stderr,
        )
        sys.exit(1)

    return sorted(found)


def anonymize_files(journal_files: List[Path], mappings: List[Tuple[str, str]]) -> None:
    """Anonymize a list of journal files and write output to journals-anonymized/."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    replaced_count = 0
    for journal_path in journal_files:
        original_text = journal_path.read_text(encoding="utf-8")
        anonymized_text = anonymize_text(original_text, mappings)

        # Preserve original filename, write to output dir
        output_path = OUTPUT_DIR / journal_path.name
        output_path.write_text(anonymized_text, encoding="utf-8")

        names_replaced = sum(
            len(re.findall(re.compile(re.escape(name), re.IGNORECASE), original_text))
            for name, _ in mappings
        )
        replaced_count += names_replaced
        print(f"  {journal_path.name} → {output_path} ({names_replaced} replacements)")

    print(
        f"\nDone. {len(journal_files)} file(s) written to {OUTPUT_DIR}/  "
        f"({replaced_count} total name replacements)"
    )
    print(
        "\nReminder: anonymization only covers the names listed in names.txt.\n"
        "Content-level sensitive information (events, situations, etc.) is not protected."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonymize journal entries by replacing names with abstract labels."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--month",
        metavar="YYYY-MM",
        help="Process journals for a specific month (e.g. 2026-03)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Process all journal files found",
    )
    args = parser.parse_args()

    print(f"Loading name mappings from {NAMES_FILE}...")
    mappings = load_name_mappings(NAMES_FILE)
    print(f"  {len(mappings)} mapping(s) loaded.")

    month = args.month if not args.all else None
    print(f"\nFinding journal files{' for ' + month if month else ''}...")
    journal_files = find_journal_files(month)
    print(f"  {len(journal_files)} file(s) found.")

    print(f"\nAnonymizing to {OUTPUT_DIR}/...")
    anonymize_files(journal_files, mappings)


if __name__ == "__main__":
    main()
