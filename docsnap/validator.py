import json

from anthropic import Anthropic

from .config import CATEGORIES, VALIDATOR_MODEL


class Validator:
    def __init__(self):
        self.client = Anthropic()
        self.model = VALIDATOR_MODEL

    def _validate_structure(self, categoria: str, fields: dict, missing_fields: list) -> tuple[list, list]:
        errors = []
        warnings = []

        for campo in missing_fields:
            warnings.append(f"Campo mancante: '{campo}'")

        for campo, valore in fields.items():
            if valore is None or str(valore).strip() in ("", "...", "null", "N/A", "n/a"):
                warnings.append(f"Campo '{campo}' è vuoto o non compilato")

        return errors, warnings

    def _build_prompt(self, categoria: str, fields: dict) -> str:
        descrizione = CATEGORIES[categoria]["descrizione"]

        lines = [
            f"Sei un validatore di documenti fiscali e amministrativi.",
            f"Hai estratto i seguenti campi da un documento di tipo '{categoria}' ({descrizione}):\n",
            json.dumps(fields, ensure_ascii=False, indent=2),
            "\nAnalizza i valori e identifica:",
            "- ERRORI: valori palesemente errati o incoerenti (es. totale diverso da imponibile+IVA, data impossibile, P.IVA con formato sbagliato)",
            "- WARNING: valori sospetti o anomali ma non necessariamente errati (es. importo insolitamente alto, data futura)",
            "\nRispondi SOLO con un JSON senza backtick nel formato esatto:",
            '{"errors": ["...", "..."], "warnings": ["...", "..."]}',
            "\nSe non ci sono errori o warning usa liste vuote.",
        ]

        return "\n".join(lines)

    def _parse_response(self, response) -> tuple[list, list]:
        text = response.content[0].text
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"La risposta del modello non è un JSON valido: {e}\nRisposta ricevuta: {text!r}")

        if "errors" not in data or "warnings" not in data:
            raise ValueError("La risposta del modello non contiene i campi 'errors' e 'warnings'.")

        return data["errors"], data["warnings"]

    def validate(self, extraction_result: dict) -> dict:
        categoria = extraction_result["categoria"]
        fields = extraction_result["fields"]
        missing_fields = extraction_result.get("missing_fields", [])

        struct_errors, struct_warnings = self._validate_structure(categoria, fields, missing_fields)

        llm_errors, llm_warnings = [], []
        if not struct_errors:
            prompt = self._build_prompt(categoria, fields)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            llm_errors, llm_warnings = self._parse_response(response)

        errors = struct_errors + llm_errors
        warnings = struct_warnings + llm_warnings

        return {
            **extraction_result,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
