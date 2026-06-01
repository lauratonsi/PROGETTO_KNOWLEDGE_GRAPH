# Gender Gap nella Toponomastica di Bologna — Knowledge Graph

Knowledge Graph RDF per analizzare il divario di genere nelle intitolazioni stradali di Bologna.
Su 1.960 strade censite, solo 66 (5,8%) sono dedicate a donne.

Sito del progetto: <https://lauratonsi.github.io/PROGETTO_KNOWLEDGE_GRAPH/>

---

## Prerequisiti

- Python 3.10+
- `openpyxl` (per `classifica_professioni.py` e `wikidata_fetch.py`)

```bash
pip install openpyxl
```

---

## Pipeline di costruzione del KG

### 1. Correzione e classificazione (`equita.py`)

Input: `bologna_entita_uniche_comma.csv` (classificazione LLM grezza)  
Output: `bologna_KG_ready.csv`

```bash
python equita.py
```

Applica sistematicamente le correzioni validate: declassa santi e nomi astratti femminili
a Toponimo, recupera artisti con soprannome erroneamente classificati, corregge tre donne
classificate Male (Artemisia Gentileschi, Properzia De Rossi, Bittisia Gozzadini).

---

### 2. Generazione del Knowledge Graph (`genera_ttl.py`)

Input: `bologna_KG_ready.csv`  
Output: `bologna_KG_corretto.ttl`

```bash
python genera_ttl.py
```

Scrive le triple Turtle direttamente usando solo la libreria standard Python
(`csv`, `hashlib`, `re`, `pathlib`). Replica la logica della query `trasforma_finale.sparql`
usata nella fase iniziale con SPARQL-Anything, eliminando la dipendenza da Java.

---

### 3. Arricchimento biografico via Wikidata (`wikidata_fetch.py`)

Input: `bologna_KG_corretto.ttl` (lista persone) + API Wikidata  
Output: `F_M DATE.xlsx`

```bash
python wikidata_fetch.py
```

Interroga `wbsearchentities` + `wbgetentities` per 1.129 persone recuperando
professione (P106), data/luogo di nascita (P569/P19), data/luogo di morte (P570/P20).
Copertura: 1.001 persone (88,7%).

---

### 4. Classificazione professionale (`classifica_professioni.py`)

Input: `F_M DATE.xlsx` (fogli UOMINI + DONNE) + `proposte_intitolazioni_future.csv`  
Output: `classificazione_professioni.csv`

```bash
python classifica_professioni.py
```

Assegna una macro-categoria occupazionale a ciascuna delle 1.191 persone classificate
tramite matching su parole chiave nelle professioni Wikidata.

---

### 5. Arricchimento topografico e semantico (`arricchimento_kg.py`)

Input: `bologna_KG_corretto.ttl` + `bologna_KG_ready.csv` +
`le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv` + `classificazione_professioni.csv`  
Output: `bologna_KG_corretto.ttl` (aggiornato in-place)

```bash
python arricchimento_kg.py
```

Aggiunge a `clv:Street`: `ex:quartiere`, `ex:geoPoint`, `ex:dataIstituzione`, `ex:tipologiaLuogo`.  
Aggiunge a `cpv:Person`: `ex:macroCategoriaOccupazionale`, `ex:datiAnagrafici`, `ex:professione` (completamento).  
Il TTL passa da ~18.363 a 27.251 righe (+4.545 triple di arricchimento).

---

## Script di utilità

| Script | Funzione |
|---|---|
| `normalizzazione_CSV.py` | Pulizia e normalizzazione dei CSV grezzi comunali |
| `pulizia.py` | Pre-processing del testo (nomi vie) |
| `cross_check.py` / `detailed_match.py` | Verifica incrociata classificazioni |
| `professioni_analisi.py` | Analisi statistica delle professioni |
| `generazione_grafici_analisi.py` | Genera i grafici per il sito |
| `run_queries.py` | Esegue query SPARQL sul KG localmente |
| `build_site.py` | Utility per il build del sito |
| `P106.py` | Prototipo iniziale: estrazione P106 via SPARQL-Anything (non nella pipeline finale) |

---

## File principali

| File | Descrizione |
|---|---|
| `bologna_entita_uniche_comma.csv` | Classificazione LLM grezza (input) |
| `bologna_KG_ready.csv` | CSV classificato e corretto (output di `equita.py`) |
| `bologna_KG_corretto.ttl` | Knowledge Graph finale (~27.000 righe, ~21.000 triple) |
| `F_M DATE.xlsx` | Dati biografici Wikidata per 1.129 persone |
| `classificazione_professioni.csv` | Macro-categorie occupazionali |
| `proposte_intitolazioni_future.csv` | 34 proposte di nuove intitolazioni |
| `proposte_KG.ttl` | Triple RDF per le proposte |
| `trasforma_finale.sparql` | Query CONSTRUCT originale (fase SPARQL-Anything) |
| `docs/schema.ttl` | Ontologia OWL in formato Turtle |

---

## Nota storica su SPARQL-Anything

La fase iniziale del progetto usava SPARQL-Anything (jar Java) con `trasforma_finale.sparql`
per convertire il CSV in Turtle. La pipeline è stata poi riscritta interamente in Python
(`genera_ttl.py`) per eliminare la dipendenza da Java, replicando la stessa logica CONSTRUCT.
