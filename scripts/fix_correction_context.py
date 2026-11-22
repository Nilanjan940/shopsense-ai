from pathlib import Path

path = Path("backend/shopsense/engine/intent.py")
source = path.read_text(encoding="utf-8")

old = r'''                correction_context = re.search(
                    r"\b(?:size|uk|waist|number)\b"
                    r"[^.!?]{0,40}"
                    r"\b(?:actually|oops|no|no no|i mean|meant|wait)\b"
                    r"[^.!?]{0,24}$",
                    before
                )'''

new = r'''                correction_context = re.search(
                    r"\b(?:size|uk|waist|number)\b"
                    r"[^.!?]{0,40}"
                    r"\b(?:actually|oops|no|no no|i mean|meant|wait)\b"
                    r"(?:(?!\b(?:size|uk|waist|number)\b)[^.!?]){0,24}$",
                    before
                )'''

if old not in source:
    raise SystemExit("ERROR: Expected correction-context block not found. No changes made.")

source = source.replace(old, new, 1)
compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")

print("Correction-context boundary fixed.")
print("Syntax validation: PASS")
