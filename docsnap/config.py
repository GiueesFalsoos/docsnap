"""Configurazione centrale di DocSnap: modelli, categorie, soglie."""

# --- Modelli ---
# Decisione esplicita costi/qualità:
# Haiku per la classificazione (task semplice, alto volume),
# Sonnet per estrazione e validazione (serve precisione).
CLASSIFIER_MODEL = "claude-haiku-4-5"
EXTRACTOR_MODEL = "claude-sonnet-4-6"
VALIDATOR_MODEL = "claude-sonnet-4-6"

# --- Soglie ---
# Sotto questa confidence il documento non prosegue nella pipeline
# e finisce nella coda "revisione manuale".
CONFIDENCE_THRESHOLD = 0.75

# --- Categorie documentali ---
# Fonte unica di verità: Classifier ed Extractor costruiscono
# i loro prompt leggendo da qui.
CATEGORIES = {
    "fattura": {
        "descrizione": "Fattura di acquisto o vendita con dati fiscali completi",
        "campi": [
            "numero_fattura",
            "data",
            "fornitore",
            "partita_iva_fornitore",
            "imponibile",
            "iva",
            "totale",
        ],
    },
    "ricevuta": {
        "descrizione": "Ricevuta o scontrino per spese senza fattura",
        "campi": [
            "data",
            "esercente",
            "importo",
            "metodo_pagamento",
            "descrizione_spesa",
        ],
    },
    "estratto_conto": {
        "descrizione": "Estratto conto bancario periodico",
        "campi": [
            "banca",
            "intestatario",
            "iban",
            "periodo",
            "saldo_iniziale",
            "saldo_finale",
        ],
    },
    "contratto": {
        "descrizione": "Contratto tra parti con valore legale ed economico",
        "campi": [
            "parti",
            "oggetto",
            "data_firma",
            "durata",
            "valore_economico",
        ],
    },
    "comunicazione_fiscale": {
        "descrizione": "Comunicazione da enti fiscali (Agenzia Entrate, INPS, ecc.)",
        "campi": [
            "ente_emittente",
            "tipo_comunicazione",
            "data",
            "scadenza",
            "importo_dovuto",
        ],
    },
}