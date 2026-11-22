from pathlib import Path

path = Path(r"backend\shopsense\engine\intent.py")
source = path.read_text(encoding="utf-8-sig")

start = source.index("def _extract_budget(text):")
end = source.index("\n\nclass IntentExtractor:", start)

replacement = r'''
def _extract_budget(text):
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

    candidates = []

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

        words = re.findall(r"[a-z]+", remainder.lower())
        number_words = []

        for word in words:
            if word not in NUMBER_WORDS:
                break
            number_words.append(word)

        amount = _number_from_words(number_words)

        if amount is not None:
            candidates.append((trigger.start(), amount))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]
'''

source = source[:start] + replacement + source[end:]
path.write_text(source, encoding="utf-8")

print("Budget extraction function replaced successfully.")
