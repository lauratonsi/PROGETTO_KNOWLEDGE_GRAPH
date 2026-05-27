# Note Metodologiche — Classificazione di Genere delle Strade di Bologna

## Fonte dei dati

Il dataset utilizzato in questo progetto è stato scaricato dal portale open data del Comune di Bologna:
[https://opendata.comune.bologna.it/pages/home/](https://opendata.comune.bologna.it/pages/home/) 

L'analisi strutturale si basa sull'integrazione dell'elenco degli archi stradali con i riferimenti spaziali di origine e destinazione disponibili nel dataset dei Nodi stradali; l'unione di queste componenti consente la modellazione del grafo stradale integrale del Comune di Bologna in formato CSV ([Open Data Comune di Bologna - Archi Stradali](https://opendata.comune.bologna.it/explore/dataset/rifter_arcstra_li/information/)). Questo framework è stato successivamente confrontato e integrato con il dataset "Le aree verdi, piazze e vie di Bologna dedicate alle donne", anch'esso in formato CSV, che raccoglie la mappatura geografica dei toponimi femminili e le relative schede biografiche ([Open Data Comune di Bologna - Vie dedicate alle donne](https://opendata.comune.bologna.it/explore/dataset/le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne/information/?disjunctive.quartiere&disjunctive.tipologia&disjunctive.tipo&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJ0cmVlbWFwIiwiZnVuYyI6IkNPVU5UIiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWUsImNvbG9yIjoicmFuZ2UtY3VzdG9tIiwicG9zaXRpb24iOiJjZW50ZXIifV0sInhBeGlzIjoidGlwb2xvZ2lhIiwibWF4cG9pbnRzIjpudWxsLCJ0aW1lc2NhbGUiOiIiLCJzb3J0IjoiIiwic2VyaWVzQnJlYWtkb3duIjoiIiwic2VyaWVzQnJlYWtkb3duVGltZXNjYWxlIjoiIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJsZS1hcmVlLXZlcmRpLWUtbGUtdmllLWRpLWJvbG9nbmEtZGVkaWNhdGUtYWxsZS1kb25uZSIsIm9wdGlvbnMiOnsiZGlzanVuY3RpdmUucXVhcnRpZXJlIjp0cnVlLCJkaXNqdW5jdGl2ZS50aXBvbG9naWEiOnRydWUsImRpc2p1bmN0aXZlLnRpcG8iOnRydWV9fX1dLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlLCJ0aW1lc2NhbGUiOiIifQ%3D%3D)). 

Poiché lo stradario comunale di base non include nativamente una classificazione di genere — elemento invece fondamentale per quantificare e studiare il *gender gap* toponomastico all'interno dello spazio urbano —, il gruppo di ricerca ha provveduto a una categorizzazione sistematica di ciascuna intitolazione. Questa operazione di arricchimento semantico è stata condotta attraverso l'ausilio di modelli linguistici avanzati (DeepSeek, Gemini, ChatGPT e Claude). Tutte le attribuzioni finali e le scelte tassonomiche descritte nel presente documento costituiscono decisioni metodologiche assunte e validate sotto l'esclusiva responsabilità del gruppo di ricerca. 
--- 
## Quadro Normativo e Vincoli — Regolamento Toponomastico
L'attività di proposta di nuove intitolazioni è subordinata al rispetto della normativa vigente. Il principale vincolo normativo è stabilito dalla **Legge 23 giugno 1927, n. 1188**, la quale prescrive che la denominazione di aree pubbliche o monumenti a persone deve avvenire **solo dopo il decorso di almeno dieci anni dal decesso** della persona in questione.
- Deroghe: Il Regolamento Toponomastico del Comune di Bologna prevede la possibilità di richiedere deroghe a tale limite temporale per personalità di comprovata rilevanza storica e culturale, previa autorizzazione prefettizia.
- Procedure: Ai sensi dell'art. 12 del Regolamento Toponomastico, le proposte possono essere avanzate da consessi istituzionali (Consigli di Quartiere, Consiglio Comunale) o da gruppi di cittadini (minimo 20 firmatari). Ogni proposta deve essere corredata da una relazione illustrativa che ne giustifichi il merito, supportata da documentazione biografica.
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
