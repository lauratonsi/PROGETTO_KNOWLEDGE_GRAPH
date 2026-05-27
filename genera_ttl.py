"""
Generate bologna_KG_corretto.ttl from bologna_KG_ready.csv.
Replicates the logic of trasforma_finale.sparql without needing Java.
"""
import csv, re, sys, hashlib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
CSV_IN  = BASE / 'bologna_KG_ready.csv'
TTL_OUT = BASE / 'bologna_KG_corretto.ttl'

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

BASE_STREET  = "https://w3id.org/bologna/resource/street/"
BASE_PERSON  = "https://w3id.org/bologna/resource/person/"
CLV          = "https://w3id.org/italia/onto/CLV/"
CPV          = "https://w3id.org/italia/onto/CPV/"

def strip_prefix(s):
    return STREET_PREFIXES.sub('', s).strip()

def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def escape_literal(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

lines = [
    '@prefix clv: <https://w3id.org/italia/onto/CLV/> .',
    '@prefix cpv: <https://w3id.org/italia/onto/CPV/> .',
    '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
    '',
]

persons_written = set()
streets = 0
females = 0

with open(CSV_IN, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        genere    = row['GENERE'].strip()
        cod_via   = row['CODVIA'].strip()
        nome_via  = row['NOMEVIA'].strip()
        nome_pul  = row['NOME_PULITO'].strip()

        if genere not in ('Male', 'Female'):
            continue

        # Replicate SPARQL BIND logic
        nome_pulitissimo = strip_prefix(nome_pul)

        if nome_pulitissimo in NOT_IN:
            continue

        via_uri    = f"<{BASE_STREET}{cod_via}>"
        person_uri = f"<{BASE_PERSON}{md5(nome_pulitissimo)}>"

        # Street triples
        lines.append(f'{via_uri}')
        lines.append(f'        rdf:type           clv:Street ;')
        lines.append(f'        clv:hasStreetName  "{escape_literal(nome_via)}" ;')
        lines.append(f'        clv:isDedicatedTo  {person_uri} .')
        lines.append('')

        # Person triples (write once per unique person)
        if person_uri not in persons_written:
            lines.append(f'{person_uri}')
            lines.append(f'        rdf:type      cpv:Person ;')
            lines.append(f'        cpv:fullName  "{escape_literal(nome_pulitissimo)}" ;')
            lines.append(f'        cpv:sex       "{genere}" .')
            lines.append('')
            persons_written.add(person_uri)

        streets += 1
        if genere == 'Female':
            females += 1

TTL_OUT.write_text('\n'.join(lines), encoding='utf-8')
males = streets - females
print(f'Scritte {streets} strade: {males} Male, {females} Female')
print(f'Persone uniche: {len(persons_written)}')
print(f'File: {TTL_OUT.name}')
