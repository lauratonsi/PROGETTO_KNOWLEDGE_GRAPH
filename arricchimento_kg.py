"""
arricchimento_kg.py
Arricchisce bologna_KG_corretto.ttl con nuove proprietà estratte dai CSV.

Aggiunge a clv:Street:
  ex:quartiere          – nome del quartiere
  ex:geoPoint           – coordinate WGS84 del centroide (lat, lon)
  ex:dataIstituzione    – data di istituzione ufficiale della via
  ex:tipologiaLuogo     – tipo di luogo (Via, Largo, Parco…) [da aree_verdi]

Aggiunge a cpv:Person:
  ex:macroCategoriaOccupazionale – categoria semantica della professione
  ex:datiAnagrafici     – luogo e date di nascita/morte [solo Female, da aree_verdi]
  ex:professione        – professione [solo Female già non arricchite, da aree_verdi]
"""
import csv, hashlib, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE      = Path(__file__).parent
TTL_FILE  = BASE / 'bologna_KG_corretto.ttl'
CSV_READY = BASE / 'bologna_KG_ready.csv'
CSV_PROF  = BASE / 'classificazione_professioni.csv'
CSV_VERDE = BASE / 'le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv'

STREET_PREFIXES = re.compile(
    r'^(VIA |VIALE |PIAZZA |PIAZZETTA |PIAZZALE |PASSAGGIO |ROTONDA |'
    r'GALLERIA |PONTE |LARGO |LOCALITA\' |MURA |SOTTOPASSO |VICOLO |SALITA )',
    re.IGNORECASE
)

NOT_IN = {
    "NOME VIA DA ISTITUIRE", "VIGILI DEL FUOCO", "DE LA BIRRA",
    "DISPERSI DEL NAUFRAGIO DEL PIROSCAFO ORIA", "SANTISSIMA ANNUNZIATA",
    "DECORATI AL VALOR MILITARE", "BRIGATA BOLERO", "BRIGATE PARTIGIANE",
    "FONTI DI CASAGLIA", "VOLTO SANTO", "CONSIGLIO D'EUROPA",
    "MEMORIALE DELLA SHOAH", "GRANATIERI DI SARDEGNA", "CASTELL'ARIENTI",
    "DE LA BOVA", "MASSA CARRARA", "SURROGAZIONE RENO", "BUON PASTORE",
    "LA BASTIA", "LA VENETA",
}

BASE_STREET = "https://w3id.org/bologna/resource/street/"
BASE_PERSON = "https://w3id.org/bologna/resource/person/"


def strip_prefix(s):
    return STREET_PREFIXES.sub('', s).strip()


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


# ── 1. Leggo il TTL esistente e individuo le persone già con ex:professione ──
existing_ttl = TTL_FILE.read_text(encoding='utf-8')

persons_with_prof = set()
current_uri = None
for line in existing_ttl.splitlines():
    stripped = line.strip()
    m = re.match(r'^<(https://w3id\.org/bologna/resource/person/[^>]+)>$', stripped)
    if m:
        current_uri = m.group(1)
    elif stripped.startswith('ex:professione') and current_uri:
        persons_with_prof.add(current_uri)
    elif stripped == '':
        current_uri = None

print(f'Persone con ex:professione già nel TTL: {len(persons_with_prof)}')

