from pathlib import Path

path = Path("backend/shopsense/engine/intent.py")
source = path.read_text(encoding="utf-8")

# 1. Add the Hinglish alias.
old_alias = '    "ten": "10",'
new_alias = '    "ten": "10",\n    "das": "10",'

if '"das": "10"' not in source:
    if old_alias not in source:
        raise SystemExit("ERROR: Could not find the expected ten alias.")
    source = source.replace(old_alias, new_alias, 1)

# 2. Replace numeric phrase matching.
start = source.index("def _phrase_matches(text, phrase):")
end = source.index("\ndef _last_match(", start)

new_matching = r'''def _phrase_matches(text, phrase):
    phrase = _normalise(phrase)

    if phrase.isdigit():
        # Allow punctuation after a size, but never match a number
        # that is part of a comma-separated or decimal price.
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(phrase)
            + r"(?![a-z0-9]|\s*[,.]\s*\d)"
        )
    else:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(phrase)
            + r"(?![a-z0-9])"
        )

    return list(re.finditer(pattern, text))
'''

source = source[:start] + new_matching + source[end:]

# 3. Replace contextual size extraction.
start = source.index("def _extract_size(text, phrases):")
end = source.index("\n\nclass IntentExtractor:", start)

new_extractor = r'''def _extract_size(text, phrases):
    candidates = []

    numeric_values = {
        "6", "7", "8", "9", "10", "11",
        "28", "30", "32", "34", "36",
        "six", "seven", "eight", "nine", "ten", "eleven",
        "das",
    }

    for phrase, value in phrases.items():
        token = phrase.lower()

        for match in _phrase_matches(text, phrase):
            start, end = match.span()
            before = text[max(0, start - 40):start]
            after = text[end:end + 24]

            # Single-letter sizes must have explicit size context.
            if token in ("s", "m", "l"):
                context_ok = (
                    re.search(
                        r"\b(?:size|sized)\s*$",
                        before
                    )
                    or re.match(
                        r"\s*(?:size|sized)\b",
                        after
                    )
                )

                if not context_ok:
                    continue

            # Numeric sizes and their spoken equivalents need context.
            if token in numeric_values:
                direct_context = (
                    re.search(
                        r"\b(?:size|uk|waist)\s*$",
                        before
                    )
                    or re.match(
                        r"\s*(?:uk|waist|size|number)\b",
                        after
                    )
                    or re.search(
                        r"\b(?:das|number)\s*$",
                        before
                    )
                )

                # Carry size context through explicit corrections:
                # "size eight actually six"
                # "UK 8, no, 6"
                correction_context = re.search(
                    r"\b(?:size|uk|waist|number)\b"
                    r"[^.!?]{0,40}"
                    r"\b(?:actually|oops|no|no no|i mean|meant|wait)\b"
                    r"[^.!?]{0,24}$",
                    before
                )

                if not (direct_context or correction_context):
                    continue

            candidates.append((start, end, value))

    if not candidates:
        return None

    # Prefer longer phrases when matches overlap.
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

source = source[:start] + new_extractor + source[end:]

compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")

print("Size extraction patch applied successfully.")
print("Python syntax validation: PASS")
