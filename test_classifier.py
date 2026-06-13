"test del classifier"
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from docsnap.classifier import Classifier


SAMPLE_DOCS = Path(__file__).parent / "sample_docs"


def extract_expected_category(filename: str) -> str:
    return Path(filename).stem.rsplit("_", 1)[0]


def main():
    classifier = Classifier()
    txt_files = sorted(SAMPLE_DOCS.glob("*.txt"))

    if not txt_files:
        print("Nessun file .txt trovato in sample_docs/")
        sys.exit(1)

    ok = 0
    total = len(txt_files)

    for path in txt_files:
        expected = extract_expected_category(path.name)
        document_text = path.read_text(encoding="utf-8")

        result = classifier.classify(document_text)

        predicted = result["categoria"]
        confidence = result["confidence"]
        low_conf = result["low_confidence"]
        correct = predicted == expected

        status = "CORRETTO" if correct else f"ERRATO (atteso: {expected})"
        ok += correct

        print(
            f"File:           {path.name}\n"
            f"Categoria:      {predicted}\n"
            f"Confidence:     {confidence:.2f}\n"
            f"Low confidence: {low_conf}\n"
            f"Risultato:      {status}\n"
            f"{'-' * 45}"
        )

    print(f"\nAccuratezza: {ok}/{total} ({ok / total * 100:.0f}%)")


if __name__ == "__main__":
    main()
