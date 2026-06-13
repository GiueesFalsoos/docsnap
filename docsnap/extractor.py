import json

from anthropic import Anthropic

from .config import CATEGORIES, EXTRACTOR_MODEL


class Extractor:
    def __init__(self):
        self.client = Anthropic()
        self.model = EXTRACTOR_MODEL

    def _build_prompt(self, document_text: str, categoria: str) -> str:
        campi = CATEGORIES[categoria]["campi"]
        campi_json = {campo: "..." for campo in campi}

        lines = [
            f"Estrai i seguenti campi dal documento di tipo '{categoria}':\n",
            *[f"- {campo}" for campo in campi],
            f"\nDocumento:\n{document_text}",
            f"\nRispondi SOLO con un JSON, senza backtick o markdown, nel formato esatto:\n{json.dumps(campi_json)}",
        ]

        return "\n".join(lines)

    def _parse_response(self, response, categoria: str) -> dict:
        text = response.content[0].text
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"La risposta del modello non è un JSON valido: {e}\nRisposta ricevuta: {text!r}")

        campi_attesi = CATEGORIES[categoria]["campi"]
        mancanti = [c for c in campi_attesi if c not in data]
        
            

        return {
            "categoria": categoria,
            "fields": data,
            "missing_fields": mancanti,
            "raw_response": text
        }

    def extract(self, document_text: str, categoria: str) -> dict:
        if categoria not in CATEGORIES:
            raise ValueError(
                f"Categoria '{categoria}' non riconosciuta. "
                f"Categorie valide: {list(CATEGORIES.keys())}"
            )

        prompt = self._build_prompt(document_text, categoria)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_response(response, categoria)
