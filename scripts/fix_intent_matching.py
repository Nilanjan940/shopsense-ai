from pathlib import Path

path = Path(r"backend\shopsense\engine\intent.py")
source = path.read_text(encoding="utf-8-sig")

# 1. Replace phrase matching so numbers inside prices are not treated as sizes.
start = source.index("def _phrase_matches(text, phrase):")
end = source.index("\n\ndef _last_match", start)

replacement = r'''
def _phrase_matches(text, phrase):
    phrase = _normalise(phrase)

    # Commas and decimal points are boundaries for words, but not for
    # numeric sizes: this prevents matching "7" inside "7,500".
    if phrase.isdigit():
        pattern = r"(?<![a-z0-9,.])" + re.escape(phrase) + r"(?![a-z0-9,.])"
    else:
        pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"

    return list(re.finditer(pattern, text))
'''

source = source[:start] + replacement + source[end:]

# 2. Replace selection logic: prefer longer overlapping phrases,
# then choose the latest remaining occurrence for corrections.
start = source.index("def _last_match(text, phrases):")
end = source.index("\n\ndef _number_from_words", start)

replacement = r'''
def _last_match(text, phrases):
    candidates = []

    for phrase, value in phrases.items():
        for match in _phrase_matches(text, phrase):
            candidates.append((match.start(), match.end(), value))

    if not candidates:
        return None

    # Remove matches contained inside a longer phrase.
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

    # Latest occurrence wins, preserving corrections such as M -> XS.
    filtered.sort(key=lambda item: (item[0], item[1]))
    return filtered[-1][2]
'''

source = source[:start] + replacement + source[end:]

# 3. Add common singular category aliases.
source = source.replace(
    '"sneaker": "sneakers",',
    '"sneaker": "sneakers",\n    "shirt": "shirts",\n    "kurta": "kurtas",',
    1,
)

path.write_text(source, encoding="utf-8")
print("Intent matching corrections applied.")
