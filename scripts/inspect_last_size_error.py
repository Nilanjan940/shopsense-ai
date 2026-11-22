import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.shopsense.engine.intent import IntentExtractor

extractor = IntentExtractor()

with open("competition/dev.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if row.get("id") == "dev-0159":
            print("EXACT DEV REQUEST:")
            print(row["text"])
            print("\nEXPECTED FILTERS:")
            print(row["filters"])
            print("\nEXTRACTED FILTERS:")
            print(extractor.extract(row["text"]))
            break
