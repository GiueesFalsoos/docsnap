import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from docsnap.pipeline import Pipeline


SAMPLE_DOCS = Path(__file__).parent / "sample_docs"


def extract_expected_category(filename: str) -> str:
    return Path(filename).stem.rsplit("_", 1)[0]


def main():
    pipeline = Pipeline()
    txt_files = sorted(SAMPLE_DOCS.glob("*.txt"))

    if not txt_files:
        print("Nessun file .txt trovato in sample_docs/")
        sys.exit(1)

    ok = 0
    total = len(txt_files)

    for path in txt_files:
        expected = extract_expected_category(path.name)
        document_text = path.read_text(encoding="utf-8")

        result = pipeline.run(document_text)

        categoria = result["categoria"]
        confidence = result["confidence"]
        status = result["status"]
        correct = categoria == expected
        campi = result["campi"]

        ok += correct
        esito = "CORRETTO" if correct else f"ERRATO (atteso: {expected})"

        print(f"File:       {path.name}")
        print(f"Status:     {status}")
        print(f"Categoria:  {categoria}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Risultato:  {esito}")

        if status == "ok":
            campi = result["campi"]
            if campi.get("missing_fields"):
                print(f"Campi mancanti: {campi['missing_fields']}")
            print("Campi estratti:")
            for campo, valore in campi["fields"].items():
                print(f"  {campo}: {valore}")
            if campi.get("errors"):
                print(f"Errori: {campi['errors']}")
            if campi.get("warnings"):
                print(f"Warning: {campi['warnings']}")    
        else:
            print("Estrazione saltata: confidence sotto soglia.")

        print("-" * 45)

    print(f"\nAccuratezza classificazione: {ok}/{total} ({ok / total * 100:.0f}%)")
    

if __name__ == "__main__":
    main()
