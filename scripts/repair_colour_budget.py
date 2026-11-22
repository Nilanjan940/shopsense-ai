from pathlib import Path
import re

path = Path("backend/shopsense/engine/intent.py")
source = path.read_text(encoding="utf-8")

# 1. Add the observed Hindi/Hinglish colour aliases.
start = source.index("COLOUR_ALIASES = {")
end = source.index("\n\nSIZE_ALIASES =", start)

new_colours = '''COLOUR_ALIASES = {
    "navy blue": "navy",
    "dark blue": "navy",
    "olive green": "olive",
    "grey": "grey",
    "gray": "grey",
    "kaala": "black",
    "kala": "black",
    "gulabi": "pink",
    "laal": "red",
    "bhura": "brown",
    "golden": "gold",
}'''

source = source[:start] + new_colours + source[end:]


# 2. Replace budget extraction with a more robust implementation.
start = source.index("def _extract_budget(text):")
end = source.index("\n\ndef _extract_size(", start)

new_budget = r'''def _extract_budget(text):
    candidates = []

    # Hindi number vocabulary used by the observed development requests.
    hindi_numbers = {
        "ek": 1,
        "do": 2,
        "teen": 3,
        "char": 4,
        "chaar": 4,
        "paanch": 5,
        "che": 6,
        "chhe": 6,
        "saat": 7,
        "aath": 8,
        "nau": 9,
        "das": 10,
        "pandrah": 15,
        "satrah": 17,
        "bees": 20,
        "pachis": 25,
        "pachchis": 25,
        "tees": 30,
    }

    # Numeric amounts followed by Hindi budget expressions:
    # "2000 tak", "1700 se kam", "1500 ke andar".
    numeric_before_marker = re.compile(
        r"(?<![a-z0-9])"
        r"(\d[\d,]*(?:\.\d+)?)"
        r"\s*(?:rupees?|rs\.?|inr)?\s*"
        r"(?:tak|se\s+kam|ke\s+andar|ke\s+under)",
        re.IGNORECASE,
    )

    for match in numeric_before_marker.finditer(text):
        amount = float(match.group(1).replace(",", ""))
        candidates.append((match.start(), int(amount)))

    # Hindi amounts:
    # "saadhe teen hazaar" = 3500
    # "dhai hazaar" = 2500
    # "dedh hazaar" = 1500
    # "pandrah sau" = 1500
    # "satrah sau" = 1700
    hindi_patterns = [
        (
            re.compile(
                r"\bsaadhe\s+(ek|do|teen|char|chaar|paanch|che|chhe|"
                r"saat|aath|nau|das)\s+hazaar\b"
            ),
            lambda m: hindi_numbers[m.group(1)] * 1000 + 500,
        ),
        (
            re.compile(r"\bdhai\s+hazaar\b"),
            lambda m: 2500,
        ),
        (
            re.compile(r"\bdedh\s+hazaar\b"),
            lambda m: 1500,
        ),
        (
            re.compile(
                r"\b(pandrah|satrah|bees|pachis|pachchis|tees)\s+sau\b"
            ),
            lambda m: hindi_numbers[m.group(1)] * 100,
        ),
    ]

    for pattern, converter in hindi_patterns:
        for match in pattern.finditer(text):
            candidates.append((match.start(), converter(match)))

    # English and numeric budget triggers.
    trigger_pattern = re.compile(
        r"\b(?:under|below|less than|not more than|up to|upto|"
        r"within|maximum|max|budget(?: of)?|at most)\b",
        re.IGNORECASE,
    )

    numeric_pattern = re.compile(
        r"^\s*(?:₹|rs\.?|inr)?\s*"
        r"(\d[\d,]*(?:\.\d+)?)\s*(k|thousand)?",
        re.IGNORECASE,
    )

    for trigger in trigger_pattern.finditer(text):
        remainder = text[trigger.end():]

        numeric = numeric_pattern.match(remainder)
        if numeric:
            amount = float(numeric.group(1).replace(",", ""))
            suffix = (numeric.group(2) or "").lower()

            if suffix in ("k", "thousand"):
                amount *= 1000

            candidates.append((trigger.start(), int(amount)))
            continue

        # Do not allow number words to continue into another sentence.
        first_sentence = re.split(r"[.!?]", remainder, maxsplit=1)[0]
        words = re.findall(r"[a-z]+", first_sentence.lower())

        number_words = []
        for word in words:
            if word not in NUMBER_WORDS:
                break
            number_words.append(word)

        amount = _number_from_words(number_words)

        if amount is not None:
            candidates.append((trigger.start(), amount))

        # Also support Hindi word budgets after "budget".
        for pattern, converter in hindi_patterns:
            match = pattern.search(remainder)
            if match:
                candidates.append((trigger.start(), converter(match)))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]
'''

source = source[:start] + new_budget + source[end:]

compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")

print("Colour aliases updated.")
print("Hindi/Hinglish budget extraction updated.")
print("English sentence-boundary handling updated.")
print("Syntax validation: PASS")
