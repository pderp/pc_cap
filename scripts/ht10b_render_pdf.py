"""Small plotting-environment entry point for already-bound deck-v2 slide data."""

import argparse
import json
from pathlib import Path

from scripts.ht10_slide_deck import pdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slides", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pdf(json.loads(args.slides.read_text()), args.output)
