from pathlib import Path

path = Path("backend/shopsense/engine/intent.py")
source = path.read_text(encoding="utf-8")

old = '''        (
            re.compile(r"\\bdhai\\s+hazaar\\b"),
            lambda m: 2500,
        ),'''

new = '''        (
            re.compile(r"\\bpaanch\\s+hazaar\\b"),
            lambda m: 5000,
        ),
        (
            re.compile(r"\\bdhai\\s+hazaar\\b"),
            lambda m: 2500,
        ),'''

if old not in source:
    raise SystemExit("ERROR: Expected insertion point not found.")

source = source.replace(old, new, 1)
compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")

print("Added paanch hazaar = 5000.")
print("Syntax validation: PASS")
