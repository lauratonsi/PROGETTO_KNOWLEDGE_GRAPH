from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import subprocess
import io
import time

# Eseguiamo la query SPARQL sul grafo locale per ottenere i nomi delle entità female
command = [
    "java", "-jar", "sparql-anything-0.9.0.jar",
    "-q", "female_entities.sparql",
    "-l", "bologna_KG_definitivo.ttl",
    "-f", "CSV"
]

result = subprocess.run(command, capture_output=True, text=True, cwd="/Users/lauratonsi/METODI")

if result.returncode != 0:
    print("Errore nell'esecuzione della query SPARQL:", result.stderr)
    exit(1)

# Leggiamo il CSV dall'output
csv_data = io.StringIO(result.stdout)
df_female = pd.read_csv(csv_data)

# Estraiamo la lista dei nomi
names = df_female['name'].tolist()

# Inizializziamo l'endpoint di Wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
time.sleep(1)  # Piccola pausa per evitare di sovraccaricare l'endpoint
results_list = []

for name in names:
    # Normalizziamo il nome a title case per migliorare le corrispondenze
    name_normalized = name.title()
    
    # Questa query cerca l'entità (persona) con il nome specificato e recupera la sua professione (P106)
    # L'uso di rdfs:label con il tag @it garantisce che cerchiamo le stringhe italiane
    query = f"""
    SELECT ?person ?personLabel ?occupation ?occupationLabel WHERE {{
      ?person wdt:P31 wd:Q5; # Deve essere un'istanza (P31) di "essere umano" (Q5)
              wdt:P106 ?occupation. # Estrarre l'occupazione
      ?person rdfs:label ?personLabel .
      FILTER(regex(str(?personLabel), "{name_normalized}", "i")) .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,en". }}
    }}
    LIMIT 5
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        
        if not bindings:
            # Se Wikidata non trova una corrispondenza esatta
            results_list.append({"Nome": name, "Wikidata_URI": "Non trovato", "Professione": "N/D"})
        else:
            for result in bindings:
                results_list.append({
                    "Nome": name,
                    "Wikidata_URI": result["person"]["value"],
                    "Professione": result["occupationLabel"]["value"]
                })
    except Exception as e:
        print(f"Errore interrogando {name}: {e}")

# Mettiamo i risultati in un DataFrame per leggerli meglio
df = pd.DataFrame(results_list)
print(df)