from .classifier import Classifier
from .extractor import Extractor


class Pipeline:
    def __init__(self):
        self.classifier = Classifier()
        self.extractor = Extractor()

    def run(self, document_text: str) -> dict:
        classification = self.classifier.classify(document_text)

        if classification["low_confidence"]:
            return {
                "status": "revisione_manuale",
                "categoria": classification["categoria"],
                "confidence": classification["confidence"],
                "campi": None,
            }

        categoria = classification["categoria"]
        campi = self.extractor.extract(document_text, categoria)

        return {
            "status": "ok",
            "categoria": categoria,
            "confidence": classification["confidence"],
            "campi": campi,
        }
