import csv

file_input = 'bologna_entita_uniche_comma.csv'
file_output = 'bologna_KG_ready.csv'

# Le "False Femmine" da declassare a Toponimo
false_femmine = [
    "SANTA BARBARA", "SANT'AGNESE", "SANTA MARIA", "SANTA LUCIA", "SANTA CHIARA",
    "SANTA CATERINA DI QUARTO", "SANT'ANNA", "SANTA CATERINA", "SANTA MARGHERITA AL COLLE",
    "SANTA MARGHERITA", "SANTA LIBERATA", "SANT'APOLLONIA", "SANTA RITA",
    "LEMONIA", "VALERIA", "LICINIA", "POMPONIA", "EGNAZIA", "CAMONIA",
    "CROCEROSSINE", "VITTORIA", "LETIZIA", "SERENA", "ALTABELLA",
    "SANTISSIMA ANNUNZIATA", "DUE MADONNE"
]

# I "Falsi Maschi" da declassare a Toponimo
falsi_maschi = [
    "RIO POLO",
    # Collettivi/istituzioni
    "GRANATIERI DI SARDEGNA", "VIGILI DEL FUOCO", "DECORATI AL VALOR MILITARE",
    "CONSIGLIO D'EUROPA", "DISPERSI DEL NAUFRAGIO DEL PIROSCAFO ORIA",
    "BRIGATA BOLERO", "BRIGATE PARTIGIANE",
    "COLLEGIO DI SPAGNA", "DECORATO VALORE CIVILE", "LIBER PARADISUS",
    # Luoghi e toponimi geografici
    "BAGNI DI MARIO", "BASSA DEI SASSI", "BERRETTA ROSSA", "BOCCA DI LUPO",
    "CA' SELVATICA", "CAPO DI LUCCA", "CAVEDONE", "DALLA VOLTA",
    "ESTRO MENABUE", "FANTUZZI", "FOSSA CAVA", "LA CASTIGLIA",
    "MICHELINO", "PAGLIA CORTA", "PELLEGRINO", "QUARTO DI SOPRA",
    "RIZZOLA LEVANTE", "SALITA DI SAN BENEDETTO", "SANTO STEFANO",
    "SAVENA ANTICO", "SERAGNOLI", "SPIRITO SANTO", "STAZIONE ROVERI",
    "VAL D'APOSA", "VITTORIO VENETO",
    # Gia' filtrati nel SPARQL ma ancora Male nel CSV
    "NOME VIA DA ISTITUIRE", "FONTI DI CASAGLIA", "VOLTO SANTO",
    "MEMORIALE DELLA SHOAH", "LOCALITA' CASTELL'ARIENTI", "SURROGAZIONE RENO",
    "BUON PASTORE", "MASSA CARRARA", "DE LA BIRRA", "DE LA BOVA",
    "LA BASTIA", "LA VENETA"
]

# Donne classificate erroneamente come Male
vere_femmine = [
    "ARTEMISIA GENTILESCHI",   # pittrice barocca (1593-1654)
    "BITTISIA GOZZADINI",      # giurista medievale bolognese (1209-1261)
    "PROPERZIA DE ROSSI"       # scultrice rinascimentale bolognese (c.1490-1530)
]

try:
    with open(file_input, mode='r', encoding='utf-8') as fin, \
         open(file_output, mode='w', encoding='utf-8', newline='') as fout:
        
        # Leggiamo con la VIRGOLA
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, delimiter=',')
        writer.writeheader()

        donne_rimosse = 0
        uomini_rimossi = 0
        donne_recuperate = 0

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
            elif nome in vere_femmine and genere == 'Male':
                row['GENERE'] = 'Female'
                donne_recuperate += 1

            writer.writerow(row)

    print(f"OPERAZIONE EQUITA' COMPLETATA. File '{file_output}' creato.")
    print(f" -> False donne rimosse: {donne_rimosse}")
    print(f" -> Falsi uomini rimossi: {uomini_rimossi}")
    print(f" -> Vere donne recuperate: {donne_recuperate}")

except Exception as e:
    print(f"Errore critico: {e}")