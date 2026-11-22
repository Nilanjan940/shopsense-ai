import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from shopsense.engine.intent import IntentExtractor


class Agent:
    def __init__(self, tools):
        self.tools = tools
        self.extractor = IntentExtractor()
        self.start(None)

    def start(self, request_id):
        self.request_id = request_id
        self.words = []
        self.text = ""
        self.filters = {}
        self.final_product = None

    def observe(self, word):
        self.words.append(str(word))
        self.text = " ".join(self.words)

        self.filters = self.extractor.extract(self.text)

        # No commitment during the initial conservative benchmark.
        return {"filters": dict(self.filters)}

    def finish(self):
        if not self.words:
            return None

        self.text = " ".join(self.words)
        self.filters = self.extractor.extract(self.text)

        # One full-filter catalogue search.
        results = self.tools.search(
            query=self.text,
            filters=self.filters,
            k=100,
        )

        if results:
            self.final_product = results[0]["product_id"]
        else:
            self.final_product = None

        return self.final_product
