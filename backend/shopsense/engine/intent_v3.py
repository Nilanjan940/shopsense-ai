import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOGUE_PATH = PROJECT_ROOT / "competition" / "catalogue.csv"

FILTER_FIELDS = ("brand", "category", "colour", "size")

CATEGORY_ALIASES = {
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
    "trainers": "sneakers",
    "trainer": "sneakers",
    "shoes": "sneakers",
    "sneaker": "sneakers",
    "shirt": "shirts",
    "kurta": "kurtas",
    "shirt": "shirts",
    "kurta": "kurtas",
    "slides": "sandals",
    "slide": "sandals",
    "floaters": "sandals",
    "floater": "sandals",
    "flip flops": "sandals",
    "flip-flops": "sandals",
    "hooded sweatshirt": "hoodies",
    "hooded sweatshirts": "hoodies",
    "sweatshirt": "hoodies",
    "sweatshirts": "hoodies",
    "t shirt": "t-shirts",
    "t-shirt": "t-shirts",
    "tee": "t-shirts",
    "tees": "t-shirts",
    "trouser": "track pants",
    "trousers": "track pants",
    "trackpant": "track pants",
    "trackpants": "track pants",
}

COLOUR_ALIASES = {
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
}

SIZE_ALIASES = {
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "das": "10",
    "eleven": "11",
    "2xl": "XXL",
    "2 x l": "XXL",
    "2x large": "XXL",
    "double extra-large": "XXL",
    "double-extra-large": "XXL",
    "small": "S",
    "medium": "M",
    "large": "L",
    "extra small": "XS",
    "extra-small": "XS",
    "xs": "XS",
    "extra large": "XL",
    "extra-large": "XL",
    "x large": "XL",
    "xl": "XL",
    "double extra large": "XXL",
    "double xl": "XXL",
    "xxl": "XXL",
}


ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}

TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

NUMBER_WORDS = set(ONES) | set(TENS) | {"hundred", "thousand", "and"}


def _normalise(text):
    return re.sub(r"\s+", " ", str(text).lower().replace("-", " ")).strip()


def _load_catalogue_vocabulary():
    if not CATALOGUE_PATH.exists():
        raise FileNotFoundError(
            f"Catalogue not found: {CATALOGUE_PATH}"
        )

    vocabulary = {field: set() for field in FILTER_FIELDS}

    with CATALOGUE_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for field in FILTER_FIELDS:
                value = (row.get(field) or "").strip()
                if value:
                    vocabulary[field].add(value)

    return vocabulary




def _phrase_matches(text, phrase):
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


def _number_from_words(words):
    total = 0
    current = 0
    found = False

    for word in words:
        if word == "and":
            continue
        if word in ONES:
            current += ONES[word]
            found = True
        elif word in TENS:
            current += TENS[word]
            found = True
        elif word == "hundred":
            current = max(1, current) * 100
            found = True
        elif word == "thousand":
            total += max(1, current) * 1000
            current = 0
            found = True
        else:
            break

    return total + current if found else None



def _extract_budget(text):
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
            re.compile(r"\bpaanch\s+hazaar\b"),
            lambda m: 5000,
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