# ── 2. macro_categoria → {nome.upper(): macro} ──
macro_by_name = {}
with open(CSV_PROF, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        macro_by_name[row['nome'].upper()] = row['macro_categoria']

print(f'Macro-categorie caricate: {len(macro_by_name)}')

# ── 3. Aree verdi → {LABEL1.upper(): {tipologia, classificazione, dati_anagrafici}} ──
verde_by_label = {}
verde_by_nome  = {}
with open(CSV_VERDE, encoding='utf-8', errors='replace') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for row in reader:
        if len(row) < 16:
            continue
        # Indici (0-based):
        # 1=TIPOLOGIA  2=NOME(persona)  8=LABEL1(nome completo via)
        # 10=CLASSIFICAZIONE  15=DATI ANAGRAFICI
        tipologia       = row[1].strip()
        nome_persona    = row[2].strip()
        label1          = row[8].strip()
        classificazione = row[10].strip()
        dati_anagrafici = row[15].strip()
        entry = {
            'tipologia'      : tipologia,
            'classificazione': classificazione,
            'dati_anagrafici': dati_anagrafici,
        }
        if label1:
            verde_by_label[label1.upper()] = entry
        if nome_persona:
            verde_by_nome[nome_persona.upper()] = entry

print(f'Voci aree verdi per LABEL1: {len(verde_by_label)}')
print(f'Voci aree verdi per NOME:   {len(verde_by_nome)}')

# ── 4. Genero le triple di arricchimento ──
out = [
    '',
    '# ── Arricchimento — maggio 2026 ────────────────────────────────────────────',
    '# Fonti: bologna_KG_ready.csv · classificazione_professioni.csv',
    '#        le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv',
    '',
]

persons_done    = set()
streets_count   = 0
persons_count   = 0
verde_matched   = 0
prof_filled     = 0

with open(CSV_READY, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        genere = row['GENERE'].strip()
        if genere not in ('Male', 'Female'):
            continue

        cod_via    = row['CODVIA'].strip()
        nome_via   = row['NOMEVIA'].strip()
        nome_pul   = row['NOME_PULITO'].strip()
        nome_strip = strip_prefix(nome_pul)

        if nome_strip in NOT_IN:
            continue

        quartiere = row['Quartiere'].strip()
        geo_point = row['Geo Point'].strip()
        data_ist  = row['DATA_ISTIT'].strip()

        via_uri        = f"<{BASE_STREET}{cod_via}>"
        person_uri_str = f"{BASE_PERSON}{md5(nome_strip)}"
        person_uri     = f"<{person_uri_str}>"

        # Cerca la via nelle aree verdi (prima per nome completo, poi per nome persona)
        verde = (verde_by_label.get(nome_via.upper())
                 or verde_by_nome.get(nome_strip.upper())
                 or {})
        if verde:
            verde_matched += 1

        # ── Arricchimento della strada ──
        street_props = {}
        if quartiere:
            street_props['ex:quartiere']       = f'"{esc(quartiere)}"'
        if geo_point:
            street_props['ex:geoPoint']        = f'"{esc(geo_point)}"'
        if data_ist:
            street_props['ex:dataIstituzione'] = f'"{esc(data_ist)}"'
        if verde.get('tipologia'):
            street_props['ex:tipologiaLuogo']  = f'"{esc(verde["tipologia"])}"'

        if street_props:
            props_str = ' ;\n    '.join(f'{k}  {v}' for k, v in street_props.items())
            out.append(f'{via_uri}')
            out.append(f'    {props_str} .')
            out.append('')
            streets_count += 1

        # ── Arricchimento della persona (una sola volta) ──
        if person_uri not in persons_done:
            persons_done.add(person_uri)

            macro    = macro_by_name.get(nome_strip.upper(), '')
            dati_an  = ''
            prof_fill = ''

            if genere == 'Female' and verde:
                dati_an = verde.get('dati_anagrafici', '')
                # Professione da aree_verdi solo se mancante nel TTL
                if person_uri_str not in persons_with_prof:
                    prof_fill = verde.get('classificazione', '')
                    if prof_fill:
                        prof_filled += 1

            person_props = {}
            if macro:
                person_props['ex:macroCategoriaOccupazionale'] = f'"{esc(macro)}"'
            if dati_an:
                person_props['ex:datiAnagrafici']              = f'"{esc(dati_an)}"'
            if prof_fill:
                person_props['ex:professione']                 = f'"{esc(prof_fill)}"'

            if person_props:
                props_str = ' ;\n    '.join(f'{k}  {v}' for k, v in person_props.items())
                out.append(f'{person_uri}')
                out.append(f'    {props_str} .')
                out.append('')
                persons_count += 1

# ── 5. Scrivo il TTL aggiornato ──
new_ttl = existing_ttl + '\n'.join(out)
TTL_FILE.write_text(new_ttl, encoding='utf-8')

print()
print(f'Strade arricchite:             {streets_count}')
print(f'Persone arricchite:            {persons_count}')
print(f'Match aree verdi:              {verde_matched}')
print(f'Professioni colmate da verde:  {prof_filled}')
print(f'File aggiornato: {TTL_FILE.name}')
