# Note Metodologiche — Classificazione di Genere delle Strade di Bologna

## Fonte dei dati

Il dataset utilizzato in questo progetto è stato scaricato dal portale open data del Comune di Bologna:
[https://opendata.comune.bologna.it/pages/home/](https://opendata.comune.bologna.it/pages/home/) 

L'analisi strutturale si basa sull'integrazione dell'elenco degli archi stradali con i riferimenti spaziali di origine e destinazione disponibili nel dataset dei Nodi stradali; l'unione di queste componenti consente la modellazione del grafo stradale integrale del Comune di Bologna in formato CSV ([Open Data Comune di Bologna - Archi Stradali](https://opendata.comune.bologna.it/explore/dataset/rifter_arcstra_li/information/)). Questo framework è stato successivamente confrontato e integrato con il dataset "Le aree verdi, piazze e vie di Bologna dedicate alle donne", anch'esso in formato CSV, che raccoglie la mappatura geografica dei toponimi femminili e le relative schede biografiche ([Open Data Comune di Bologna - Vie dedicate alle donne](https://opendata.comune.bologna.it/explore/dataset/le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne/information/?disjunctive.quartiere&disjunctive.tipologia&disjunctive.tipo&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJ0cmVlbWFwIiwiZnVuYyI6IkNPVU5UIiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWUsImNvbG9yIjoicmFuZ2UtY3VzdG9tIiwicG9zaXRpb24iOiJjZW50ZXIifV0sInhBeGlzIjoidGlwb2xvZ2lhIiwibWF4cG9pbnRzIjpudWxsLCJ0aW1lc2NhbGUiOiIiLCJzb3J0IjoiIiwic2VyaWVzQnJlYWtkb3duIjoiIiwic2VyaWVzQnJlYWtkb3duVGltZXNjYWxlIjoiIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJsZS1hcmVlLXZlcmRpLWUtbGUtdmllLWRpLWJvbG9nbmEtZGVkaWNhdGUtYWxsZS1kb25uZSIsIm9wdGlvbnMiOnsiZGlzanVuY3RpdmUucXVhcnRpZXJlIjp0cnVlLCJkaXNqdW5jdGl2ZS50aXBvbG9naWEiOnRydWUsImRpc2p1bmN0aXZlLnRpcG8iOnRydWV9fX1dLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlLCJ0aW1lc2NhbGUiOiIifQ%3D%3D)). 

Poiché lo stradario comunale di base non include nativamente una classificazione di genere — elemento invece fondamentale per quantificare e studiare il *gender gap* toponomastico all'interno dello spazio urbano —, il gruppo di ricerca ha provveduto a una categorizzazione sistematica di ciascuna intitolazione. Questa operazione di arricchimento semantico è stata condotta attraverso l'ausilio di modelli linguistici avanzati (DeepSeek, Gemini, ChatGPT e Claude). Tutte le attribuzioni finali e le scelte tassonomiche descritte nel presente documento costituiscono decisioni metodologiche assunte e validate sotto l'esclusiva responsabilità del gruppo di ricerca.

---

## Arricchimento biografico tramite Wikidata

Per le 1.129 persone identificate nel Knowledge Graph (strade intitolate a persone di genere **Male** o **Female**), i dati biografici — professione/occupazione, data e luogo di nascita, data e luogo di morte — sono stati recuperati automaticamente tramite l'**API JSON di Wikidata** ([https://www.wikidata.org/w/api.php](https://www.wikidata.org/w/api.php)), utilizzando le seguenti proprietà:

| Proprietà | Significato |
|-----------|-------------|
| P31 + Q5  | Istanza di essere umano (usata per disambiguare da omonimi non-persona) |
| P106      | Occupazione / professione |
| P569 / P19 | Data e luogo di nascita |
| P570 / P20 | Data e luogo di morte |

La ricerca è avvenuta in due fasi: prima una ricerca testuale (`wbsearchentities`) sul nome normalizzato della strada, poi il recupero strutturato delle proprietà (`wbgetentities`) sull'entità candidata, con verifica obbligatoria che l'entità fosse classificata come essere umano (P31 = Q5).

Per le circa 15 figure di rilevanza esclusivamente locale non documentate su Wikidata (tra cui Vittorio Sabena, Don Giuseppe Nozzi, Giorgio Neri, Carlo Pelagalli, Alfio Pappalardo), i dati biografici sono stati integrati tramite ricerca nelle seguenti fonti archivistiche e locali:

- **Storia e Memoria di Bologna** – Comune di Bologna ([storiaememoriadibologna.it](https://www.storiaememoriadibologna.it))
- **ANPI Bologna** – Archivio partigiani ([anpi.it](https://www.anpi.it))
- **Archivio di Stato di Bologna** ([archiviodistatobologna.it](https://archiviodistatobologna.it))
- Segnalazioni dirette e documentazione fornita dal gruppo di ricerca del corso *Metodologie e Tecniche di Simulazione*

### Copertura dell'arricchimento biografico

Su **1.129 persone** presenti nel Knowledge Graph (strade intitolate a individui di genere Male o Female), **943 (83,5%)** sono state arricchite con le proprietà `ex:professione`, `ex:dataNascita`, `ex:luogoNascita`, `ex:dataMorte`, `ex:luogoMorte`. Le restanti **128 (11,3%)** non dispongono di dati biografici per le seguenti ragioni strutturali:

- **Nome abbreviato nello stradario**: il TTL contiene il solo cognome o soprannome (es. `CAVOUR`, `DANTE`, `TINTORETTO`, `ROSSINI`) che non è stato possibile collegare automaticamente al nome completo nel foglio dati.
- **Assenza di dati di partenza**: figure locali minori per cui né Wikidata né le fonti archivistiche consultate hanno restituito risultati.
- **Collettivi e coppie**: intitolazioni a gruppi storici (es. `AMBROGIO E PIETRO LORENZETTI`, `FRATELLI CERVI`) che non corrispondono a singoli individui nel dataset biografico.

Questa limitazione è documentata a fini di trasparenza metodologica e non inficia la validità dell'analisi complessiva, che si basa sull'83,5% della popolazione censita.

--- 
## Quadro Normativo e Vincoli — Regolamento Toponomastico
L'attività di proposta di nuove intitolazioni è subordinata al rispetto della normativa vigente. Il principale vincolo normativo è stabilito dalla **Legge 23 giugno 1927, n. 1188**, la quale prescrive che la denominazione di aree pubbliche o monumenti a persone deve avvenire **solo dopo il decorso di almeno dieci anni dal decesso** della persona in questione.
- **Deroghe**: Il Regolamento Toponomastico del Comune di Bologna prevede la possibilità di richiedere deroghe a tale limite temporale per personalità di comprovata rilevanza storica e culturale, previa autorizzazione prefettizia.
- **Procedure**: Ai sensi dell'art. 12 del Regolamento Toponomastico, le proposte possono essere avanzate da consessi istituzionali (Consigli di Quartiere, Consiglio Comunale) o da gruppi di cittadini (minimo 20 firmatari). Ogni proposta deve essere corredata da una relazione illustrativa che ne giustifichi il merito, supportata da documentazione biografica.
Questa analisi, unita alla documentazione sul gender gap qui prodotta, costituisce la base conoscitiva necessaria per avanzare proposte formali di intitolazione volte al riequilibrio della toponomastica cittadina.
---

## Le tre categorie

- **Male**: la strada è intitolata a una persona di genere maschile, o a un gruppo composto esclusivamente da uomini, o a un collettivo denominato con sostantivo maschile.
- **Female**: la strada è intitolata a una persona di genere femminile.
- **Toponimo**: la strada è intitolata a un luogo, un concetto, un'istituzione, un evento storico, un mestiere, o un nome di famiglia senza riferimento a un individuo specifico identificabile.

---

## Criteri di classificazione

### Nomi di santi e luoghi sacri → Toponimo
I nomi di santi (es. *Santa Maria*, *San Lorenzo*, *Sant'Anna*) sono classificati come **Toponimo** perché nella toponomastica bolognese si riferiscono per lo più a chiese, piazze o quartieri storici, non all'individuo religioso in quanto tale.

### Nomi d'artista o soprannomi storici → Male/Female
Quando una strada è intitolata a un personaggio noto con un solo nome o soprannome (es. *Dante*, *Donatello*, *Caravaggio*, *Giambologna*, *Tintoretto*), si è identificato il referente storico e classificata la strada di conseguenza.

### Nomi di famiglia → Toponimo
I cognomi che si riferiscono a intere famiglie nobili o borghesi bolognesi (es. *Achillini*, *Agucchi*, *Barbazzi*, *Bianchetti*, *Bolognetti*, *Cattani*, *Carracci*, *Bibiena*) sono classificati come **Toponimo**, poiché non è possibile identificare un singolo individuo di riferimento.

### Strade "Fratelli..." → Male
Le strade intitolate a fratelli (es. *Fratelli Cervi*, *Fratelli Rosselli*, *Fratelli Dandolo*) sono classificate come **Male**. Il termine "fratelli" è maschile e i referenti storici identificati sono tutti uomini.

### Collettivi con sostantivo maschile → Male
I collettivi denominati con un sostantivo maschile (es. *Ragazzi del '99*) sono classificati come **Male**, in accordo con la grammatica italiana che usa il maschile plurale come genere non marcato anche per gruppi misti.

---

## Casi particolari e note critiche

### Passaggio Fratelli Marincola — classificato Male
Il Passaggio Fratelli Marincola è intitolato a Giorgio e Isabella Marincola: un fratello e una sorella, entrambi partigiani. Isabella Marincola era una donna. Tuttavia, l'intitolazione usa il termine **"Fratelli"** (maschile plurale), che nella lingua italiana cancella la presenza femminile. La scelta di classificare questa strada come **Male** riflette la denominazione ufficiale, ma si vuole qui segnalare esplicitamente che questa scelta oscura il contributo di Isabella Marincola come donna partigiana. Questo è un esempio concreto di come il genere grammaticale maschile della lingua italiana renda invisibile la presenza femminile nella storia.

### Ragazzi del '99 — classificato Male
L'espressione "Ragazzi del '99" si riferisce ai giovani nati nel 1899, chiamati alle armi nel 1917 durante la Prima Guerra Mondiale. Anche in questo caso il collettivo è maschile, sebbene nella realtà storica il contributo femminile alla guerra (crocerossine, operaie, staffette) fosse significativo ma non riconosciuto nell'intitolazione.

### Nomi classificati erroneamente per via del genere grammaticale
Alcuni nomi propri femminili (es. *Vittoria*, *Serena*, *Letizia*, *Valeria*) si riferiscono in realtà a concetti astratti, eventi o luoghi e sono stati classificati come **Toponimo**. Analogamente, alcuni nomi maschili (es. *Spirito Santo*, *Santo Stefano*, *Vittorio Veneto*, *Massa Carrara*) si riferiscono a luoghi o concetti e sono stati anch'essi corretti a **Toponimo**.

---

## Persone transgender e non binarie

### Assenza di strade dedicate a persone non binarie
Nel dataset non sono state identificate strade esplicitamente dedicate a persone non binarie. Questo non sorprende: la toponomastica bolognese riflette principalmente figure del XIX e XX secolo, un'epoca in cui l'identità non binaria non era riconosciuta né documentata pubblicamente. Questa assenza è comunque una limitazione strutturale del sistema di classificazione adottato, che è binario per costruzione e non prevede categorie alternative.

### Caso concreto: Piazzale Marcella Di Folco — classificato Female
Il **Piazzale Marcella Di Folco** è intitolato a Marcella Di Folco (1943–2010), nata con un nome maschile, vissuta come donna a partire dagli anni '70 e tra le più importanti attiviste per i diritti transgender in Italia.

Il gruppo di ricerca ha scelto di classificare questa strada come **Female**, in accordo con l'identità di genere della persona onorata. Questa scelta riflette il principio che la classificazione debba rispettare l'identità autodichiarata, non il genere anagrafico alla nascita. È una posizione etica esplicita del gruppo, in assenza di qualsiasi indicazione ufficiale esterna.

---

## Riflessione sul metodo

L'analisi del gender gap nella toponomastica è inevitabilmente condizionata dalle convenzioni linguistiche e storiche della lingua italiana, che utilizza il maschile come genere non marcato. Questo significa che alcune strade intitolate a gruppi misti o a concetti inclusivi di donne vengono comunque contate come **Male** per via della denominazione ufficiale. Il caso del Passaggio Fratelli Marincola è emblematico: una sorella partigiana è resa invisibile dal sostantivo "fratelli". Questa nota vuole esplicitare tali limiti, affinché i risultati del progetto siano interpretati tenendo conto del contesto linguistico e culturale in cui la toponomastica è stata prodotta.

---

---

## Decisioni ontologiche e conformità agli standard Ontopia (giugno 2026)

### 1. Conformità CLV-AP_IT v1.0

Il Knowledge Graph usa i nomi di classe e proprietà ufficiali di CLV-AP_IT v1.0, verificati direttamente su [schema.gov.it/lodview/onto/CLV](https://schema.gov.it/lodview/onto/CLV) il 4 giugno 2026:

| Termine usato nel KG | Alternativa scartata | Motivo |
|---|---|---|
| `clv:StreetToponym` | `clv:Street` | `clv:Street` non esiste in CLV-AP_IT: un tool RDF che dereferenzia `https://w3id.org/italia/onto/CLV/Street` riceve HTTP 404 |
| `clv:officialStreetName` | `clv:hasStreetName` | `clv:hasStreetName` non esiste in CLV-AP_IT |
| `ex:isDedicatedTo` | `clv:isDedicatedTo` | CLV-AP_IT non definisce alcuna proprietà per la relazione persona-luogo; la "dedicazione" è un concetto specifico di questo progetto e appartiene al namespace custom `ex:` |

La proprietà `ex:isDedicatedTo` è dichiarata nel namespace `ex: <https://w3id.org/bologna/ontology#>`, comune a tutte le proprietà custom del progetto.

### 2. cpv:hasSex invece di cpv:hasGender

CPV v0.8 (marzo 2023) ha introdotto due proprietà distinte:
- `cpv:hasSex` — sesso biologico, collegato al vocabolario controllato `classifications-for-people/sex` (valori: `sex/M`, `sex/F`)
- `cpv:hasGender` — identità di genere socio-culturale, introdotta per distinguere il genere dal sesso biologico

Il progetto usa `cpv:hasSex` e non `cpv:hasGender` per la seguente ragione tecnica: il vocabolario controllato corrispondente per `cpv:hasGender` (`https://w3id.org/italia/controlled-vocabulary/classifications-for-people/gender`) **non è ancora pubblicato** da Ontopia — la risorsa restituisce HTTP 404 (verificato il 4 giugno 2026). Usare `cpv:hasGender` senza un vocabolario a cui puntare renderebbe il KG non dereferenziabile come Linked Open Data.

Il vocabolario per `cpv:hasSex` è invece pienamente disponibile e stabile. Questa scelta sarà rivista quando Ontopia pubblicherà il vocabolario gender.

### 3. ex:macroCategoriaOccupazionale — tassonomia custom Bologna

Ontopia/schema.gov.it **non fornisce classificazioni per professioni o occupazioni**. Verifica effettuata il 4 giugno 2026:

- **CPV** (Core Person Vocabulary) — 23 object property, 16 data property: modella nome, data di nascita/morte, sesso, titolo, livello di istruzione, residenza, parentela. Nessuna proprietà relativa a professione, occupazione o ruolo lavorativo.
- **RO** (Roles Ontology) — modella `Role` e `TimeIndexedRole` in modo astratto. Nessuna specializzazione occupazionale.
- **VocabolariControllati/classifications-for-people** — contiene: education-level, marital-status, parental-relationship, person-title, registry-office types, sex. Nessuna classificazione delle professioni.

L'unica classificazione italiana autorevole per le professioni è la **CP 2011 ISTAT** (adattamento italiano di ISCO-08), progettata però per occupazioni contemporanee e inapplicabile a figure storiche come "Patriota risorgimentale", "Pittrice fiamminga del '600" o "Compositore barocco". Queste categorie non esistono nell'ISCO-08.

La proprietà `ex:macroCategoriaOccupazionale` è quindi una **tassonomia Bologna-specifica non standard**, dichiarata esplicitamente come tale nel namespace custom `ex:` e documentata nel `rdfs:comment` di `docs/schema.ttl`. I 13 valori adottati sono stati definiti dal gruppo di ricerca per l'analisi storico-culturale del gender gap nella toponomastica: `Arte visiva e architettura` · `Filosofia, storia e accademia` · `Istruzione ed educazione` · `Letteratura e giornalismo` · `Musica, teatro e cinema` · `Patrioti, militari ed esploratori` · `Politica e diritto` · `Religione` · `Resistenza e antifascismo` · `Scienze e medicina` · `Sindacalismo e attivismo civile` · `Sport` · `Altro / istituzionale`.

---

## Arricchimento topografico e semantico del Knowledge Graph (maggio 2026)

In una seconda fase di arricchimento, il Knowledge Graph è stato esteso con nuove proprietà estratte da due ulteriori dataset open data del Comune di Bologna e dal file di classificazione professionale prodotto internamente al progetto.

### Fonti aggiuntive

| Dataset | Proprietà aggiunte |
|---|---|
| **bologna_KG_ready.csv** (stradario classificato) | `ex:quartiere`, `ex:geoPoint`, `ex:dataIstituzione` |
| **le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv** | `ex:tipologiaLuogo`, `ex:datiAnagrafici`, `ex:professione` (colmatura) |
| **classificazione_professioni.csv** (prodotto internamente) | `ex:macroCategoriaOccupazionale` |

### Nuove proprietà su `clv:StreetToponym`

- **`ex:quartiere`** — nome del quartiere bolognese in cui ricade la strada (es. `"Savena"`, `"Porto - Saragozza"`). Presente per tutte le 1.131 strade Male e Female.
- **`ex:geoPoint`** — coordinate WGS84 del centroide della strada, formato `"lat, lon"` (es. `"44.483592003952296, 11.367738980601088"`). Abilita query e visualizzazioni geospaziali.
- **`ex:dataIstituzione`** — data di istituzione ufficiale dell'intitolazione in formato ISO 8601 (es. `"1991-10-21"`). Permette analisi storiche sull'evoluzione temporale delle intitolazioni.
- **`ex:tipologiaLuogo`** — tipo di luogo toponomastico (`"Via"`, `"Largo"`, `"Piazza"`, `"Passaggio"`, `"Rotonda"`, `"Parco"`, `"Giardino"`, ecc.). Estratto solo per i luoghi presenti nel dataset "Aree verdi e vie dedicate alle donne" (59 match su 66 luoghi femminili).

### Nuove proprietà su `cpv:Person`

- **`ex:macroCategoriaOccupazionale`** — categoria semantica della professione, assegnata tramite matching su parole chiave sul campo `ex:professione`. Valori possibili: `"Arte visiva e architettura"`, `"Scienze e medicina"`, `"Politica e diritto"`, `"Musica, teatro e cinema"`, `"Letteratura e giornalismo"`, `"Filosofia, storia e accademia"`, `"Patrioti, militari ed esploratori"`, `"Religione"`, `"Altro / istituzionale"`. Aggiunto a 1.030 persone.
- **`ex:datiAnagrafici`** — stringa sintetica con luogo e anno di nascita e di morte (es. `"Bologna, 1711 - Parigi, 1782"`). Estratto dal campo `DATI ANAGRAFICI` del dataset "Aree verdi e vie dedicate alle donne". Presente solo per le persone di genere Female con un match nel dataset (59 persone).
- **`ex:professione`** (colmatura) — per 3 persone di genere Female non documentate su Wikidata e quindi prive di `ex:professione` nella fase di arricchimento biografico, il campo è stato colmato con il valore `CLASSIFICAZIONE` del dataset "Aree verdi e vie dedicate alle donne".

### Script e riproducibilità

L'arricchimento è stato eseguito dallo script `arricchimento_kg.py` (Python 3, nessuna dipendenza esterna). Il file `bologna_KG_corretto.ttl` viene aggiornato in modo additivo: le nuove triple vengono aggiunte in coda al file senza modificare il contenuto preesistente. Il formato Turtle permette la presenza di blocchi multipli per lo stesso soggetto, che vengono uniti da qualunque parser RDF conforme alla specifica.

---

## Proposte di intitolazione

### Criteri di ammissibilità

Le proposte raccolte rispettano il quadro normativo italiano in materia di toponomastica urbana. Il **D.P.R. 223/1989** e le prassi consolidate del Comune di Bologna prevedono che una strada possa essere intitolata a una persona fisica soltanto se questa è deceduta da almeno **dieci anni**. Le proposte sono quindi distinte in due categorie:

- **Attive**: la persona è deceduta da più di dieci anni; la candidatura è immediatamente proponibile al Consiglio Comunale.
- **Future**: la persona è deceduta da meno di dieci anni, è ancora in vita, oppure la data di morte è incerta. La proposta viene registrata per essere ripresa nel momento in cui i requisiti temporali saranno soddisfatti.

### Criteri di selezione

Il gruppo di ricerca del corso *Metodologie e Tecniche di Simulazione* ha selezionato le candidate privilegiando:

- **Donne, persone trans e non binarie** con un contributo significativo documentato
- **Legame diretto con Bologna** (nate, vissute, morte o attive nella città) come criterio preferenziale
- In assenza di legame diretto, **rilevanza storica nazionale** nel campo della scienza, della politica, della Resistenza, dell'arte o dei diritti civili
- **Assenza di intitolazioni equivalenti** già esistenti a Bologna (si segnala nei *punti chiave* quando una figura ha già un parco, un giardino o un passaggio, ma non una via o piazza di rilievo)

### Fonti consultate

Le schede biografiche delle 34 candidature sono state costruite incrociando le seguenti fonti:

**Partigiane e Resistenza**
- ANPI – Associazione Nazionale Partigiani d'Italia ([anpi.it](https://www.anpi.it))
- Resistenzapp ([resistenzapp.it](https://www.resistenzapp.it))
- Resistenza Mappe ([resistenzamappe.it](https://resistenzamappe.it))

**Accademiche, scienziate e professioniste**
- Scienze a 2 Voci – Università di Bologna ([scienzaa2voci.unibo.it](https://scienzaa2voci.unibo.it))
- Enciclopedia delle Donne ([enciclopediadelledonne.it](https://www.enciclopediadelledonne.it))
- Università di Bologna – Alumni e personaggi celebri ([unibo.it](https://www.unibo.it))

**Figure storiche bolognesi**
- Storia e Memoria di Bologna – Comune di Bologna ([storiaememoriadibologna.it](https://www.storiaememoriadibologna.it))
- Archivio di Stato di Bologna ([archiviodistatobologna.it](https://archiviodistatobologna.it))
- Festival del Medioevo ([festivaldelmedioevo.it](https://festivaldelmedioevo.it))
- Cantiere Bologna ([cantierebologna.com](https://cantierebologna.com))

**Figure nazionali e internazionali**
- Treccani – Dizionario Biografico degli Italiani ([treccani.it](https://www.treccani.it))
- Wikipedia (edizioni italiana e inglese)
- ANPI ([anpi.it](https://www.anpi.it))

**Attivismo LGBTQ+ e diritti civili**
- Storie in Movimento ([storieinmovimento.org](https://storieinmovimento.org))
- Associazione Luki Massa ([associazionelukimassa.org](https://associazionelukimassa.org))

**Sport**
- FIDAL – Federazione Italiana di Atletica Leggera
- Wikipedia (edizione inglese)
