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

Applica le correzioni di classificazione validate: declassa santi e nomi astratti femminili
a Toponimo, recupera artisti con soprannome (DANTE, CARAVAGGIO…) erroneamente classificati
come Toponimo, corregge tre donne classificate Male (Artemisia Gentileschi, Properzia De Rossi,
Bittisia Gozzadini).

---

### 2. Generazione del Knowledge Graph (`genera_ttl.py`)

Input: `bologna_KG_ready.csv`  
Output: `bologna_KG_corretto.ttl`

```bash
python genera_ttl.py
```

Genera le triple Turtle base con sola libreria standard Python (`csv`, `hashlib`, `re`):
`clv:StreetToponym`, `clv:officialStreetName`, `ex:isDedicatedTo`, `cpv:Person`, `cpv:fullName`,
`cpv:hasSex`. Output: 1.132 strade (1.066 Male, 66 Female) e 1.129 persone uniche.

---

### 3a. Recupero dati biografici da Wikidata (`wikidata_fetch.py`)

Input: `bologna_KG_ready.csv` + API Wikidata  
Output: `F_M DATE.xlsx`

```bash
python wikidata_fetch.py
```

Interroga `wbsearchentities` + `wbgetentities` per 1.129 persone recuperando
professione (P106), data/luogo di nascita (P569/P19), data/luogo di morte (P570/P20),
con verifica umano (P31 = Q5). Copertura: 943 persone (83,5%). I non trovati sono
in `wikidata_notfound.txt`.

---

### 3b. Integrazione dati biografici nel KG (`bio_ttl.py`)

Input: `F_M DATE.xlsx` + `bologna_KG_ready.csv`  
Output: `bologna_KG_corretto.ttl` (aggiornato in-place)

```bash
python bio_ttl.py
```

Legge i dati biografici da `F_M DATE.xlsx` e aggiunge al TTL le triple
`ex:professione`, `ex:dataNascita`, `ex:luogoNascita`, `ex:dataMorte`, `ex:luogoMorte`
per ciascuna persona corrispondente nel KG.

---

### 4. Classificazione professionale (`classifica_professioni.py`)

Input: `F_M DATE.xlsx` (fogli UOMINI + DONNE) + `proposte_intitolazioni_future.csv`  
Output: `classificazione_professioni.csv`

```bash
python classifica_professioni.py
```

Assegna una delle 13 macro-categorie occupazionali a ciascuna delle 1.163 persone
classificate (1.063 uomini storici + 66 donne storiche + 34 proposte) tramite matching
su parole chiave nelle professioni Wikidata.

---

### 5. Arricchimento topografico e semantico (`arricchimento_kg.py`)

Input: `bologna_KG_corretto.ttl` + `bologna_KG_ready.csv` +
`le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv` + `classificazione_professioni.csv`  
Output: `bologna_KG_corretto.ttl` (aggiornato in-place)

```bash
python arricchimento_kg.py
```

Aggiunge a `clv:StreetToponym`: `ex:quartiere`, `ex:geoPoint`, `ex:dataIstituzione`,
`ex:tipologiaLuogo` (60 strade femminili dal dataset aree verdi).  
Aggiunge a `cpv:Person`: `ex:macroCategoriaOccupazionale` (1.030 persone),
`ex:datiAnagrafici` (60 donne), `ex:professione` (completamento per 8 donne
non presenti su Wikidata).  
Il TTL risultante conta 26.651 righe e 15.885 triple RDF.

---

## Script di utilità

| Script | Funzione |
|---|---|
| `normalizzazione_CSV.py` | Pulizia e normalizzazione dei CSV grezzi comunali |
| `pulizia.py` | Pre-processing del testo (nomi vie) |
| `cross_check.py` / `detailed_match.py` | Verifica incrociata classificazioni |
| `run_queries.py` | Esegue query SPARQL sul KG localmente |
| `build_site.py` | Utility per il build del sito |
| `bio_ttl.py` | Step 3b della pipeline: integra i dati F_M DATE.xlsx nel TTL come triple biografiche |
| `P106.py` | Prototipo iniziale: estrazione P106 via SPARQL-Anything (non nella pipeline finale) |

---

## File principali

