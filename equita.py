import csv

file_input = 'bologna_entita_uniche_comma.csv'
file_output = 'bologna_KG_ready.csv'

# Le "False Femmine" da declassare a Toponimo
false_femmine = [
    "SANTA BARBARA", "SANT'AGNESE", "SANTA MARIA", "SANTA LUCIA", "SANTA CHIARA", 
    "SANTA CATERINA DI QUARTO", "SANT'ANNA", "SANTA CATERINA", "SANTA MARGHERITA AL COLLE", 
    "SANTA MARGHERITA", "SANTA LIBERATA", "SANT'APOLLONIA", "SANTA RITA", 
    "LEMONIA", "VALERIA", "LICINIA", "POMPONIA", "EGNAZIA", "CAMONIA", 
    "CROCEROSSINE", "VITTORIA", "LETIZIA", "SERENA", "ALTABELLA"
]

# L'ultimo falso maschio
falsi_maschi = ["RIO POLO"]

try:
    with open(file_input, mode='r', encoding='utf-8') as fin, \
         open(file_output, mode='w', encoding='utf-8', newline='') as fout:
        
        # Leggiamo con la VIRGOLA
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, delimiter=',')
        writer.writeheader()

        donne_rimosse = 0
        uomini_rimossi = 0

        for row in reader:
            nome = str(row['NOME_PULITO']).strip().upper()
            genere = row['GENERE']
            
            # Applichiamo l'equità
            if nome in false_femmine and genere == 'Female':
                row['GENERE'] = 'Toponimo'
                donne_rimosse += 1
            elif nome in falsi_maschi and genere == 'Male':
                row['GENERE'] = 'Toponimo'
                uomini_rimossi += 1
                
            writer.writerow(row)

    print(f"OPERAZIONE EQUITA' COMPLETATA. File '{file_output}' creato.")
    print(f" -> False donne rimosse: {donne_rimosse}")
    print(f" -> Falsi uomini rimossi: {uomini_rimossi}")

except Exception as e:
    print(f"Errore critico: {e}")