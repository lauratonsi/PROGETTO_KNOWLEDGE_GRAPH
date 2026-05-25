import csv

file_input = 'bologna_master_definitivo.csv'
file_output = 'bologna_entita_uniche.csv'

# Gli ultimi 5 irriducibili
ultimi_fantasmi = [
    "QUATTRO NOVEMBRE", "OTTO COLONNE", "DUE PORTONI", 
    "CROCE DI CAMALDOLI", "CA' ROSA"
]

nomi_visti = set()

try:
    with open(file_input, mode='r', encoding='utf-8') as fin, \
         open(file_output, mode='w', encoding='utf-8', newline='') as fout:
        
        reader = csv.DictReader(fin, delimiter=';')
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, delimiter=';')
        writer.writeheader()

        corretti_fantasmi = 0
        rimossi_duplicati = 0

        for row in reader:
            nome = str(row['NOME_PULITO']).strip().upper()
            
            # 1. Eliminiamo l'ultimo 0.12% di errore
            if nome in ultimi_fantasmi and row['GENERE'] == 'Male':
                row['GENERE'] = 'Toponimo'
                corretti_fantasmi += 1

            # 2. Il filtro intelligente (Deduplicazione)
            # Se non abbiamo mai visto questo nome, lo salviamo. Altrimenti, lo ignoriamo.
            if nome not in nomi_visti:
                nomi_visti.add(nome)
                writer.writerow(row)
            else:
                rimossi_duplicati += 1

    print(f"OPERAZIONE COMPLETATA. File '{file_output}' pronto per la tesi.")
    print(f" -> Ultimi fantasmi eliminati: {corretti_fantasmi}")
    print(f" -> Segmenti stradali duplicati fusi: {rimossi_duplicati}")
    print(f" -> Totale ENTITA' UNICHE nel file: {len(nomi_visti)}")

except Exception as e:
    print(f"Errore critico: {e}")