| File | Descrizione |
|---|---|
| `bologna_entita_uniche_comma.csv` | Classificazione LLM grezza (input) |
| `bologna_KG_ready.csv` | CSV classificato e corretto (output di `equita.py`) |
| `bologna_KG_corretto.ttl` | Knowledge Graph finale (26.651 righe, 15.885 triple) |
| `F_M DATE.xlsx` | Dati biografici Wikidata per 1.129 persone |
| `classificazione_professioni.csv` | Macro-categorie occupazionali |
| `proposte_intitolazioni_future.csv` | 34 proposte di nuove intitolazioni |
| `proposte_KG.ttl` | Triple RDF per le proposte |
| `trasforma_finale.sparql` | Query CONSTRUCT originale (fase SPARQL-Anything) |
| `docs/schema.ttl` | Ontologia OWL in formato Turtle |

---

## Usare il Knowledge Graph

Il file `bologna_KG_corretto.ttl` è un grafo RDF in formato Turtle (15.885 triple) interrogabile con qualsiasi strumento SPARQL.

### Caricare il grafo

**Apache Jena (da riga di comando):**
```bash
# Installare Jena: https://jena.apache.org/download/
sparql --data bologna_KG_corretto.ttl --query la_tua_query.sparql
```

**GraphDB (interfaccia grafica):**
1. Creare un nuovo repository in GraphDB Free
2. Import → Upload RDF files → selezionare `bologna_KG_corretto.ttl`
3. Eseguire le query dall'interfaccia SPARQL Workbench

**Python (con rdflib):**
```bash
pip install rdflib
```
```python
from rdflib import Graph
g = Graph()
g.parse("bologna_KG_corretto.ttl", format="turtle")
results = g.query("SELECT ?via WHERE { ?via a <https://w3id.org/italia/onto/CLV/StreetToponym> } LIMIT 10")
for row in results:
    print(row)
```

### Prefissi principali

```sparql
PREFIX clv: <https://w3id.org/italia/onto/CLV/>       # strade (classe: clv:StreetToponym)
PREFIX cpv: <https://w3id.org/italia/onto/CPV/>       # persone (classe: cpv:Person)
PREFIX ex:  <https://w3id.org/bologna/ontology#>      # proprietà custom Bologna
```

### Query di esempio

**Contare le strade per genere:**
```sparql
PREFIX clv: <https://w3id.org/italia/onto/CLV/>
PREFIX cpv: <https://w3id.org/italia/onto/CPV/>

SELECT ?genere (COUNT(DISTINCT ?via) AS ?numero_strade)
WHERE {
  ?via a clv:StreetToponym ;
       ex:isDedicatedTo ?persona .
  ?persona cpv:hasSex ?genere .
}
GROUP BY ?genere
```

**Strade dedicate a donne con professione e quartiere:**
```sparql
PREFIX clv: <https://w3id.org/italia/onto/CLV/>
PREFIX cpv: <https://w3id.org/italia/onto/CPV/>
PREFIX ex:  <https://w3id.org/bologna/ontology#>

SELECT DISTINCT ?nomeVia ?nomePersona ?professione ?quartiere
WHERE {
  ?via a clv:StreetToponym ;
       clv:officialStreetName ?nomeVia ;
       ex:isDedicatedTo ?persona .
  OPTIONAL { ?via ex:quartiere ?quartiere }
  ?persona cpv:hasSex <https://w3id.org/italia/controlled-vocabulary/classifications-for-people/sex/F> ;
           cpv:fullName ?nomePersona .
  OPTIONAL { ?persona ex:professione ?professione }
}
ORDER BY ?nomeVia
```

Tutte le query documentate nel progetto sono disponibili nella pagina [Query SPARQL](https://lauratonsi.github.io/PROGETTO_KNOWLEDGE_GRAPH/sparql.html) del sito.

---

## Nota storica su SPARQL-Anything

La fase iniziale del progetto usava SPARQL-Anything (jar Java) con `trasforma_finale.sparql`
per convertire il CSV in Turtle. La pipeline è stata poi riscritta interamente in Python
(`genera_ttl.py`) per eliminare la dipendenza da Java, replicando la stessa logica CONSTRUCT.