def _extract_size(text, phrases):
    candidates = []

    numeric_values = {
        "6", "7", "8", "9", "10", "11",
        "28", "30", "32", "34", "36",
        "six", "seven", "eight", "nine", "ten", "eleven",
        "das",
    }

    word_sizes = {"small", "medium", "large"}

    apparel_terms = {
        "shirt", "shirts", "t shirt", "t shirts", "tshirt",
        "tee", "tees", "hoodie", "hoodies",
        "jacket", "jackets", "dress", "dresses",
        "kurta", "kurtas", "jeans", "denim", "denims",
        "track pants", "trackpants", "joggers", "pants",
        "sweatshirt", "sweatshirts", "sneakers", "sneaker",
        "shoes", "shoe", "trainers", "runners",
        "floaters", "slides", "sandals", "caps", "cap",
        "backpack", "backpacks", "rucksack",
        "headphones", "headset", "watches", "watch",
        "wallet", "wallets",
    }

    blocked_contexts = {
        "budget", "price", "priced", "pricing",
        "collection", "collections",
        "selection", "selections",
        "range", "amount", "quantity",
        "number", "group", "variety",
        "portion", "fit", "business",
    }

    has_apparel_context = any(
        _phrase_matches(text, term)
        for term in apparel_terms
    )

    for phrase, value in phrases.items():
        token = phrase.lower()

        for match in _phrase_matches(text, phrase):
            start, end = match.span()
            before = text[max(0, start - 60):start]
            after = text[end:end + 40]

            # Single-letter sizes remain conservative.
            if token in ("s", "m", "l"):
                explicit_context = (
                    re.search(r"\b(?:size|sized)\s*$", before)
                    or re.match(r"\s*(?:size|sized)\b", after)
                )

                correction_context = re.search(
                    r"\b(?:size|sized)\b"
                    r"[^.!?]{0,40}"
                    r"\b(?:actually|oops|no|no no|nahi|"
                    r"i mean|meant|wait|make it|change to|"
                    r"switch to|go with)\s*$",
                    before
                )

                implicit_correction = (
                    re.search(
                        r"\b(?:make it|change to|switch to|go with)\s*$",
                        before
                    )
                    and re.match(r"\s+instead\b", after)
                )

                if not (
                    explicit_context
                    or correction_context
                    or implicit_correction
                ):
                    continue

            # Preserve V1's numeric-size recognition and correction logic.
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

                correction_context = re.search(
                    r"\b(?:size|uk|waist|number)\b"
                    r"[^.!?]{0,40}"
                    r"\b(?:actually|oops|no|no no|i mean|meant|wait)\b"
                    r"(?:(?!\b(?:size|uk|waist|number)\b)[^.!?]){0,24}$",
                    before
                )

                # Do not interpret monetary quantities as sizes:
                # "under eight hundred", "below ten thousand", etc.
                monetary_amount = re.match(
                    r"\s+(?:hundred|thousand|lakh|lakhs)\b",
                    after
                )

                monetary_lead = re.search(
                    r"\b(?:under|below|less than|within|upto|up to|max)\s*$",
                    before
                )

                if monetary_amount and monetary_lead:
                    continue

                if not (direct_context or correction_context):
                    continue

            # Natural-language S/M/L expressions.
            if token in word_sizes:
                explicit_context = (
                    re.search(r"\b(?:size|sized)\s*$", before)
                    or re.match(r"\s*(?:size|sized)\b", after)
                )

                next_word = re.match(r"\s+([a-z]+)", after)
                next_token = next_word.group(1) if next_word else ""

                blocked_context = next_token in blocked_contexts

                # A size may follow an already-mentioned product:
                # "black jacket ... medium budget".
                product_before = any(
                    term_match.end() <= start
                    for term in apparel_terms
                    for term_match in _phrase_matches(text, term)
                )

                budget_size_context = (
                    next_token == "budget"
                    and product_before
                )

                correction_context = re.search(
                    r"\b(?:size|uk|waist)\b"
                    r"[^.!?]{0,50}"
                    r"\b(?:actually|oops|no|no no|nahi|"
                    r"i mean|meant|wait|change|switch)\b"
                    r"[^.!?]{0,30}$",
                    before
                )

                if blocked_context and not budget_size_context:
                    continue

                if not (
                    explicit_context
                    or has_apparel_context
                    or correction_context
                ):
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

    # Last valid size mention wins.
    filtered.sort(key=lambda item: (item[0], item[1]))
    return filtered[-1][2]


class IntentExtractor:
    def __init__(self, catalogue_path=None):
        global CATALOGUE_PATH

        if catalogue_path is not None:
            CATALOGUE_PATH = Path(catalogue_path)

        self.vocabulary = _load_catalogue_vocabulary()

        # Only use aliases whose destination exists in the catalogue.
        self.category_phrases = {
            value.lower(): value
            for value in self.vocabulary["category"]
        }
        for alias, destination in CATEGORY_ALIASES.items():
            if destination in self.vocabulary["category"]:
                self.category_phrases[alias] = destination

        self.colour_phrases = {
            value.lower(): value
            for value in self.vocabulary["colour"]
        }
        for alias, destination in COLOUR_ALIASES.items():
            if destination in self.vocabulary["colour"]:
                self.colour_phrases[alias] = destination

        self.size_phrases = {
            value.lower(): value
            for value in self.vocabulary["size"]
        }
        for alias, destination in SIZE_ALIASES.items():
            if destination in self.vocabulary["size"]:
                self.size_phrases[alias] = destination

        self.brand_phrases = {
            value.lower(): value
            for value in self.vocabulary["brand"]
        }

    def extract(self, text):
        text = _normalise(text)
        filters = {}

        category = _last_match(text, self.category_phrases)
        colour = _last_match(text, self.colour_phrases)
        size = _extract_size(text, self.size_phrases)
        brand = _last_match(text, self.brand_phrases)
        budget = _extract_budget(text)

        if category:
            filters["category"] = category
        if colour:
            filters["colour"] = colour
        if size:
            filters["size"] = size
        if brand:
            filters["brand"] = brand
        if budget is not None:
            filters["max_price"] = budget

        return filters
