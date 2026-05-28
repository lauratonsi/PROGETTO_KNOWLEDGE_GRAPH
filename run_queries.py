"""Run all 5 SPARQL queries against the TTL and print results."""
import sys
from pathlib import Path
from rdflib import Graph

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TTL = Path('bologna_KG_corretto.ttl')
QUERIES_DIR = Path('queries')

print(f'Loading {TTL} ...')
g = Graph()
g.parse(TTL, format='turtle')
print(f'Loaded: {len(g)} triples\n')

for qfile in sorted(QUERIES_DIR.glob('q*.sparql')):
    raw = qfile.read_text(encoding='utf-8')
    # Strip comment lines starting with ##
    sparql = '\n'.join(
        line for line in raw.splitlines()
        if not line.strip().startswith('##') and not line.strip().startswith('#')
    )
    print('=' * 60)
    print(f'Query: {qfile.name}')
    print('=' * 60)
    try:
        results = list(g.query(sparql))
        vars_ = [str(v) for v in g.query(sparql).vars]
        print(f'Colonne: {vars_}')
        print(f'Risultati: {len(results)}')
        print()
        for row in results[:20]:
            print('  ', tuple(str(v) if v else '' for v in row))
        if len(results) > 20:
            print(f'  ... e altri {len(results)-20} risultati')
    except Exception as e:
        print(f'ERRORE: {e}')
    print()
