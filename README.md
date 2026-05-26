# PROGETTO_KNOWLEDGE_GRAPH

Breve guida per rigenerare e validare il grafo RDF usando `sparql-anything`.

Prerequisiti
- Java (per `sparql-anything`)
- Python 3 (consigliato in `venv` del progetto)
- `sparql-anything-0.9.0.jar` nella root del progetto (o disponibile nel PATH)

1) Rigenerare il CSV pulito

Esegui lo script di equità per creare/aggiornare `bologna_KG_ready.csv`:

```bash
cd /Users/lauratonsi/METODI
source venv/bin/activate
python equita.py
```

2) Generare il TTL (grafo) a partire dal CSV con `sparql-anything`

Il file `trasforma_finale.sparql` è la query `CONSTRUCT` che legge `bologna_KG_ready.csv`.
Esegui:

```bash
cd /Users/lauratonsi/METODI
java -jar sparql-anything-0.9.0.jar -q trasforma_finale.sparql -l bologna_KG_ready.csv -f TURTLE > bologna_KG_definitivo.ttl
```

3) Validare/estrarre entità femminili (esempio)

Usa la query di controllo `female_entities.sparql` per estrarre un CSV con le persone di genere `Female`:

```bash
cd /Users/lauratonsi/METODI
java -jar sparql-anything-0.9.0.jar -q female_entities.sparql -l bologna_KG_definitivo.ttl -f CSV > female_entities.csv
```

4) Esportare le triple per LLM

Per preparare il grafo all'integrazione con modelli linguistici, esporta le triple in formato JSONL:

```bash
cd /Users/lauratonsi/METODI
source venv/bin/activate
python export_kg_for_llm.py
```

Produce: `triples_for_llm.jsonl` (formato compatto: uno per riga, {s: subject, p: predicate, o: object})

5) Arricchimento con occupazioni (opzionale)

Lo script `P106.py` usa `female_entities.sparql` su `bologna_KG_definitivo.ttl` e interroga Wikidata per P106 (professioni). Esempio:

```bash
cd /Users/lauratonsi/METODI
source venv/bin/activate
python P106.py
```

Note e suggerimenti
- Se il `sparql-anything` jar non è nella root, aggiornare il percorso nel comando Java.
- Se il TTL presenta artefatti testuali (es. inserimenti accidentali), rimuoverli prima della validazione.
- Non è necessario committare i file generati (`bologna_KG_ready.csv`, `*.ttl`) a meno che non vogliate storicizzarli nel repo.

Per problemi o ulteriori script di controllo, apri un issue o chiedi qui.
