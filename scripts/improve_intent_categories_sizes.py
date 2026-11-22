from pathlib import Path

path = Path(r"backend\shopsense\engine\intent.py")
source = path.read_text(encoding="utf-8-sig")

# Add category aliases grounded in the development error patterns.
marker = "CATEGORY_ALIASES = {\n"

aliases = '''CATEGORY_ALIASES = {
    "dress": "dresses",
    "jacket": "jackets",
    "rucksack": "backpacks",
    "bag pack": "backpacks",
    "bagpack": "backpacks",
    "backpack": "backpacks",
    "jogger": "track pants",
    "joggers": "track pants",
    "denim": "jeans",
    "denims": "jeans",
    "wrist watch": "watches",
    "wristwatch": "watches",
    "watch": "watches",
    "hoodie": "hoodies",
    "cap": "caps",
    "headset": "headphones",
    "wallet": "wallets",
    "tshirt": "t-shirts",
    "t shirts": "t-shirts",
    "runner": "running shoes",
    "runners": "running shoes",
    "jogging shoe": "running shoes",
    "jogging shoes": "running shoes",
    "running sneaker": "running shoes",
    "running sneakers": "running shoes",
'''

if marker not in source:
    raise SystemExit("CATEGORY_ALIASES marker not found. No changes made.")

source = source.replace(marker, aliases, 1)

# Add spoken numeric sizes and common 2XL forms.
marker = "SIZE_ALIASES = {\n"

size_aliases = '''SIZE_ALIASES = {
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "2xl": "XXL",
    "2 x l": "XXL",
    "2x large": "XXL",
    "double extra-large": "XXL",
    "double-extra-large": "XXL",
'''

if marker not in source:
    raise SystemExit("SIZE_ALIASES marker not found. No changes made.")

source = source.replace(marker, size_aliases, 1)

# Add contextual size extraction before the IntentExtractor class.
class_marker = "\n\nclass IntentExtractor:"

helper = r'''

def _extract_size(text, phrases):
    candidates = []

    for phrase, value in phrases.items():
        for match in _phrase_matches(text, phrase):
            start, end = match.span()
            token = phrase.lower()

            # Single-letter sizes are accepted only with explicit size context.
            if token in ("s", "m", "l"):
                before = text[max(0, start - 16):start]
                after = text[end:end + 16]

                context_ok = (
                    re.search(r"\b(?:size|size is|size of)\s*$", before)
                    or re.match(r"\s*(?:size|sized)\b", after)
                )

                if not context_ok:
                    continue

            # Numeric and spoken shoe/waist sizes need contextual evidence.
            numeric_values = {
                "6", "7", "8", "9", "10", "11",
                "28", "30", "32", "34", "36",
                "six", "seven", "eight", "nine", "ten", "eleven",
            }

            if token in numeric_values:
                before = text[max(0, start - 24):start]
                after = text[end:end + 20]

                context_ok = (
                    re.search(r"\b(?:size|uk|waist)\s*$", before)
                    or re.match(r"\s*(?:uk|waist|size|number)\b", after)
                    or re.search(r"\b(?:das|number)\s*$", before)
                )

                if not context_ok:
                    continue

            candidates.append((start, end, value))

    if not candidates:
        return None

    # Prefer longer phrases when they overlap.
    filtered = []
    for candidate in candidates:
        start, end, value = candidate
        contained = any(
            other_start <= start
            and other_end >= end
            and (other_start < start or other_end > end)
            for other_start, other_end, _ in candidates
        )
        if not contained:
            filtered.append(candidate)

    # The last valid size mention wins, supporting corrections.
    filtered.sort(key=lambda item: (item[0], item[1]))
    return filtered[-1][2]
'''

if class_marker not in source:
    raise SystemExit("IntentExtractor class marker not found. No changes made.")

source = source.replace(class_marker, helper + class_marker, 1)

old_line = "        size = _last_match(text, self.size_phrases)"
new_line = "        size = _extract_size(text, self.size_phrases)"

if old_line not in source:
    raise SystemExit("Size extraction line not found. No changes made.")

source = source.replace(old_line, new_line, 1)

path.write_text(source, encoding="utf-8")
print("Category aliases and contextual size extraction updated.")
