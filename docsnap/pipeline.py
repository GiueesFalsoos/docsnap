from .classifier import Classifier
from .extractor import Extractor
from .validator import Validator

class Pipeline:
    def __init__(self):
        self.classifier = Classifier()
        self.extractor = Extractor()
        self.validator = Validator()

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
        validatore = self.validator.validate(campi)

        return {
            "status": "ok",
            "categoria": categoria,
            "confidence": classification["confidence"],
            "campi": validatore,
        }
