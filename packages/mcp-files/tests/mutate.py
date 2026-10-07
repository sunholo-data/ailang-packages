"""Apply one mutant to a package copy: replace OLD with NEW in FILE, exactly
once (a mutant whose anchor is missing or ambiguous is an error, not a pass).
Usage: python3 -I mutate.py <file> <old> <new>"""
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path, encoding="utf-8").read()
n = text.count(old)
if n != 1:
    print(f"anchor found {n} times in {path}: {old!r}")
    sys.exit(2)
open(path, "w", encoding="utf-8").write(text.replace(old, new))
