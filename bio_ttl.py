"""
bio_ttl.py — Step 3b della pipeline
Legge F_M DATE.xlsx (UOMINI + DONNE) e aggiunge al TTL i dati biografici
recuperati da Wikidata: professione, data e luogo di nascita, data e luogo di morte.

Deve essere eseguito DOPO genera_ttl.py e PRIMA di arricchimento_kg.py,
in modo che arricchimento_kg.py possa rilevare correttamente le persone
già arricchite ed evitare duplicazioni nella colmatura da aree_verdi.

Run: python bio_ttl.py
"""

import csv, hashlib, re
from pathlib import Path
import openpyxl

BASE        = Path(__file__).parent
TTL_FILE    = BASE / 'bologna_KG_corretto.ttl'
XLSX_FILE   = BASE / 'F_M DATE.xlsx'
CSV_FILE    = BASE / 'bologna_KG_ready.csv'
BASE_PERSON = "https://w3id.org/bologna/resource/person/"

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


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def strip_prefix(s):
    return STREET_PREFIXES.sub('', s).strip()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def skip_val(v):
    return not v or str(v).strip().upper() in ('', 'N.D.', 'N.D', 'ND')


def parse_date_place(s):
    """Split 'DD mese YYYY, Luogo' → ('DD mese YYYY', 'Luogo')."""
    if not s:
        return '', ''
    m = re.search(r'\d{4},\s*(.+)$', s)
    if m:
        return s[:s.rfind(',')].strip(), m.group(1).strip()
    return s, ''


# ── Mappa nome.upper() → person_uri dal CSV (fonte di verità per gli URI) ──
name_to_uri = {}
with open(CSV_FILE, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['GENERE'] not in ('Male', 'Female'):
            continue
        ns = strip_prefix(row['NOME_PULITO'].strip())
        if ns in NOT_IN:
            continue
        name_to_uri[ns.upper()] = f"{BASE_PERSON}{md5(ns)}"

print(f"Persone nel KG (via CSV): {len(name_to_uri)}")

# ── Leggi F_M DATE.xlsx e genera le triple Turtle ──
wb  = openpyxl.load_workbook(XLSX_FILE)
out = [
    '',
    '# ── Dati biografici Wikidata (F_M DATE.xlsx) ───────────────────────────────',
    '',
]
written  = 0
skipped  = 0

for sheet_name, start_row in [('UOMINI', 1), ('DONNE', 2)]:
    ws = wb[sheet_name]
    for row in ws.iter_rows(min_row=start_row, values_only=True):
        nome_xlsx = str(row[0]).strip() if row[0] else ''
        if not nome_xlsx:
            continue

        uri = name_to_uri.get(nome_xlsx.upper())
        if not uri:
            skipped += 1
            continue

        prof      = str(row[2]).strip() if not skip_val(row[2]) else ''
        birth_str = str(row[3]).strip() if not skip_val(row[3]) else ''
        death_str = str(row[4]).strip() if not skip_val(row[4]) else ''

        data_n, luogo_n = parse_date_place(birth_str)
        data_m, luogo_m = parse_date_place(death_str)

        props = {}
        if prof:    props['ex:professione']  = prof
        if data_n:  props['ex:dataNascita']  = data_n
        if luogo_n: props['ex:luogoNascita'] = luogo_n
        if data_m:  props['ex:dataMorte']    = data_m
        if luogo_m: props['ex:luogoMorte']   = luogo_m

        if not props:
            continue

        props_str = ' ;\n    '.join(f'{k}  "{esc(v)}"' for k, v in props.items())
        out.append(f'<{uri}>')
        out.append(f'    {props_str} .')
        out.append('')
        written += 1

# ── Append al TTL ──
existing = TTL_FILE.read_text(encoding='utf-8')
TTL_FILE.write_text(existing + '\n'.join(out), encoding='utf-8')

print(f"Persone arricchite con dati biografici: {written}")
print(f"Nomi non corrispondenti (non nel KG): {skipped}")
print(f"File aggiornato: {TTL_FILE.name}")
