import json
from anthropic import Anthropic

from .config import CATEGORIES, CLASSIFIER_MODEL, CONFIDENCE_THRESHOLD


class Classifier:
    def __init__(self):
        self.client = Anthropic()
        self.model = CLASSIFIER_MODEL
        self.threshold = CONFIDENCE_THRESHOLD

    def _build_prompt(self, document_text: str) -> str:
        lines = ["Classifica il documento in una delle seguenti categorie:\n"]

        for name, meta in CATEGORIES.items():
            lines.append(f"- {name}: {meta['descrizione']}")

        lines.append(f"\nDocumento:\n{document_text}")
        lines.append(
            '\nRispondi SOLO con un JSON, Non usare backtick o markdown nel formato esatto: {"categoria": "...", "confidence": 0.0}'
            
        )

        return "\n".join(lines)

    def _parse_response(self, response) -> dict:
        text = response.content[0].text
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"La risposta del modello non è un JSON valido: {e}\nRisposta ricevuta: {text!r}")

        if "categoria" not in data:
            raise ValueError("Campo 'categoria' mancante nella risposta del modello.")
        if "confidence" not in data:
            raise ValueError("Campo 'confidence' mancante nella risposta del modello.")
        if data["categoria"] not in CATEGORIES:
            raise ValueError(
                f"Categoria '{data['categoria']}' non riconosciuta. "
                f"Categorie valide: {list(CATEGORIES.keys())}"
            )

        return data

    def classify(self, document_text: str) -> dict:
        prompt = self._build_prompt(document_text)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )

        result = self._parse_response(response)

        result["low_confidence"] = result["confidence"] < self.threshold

        return result
