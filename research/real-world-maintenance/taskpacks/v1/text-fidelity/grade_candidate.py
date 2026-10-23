#!/usr/bin/env python3
"""Controller-only arbitrary retained candidate grading entry point."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from candidate_grade import main

if __name__ == '__main__':
    sys.exit(main(Path(__file__).resolve().parent))
