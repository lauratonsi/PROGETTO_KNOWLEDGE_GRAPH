"""Run all SPARQL queries against the KG and print results."""
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


def strip_comments(text):
    return '\n'.join(
        line for line in text.splitlines()
        if not line.strip().startswith('#')
    )


def run_select(g, sparql, name):
    result = g.query(sparql)
    rows = list(result)
    cols = [str(v) for v in result.vars]
    print(f'Colonne: {cols}')
    print(f'Risultati: {len(rows)}')
    for row in rows[:20]:
        print(' ', tuple(str(v) if v is not None else '' for v in row))
    if len(rows) > 20:
        print(f'  ... e altri {len(rows) - 20} risultati')


def run_construct(g, sparql, name):
    result = g.query(sparql)
    subgraph = result.graph
    print(f'Triple generate: {len(subgraph)}')
    for s, p, o in list(subgraph)[:10]:
        print(f'  {s!s:<60} {p!s:<40} {o!s}')
    if len(subgraph) > 10:
        print(f'  ... e altre {len(subgraph) - 10} triple')


# SELECT queries q1–q10 (sorted)
for qfile in sorted(QUERIES_DIR.glob('q*.sparql')):
    raw = qfile.read_text(encoding='utf-8')
    sparql = strip_comments(raw)
    print('=' * 60)
    print(f'Query: {qfile.name}')
    print('=' * 60)
    try:
        run_select(g, sparql, qfile.name)
    except Exception as e:
        print(f'ERRORE: {e}')
    print()

# CONSTRUCT queries
for qfile in sorted(QUERIES_DIR.glob('construct_*.sparql')):
    raw = qfile.read_text(encoding='utf-8')
    sparql = strip_comments(raw)
    print('=' * 60)
    print(f'Query: {qfile.name}')
    print('=' * 60)
    try:
        run_construct(g, sparql, qfile.name)
    except Exception as e:
        print(f'ERRORE: {e}')
    print()
