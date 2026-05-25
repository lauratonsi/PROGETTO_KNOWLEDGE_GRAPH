# Note Metodologiche — Classificazione di Genere delle Strade di Bologna

## Fonte dei dati

Il dataset utilizzato in questo progetto è stato scaricato dal portale open data del Comune di Bologna:
[https://opendata.comune.bologna.it/pages/home/](https://opendata.comune.bologna.it/pages/home/)

Il dataset contiene l'elenco delle strade del territorio comunale, ma non include alcuna classificazione di genere. Al fine di studiare il gender gap nella toponomastica bolognese, il gruppo di ricerca ha eseguito una classificazione di genere di ciascuna intitolazione stradale, utilizzando modelli linguistici (DeepSeek, Gemini, ChatGPT e Claude). Le scelte classificatorie descritte in questo documento sono decisioni del gruppo di ricerca.

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
