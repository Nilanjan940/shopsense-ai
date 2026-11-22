from pathlib import Path

path = Path(r"backend\shopsense\engine\intent.py")
source = path.read_text(encoding="utf-8-sig")

old = 'r"hundred|thousand|and)"'
new = 'r"hundred|thousand|and))"'

if old not in source:
    raise SystemExit("Expected regex text not found. No changes made.")

source = source.replace(old, new, 1)
path.write_text(source, encoding="utf-8")

print("Fixed the missing closing parenthesis.")
