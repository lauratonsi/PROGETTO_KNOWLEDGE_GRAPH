"""
Generates the full docs/ website from project CSV data.
Run once; re-run whenever data changes.
"""
import sys, csv, json, re, html
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = Path(__file__).parent
DOCS = BASE / 'docs'
DOCS.mkdir(exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────

def read_csv(path, delimiter=','):
    with open(BASE / path, encoding='utf-8', errors='replace') as f:
        return list(csv.DictReader(f, delimiter=delimiter))

clf = read_csv('classificazione_professioni.csv')
props_raw = read_csv('proposte_intitolazioni_future.csv')
women_raw = read_csv('le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne.csv', delimiter=';')

# ── Stats ─────────────────────────────────────────────────────────────────────
N_TOTAL = 1960
N_MALE = 1066
N_FEMALE = 66
N_TOPO = 828
PCT_F = 5.8

# Category chart data (exclude Altro for clarity)
CATS_ORDER = [
    "Arte visiva e architettura",
    "Musica, teatro e cinema",
    "Letteratura e giornalismo",
    "Scienze e medicina",
    "Filosofia, storia e accademia",
    "Politica e diritto",
    "Resistenza e antifascismo",
    "Istruzione ed educazione",
    "Sindacalismo e attivismo civile",
    "Patrioti, militari ed esploratori",
    "Religione",
    "Sport",
]
m_clf = [r for r in clf if r['genere']=='M']
f_clf = [r for r in clf if r['genere']=='F' and r['tipo']=='storica']
p_clf = [r for r in clf if r['tipo']=='proposta']
m_cnt = Counter(r['macro_categoria'] for r in m_clf)
f_cnt = Counter(r['macro_categoria'] for r in f_clf)
p_cnt = Counter(r['macro_categoria'] for r in p_clf)

CAT_LABELS_JS  = json.dumps(CATS_ORDER, ensure_ascii=False)
M_DATA_JS  = json.dumps([round(m_cnt.get(c,0)/len(m_clf)*100,1) for c in CATS_ORDER])
F_DATA_JS  = json.dumps([round(f_cnt.get(c,0)/len(f_clf)*100,1) for c in CATS_ORDER])
P_DATA_JS  = json.dumps([round(p_cnt.get(c,0)/len(p_clf)*100,1) for c in CATS_ORDER])

# Women streets table (person-dedicated only)
EXCL_PROF = {
    'Nominativo generico',
    "Santa, vergine e martire cristiana",
    "Santa, madre di Gesu'",
    "Santa, madre di Maria",
    'Santa, monaca agostiniana',
    'Santa, fondatrice di un ordine religioso',
}
women_persons = []
for r in women_raw:
    cl = r.get('CLASSIFICAZIONE','').strip()
    nome = (r.get('NOME COMPLETO','') or r.get('NOME','')).strip()
    if cl in EXCL_PROF or not nome or nome.startswith('Maestre'):
        continue
    women_persons.append({
        'nome': nome,
        'label': r.get('LABEL1','').strip(),
        'tipologia': r.get('TIPOLOGIA','').strip(),
        'quartiere': r.get('QUARTIERE','').strip(),
        'anno': r.get('ISTITUZIONE ANNO','').strip(),
        'professione': cl,
        'dati': r.get('DATI ANAGRAFICI','').strip(),
    })
WOMEN_JS = json.dumps(women_persons, ensure_ascii=False)

# Proposals JSON
proposals = []
for p in props_raw:
    fonte = p.get('fonti','').strip()
    proposals.append({
        'nome': p['nome_completo'],
        'professione': p['professione'],
        'nascita': p['nascita'],
        'morte': p['morte'],
        'legame': p['legame_bologna'],
        'punti': p['punti_chiave'],
        'fonte': fonte,
        'stato': p['stato'],
        'eleggibile': p.get('eleggibile_dal',''),
    })
# Get macro-category from clf
prop_cats = {r['nome']: r['macro_categoria'] for r in clf if r['tipo']=='proposta'}
for p in proposals:
    p['categoria'] = prop_cats.get(p['nome'], 'Altro')
PROPOSALS_JS = json.dumps(proposals, ensure_ascii=False)

# ── Shared components ─────────────────────────────────────────────────────────

def sparql_highlight(code):
    """Minimal SPARQL syntax highlighting."""
    keywords = r'\b(PREFIX|SELECT|WHERE|FILTER|OPTIONAL|UNION|DISTINCT|GROUP BY|ORDER BY|LIMIT|REGEX|STRSTARTS|BIND|COUNT|AS|DESC|ASC|a)\b'
    prefixes = r'\b(clv|cpv|rdf|rdfs|owl|xsd)\b(?=:)'
    strings = r'"[^"]*"'
    comments = r'##[^\n]*'
    uris = r'<[^>]+>'
    variables = r'\?[a-zA-Z_][a-zA-Z0-9_]*'

    # Escape first
    code = html.escape(code)
    # Apply highlighting (order matters)
    code = re.sub(comments, lambda m: f'<span class="sc">{m.group()}</span>', code)
    code = re.sub(uris, lambda m: f'<span class="su">{m.group()}</span>', code)
    code = re.sub(strings, lambda m: f'<span class="ss">{m.group()}</span>', code)
    code = re.sub(keywords, lambda m: f'<span class="sk">{m.group()}</span>', code)
    code = re.sub(prefixes, lambda m: f'<span class="sp">{m.group()}</span>', code)
    code = re.sub(variables, lambda m: f'<span class="sv">{m.group()}</span>', code)
    return code

NAV = '''<nav id="navbar">
  <div class="nav-inner">
    <a class="nav-brand" href="index.html">Bologna Gender Gap KG</a>
    <button class="nav-toggle" onclick="document.getElementById('navbar').classList.toggle('open')" aria-label="menu">&#9776;</button>
    <ul class="nav-links">
      <li><a href="index.html">Home</a></li>
      <li><a href="topic.html">Il Tema</a></li>
      <li><a href="methodology.html">Metodologia</a></li>
      <li><a href="sparql.html">Query SPARQL</a></li>
      <li><a href="llm.html">LLM &amp; Prompt</a></li>
      <li><a href="results.html">Risultati</a></li>
      <li><a href="proposals.html">Proposte</a></li>
    </ul>
  </div>
</nav>'''

def page(title, content, active='', extra_head='', extra_js=''):
    nav = NAV.replace(f'href="{active}"', f'href="{active}" class="active"') if active else NAV
    return f'''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Gender Gap Bologna</title>
  <link rel="stylesheet" href="style.css">
  {extra_head}
</head>
<body>
{nav}
<main>
{content}
</main>
<footer>
  <div class="footer-inner">
    <p>Progetto universitario — Corso di <em>Metodologie e Tecniche di Simulazione</em>, GEPID 2024–25, Università di Bologna</p>
    <p>Dati: <a href="https://opendata.comune.bologna.it/" target="_blank">Open Data Comune di Bologna</a> ·
       Knowledge Graph: <a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH" target="_blank">GitHub</a></p>
  </div>
</footer>
{extra_js}
</body>
</html>'''

# ── style.css ─────────────────────────────────────────────────────────────────

CSS = '''
:root {
  --primary: #8b1a4a;
  --primary-light: #c45c82;
  --blue: #1b3a6b;
  --green: #1a6b3a;
  --green-light: #d4edda;
  --amber: #b5650a;
  --amber-light: #fff3cd;
  --text: #1a1a1a;
  --text-muted: #5a5a5a;
  --bg: #f8f6f2;
  --white: #ffffff;
  --border: #ddd8d0;
  --nav-bg: #1a1a2e;
  --nav-height: 62px;
  --radius: 8px;
  --shadow: 0 2px 12px rgba(0,0,0,0.08);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.7;
  color: var(--text);
  background: var(--bg);
}

/* ── Navigation ── */
#navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: var(--nav-bg);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  height: var(--nav-height);
}
.nav-inner {
  max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;
  display: flex; align-items: center; height: 100%;
}
.nav-brand {
  color: #fff; font-weight: 700; font-size: 1rem;
  text-decoration: none; white-space: nowrap; margin-right: 2rem;
  letter-spacing: 0.02em;
}
.nav-links {
  list-style: none; display: flex; gap: 0.2rem; flex-wrap: wrap;
}
.nav-links a {
  color: rgba(255,255,255,0.8); text-decoration: none;
  padding: 0.4rem 0.75rem; border-radius: 5px;
  font-size: 0.88rem; transition: background 0.15s, color 0.15s;
}
.nav-links a:hover, .nav-links a.active {
  background: var(--primary); color: #fff;
}
.nav-toggle { display: none; background: none; border: none; color: #fff; font-size: 1.4rem; cursor: pointer; margin-left: auto; }

/* ── Main ── */
main { margin-top: var(--nav-height); min-height: calc(100vh - var(--nav-height) - 80px); }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, var(--nav-bg) 0%, #2d1b3d 100%);
  color: #fff; padding: 5rem 1.5rem 4rem; text-align: center;
}
.hero h1 { font-family: Georgia, serif; font-size: clamp(1.8rem, 4vw, 3rem); margin-bottom: 1rem; }
.hero p  { font-size: 1.1rem; opacity: 0.85; max-width: 680px; margin: 0 auto 2rem; }
.hero-stat { display: inline-block; background: var(--primary); padding: 0.8rem 2.5rem; border-radius: 50px; font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em; }
.hero-stat small { font-size: 1rem; font-weight: 400; opacity: 0.85; display: block; }

/* ── Sections ── */
.section { max-width: 1100px; margin: 0 auto; padding: 3.5rem 1.5rem; }
.section + .section { padding-top: 1rem; }
.section-alt { background: var(--white); }
.section-alt .section { padding: 3.5rem 1.5rem; }
h2 { font-family: Georgia, serif; font-size: 1.9rem; color: var(--primary); margin-bottom: 1.2rem; border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; }
h3 { font-size: 1.2rem; color: var(--nav-bg); margin: 2rem 0 0.6rem; }
h4 { font-size: 1rem; color: var(--text); margin: 1.2rem 0 0.4rem; font-weight: 600; }
p  { margin-bottom: 1rem; }
a  { color: var(--primary); }
a:hover { color: var(--primary-light); }
ul, ol { margin: 0.5rem 0 1rem 1.5rem; }
li { margin-bottom: 0.3rem; }

/* ── Cards grid ── */
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.2rem; margin-top: 1.5rem; }
.card {
  background: var(--white); border-radius: var(--radius); padding: 1.4rem;
  box-shadow: var(--shadow); border-top: 4px solid var(--primary);
  transition: transform 0.15s, box-shadow 0.15s;
}
.card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
.card.future { border-top-color: var(--amber); }
.card h3 { margin-top: 0; font-size: 1.05rem; color: var(--primary); }
.card.future h3 { color: var(--amber); }
.card-meta { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.card p { font-size: 0.9rem; margin-bottom: 0.6rem; }
.badge {
  display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
}
.badge-active { background: var(--green-light); color: var(--green); }
.badge-future { background: var(--amber-light); color: var(--amber); }
.card-fonte { font-size: 0.78rem; margin-top: 0.6rem; }

/* ── Stat boxes ── */
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 2rem 0; }
.stat-box { background: var(--white); border-radius: var(--radius); padding: 1.5rem 1rem; text-align: center; box-shadow: var(--shadow); }
.stat-box .number { font-size: 2.4rem; font-weight: 700; line-height: 1; }
.stat-box .label { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.4rem; }
.stat-male   .number { color: var(--blue); }
.stat-female .number { color: var(--primary); }
.stat-topo   .number { color: #5a5a5a; }
.stat-pct    .number { color: var(--primary); }

/* ── Charts ── */
.chart-wrap { position: relative; max-width: 700px; margin: 1.5rem auto; }
.chart-wrap-full { position: relative; width: 100%; margin: 1.5rem 0; height: 420px; }

/* ── Code blocks ── */
.code-block {
  background: #1e1e2e; color: #cdd6f4; border-radius: var(--radius);
  padding: 1.4rem 1.6rem; overflow-x: auto; font-family: 'Consolas','Monaco','Courier New',monospace;
  font-size: 0.82rem; line-height: 1.7; margin: 1rem 0 1.5rem;
}
.code-block .sc { color: #6c7086; font-style: italic; }  /* comment */
.code-block .sk { color: #89b4fa; font-weight: bold; }   /* keyword */
.code-block .sp { color: #a6e3a1; }                      /* prefix name */
.code-block .su { color: #f9e2af; }                      /* uri */
.code-block .ss { color: #a6e3a1; }                      /* string */
.code-block .sv { color: #cba6f7; }                      /* variable */

/* ── Prompt boxes ── */
.prompt-box {
  border-left: 4px solid var(--primary); background: var(--white);
  padding: 1rem 1.2rem; border-radius: 0 var(--radius) var(--radius) 0;
  margin: 0.8rem 0 1.2rem; font-size: 0.92rem;
}
.response-box {
  border-left: 4px solid var(--blue); background: #f0f4ff;
  padding: 1rem 1.2rem; border-radius: 0 var(--radius) var(--radius) 0;
  margin: 0.8rem 0 1.5rem; font-size: 0.92rem;
}
.prompt-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.3rem; }

/* ── Table ── */
.table-wrap { overflow-x: auto; margin: 1rem 0; }
table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
th { background: var(--nav-bg); color: #fff; padding: 0.6rem 0.8rem; text-align: left; font-weight: 600; }
td { padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--border); }
tr:nth-child(even) td { background: #f5f3ef; }
tr:hover td { background: #ede8e0; }

/* ── Filters ── */
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0; }
.filter-btn {
  padding: 0.4rem 1rem; border-radius: 20px; border: 2px solid var(--border);
  background: var(--white); cursor: pointer; font-size: 0.85rem; transition: all 0.15s;
}
.filter-btn:hover, .filter-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
#search-box {
  padding: 0.5rem 1rem; border: 2px solid var(--border); border-radius: 20px;
  font-size: 0.9rem; width: 100%; max-width: 360px; outline: none;
}
#search-box:focus { border-color: var(--primary); }

/* ── LLM table ── */
.llm-table td, .llm-table th { padding: 0.7rem 1rem; }
.llm-table .check { color: var(--green); font-weight: bold; }
.llm-table .partial { color: var(--amber); }
.llm-table .cross { color: #c0392b; }

/* ── Step list ── */
.step-list { list-style: none; margin: 1rem 0; padding: 0; counter-reset: steps; }
.step-list li {
  counter-increment: steps; display: flex; gap: 1rem;
  padding: 1rem; background: var(--white); border-radius: var(--radius);
  box-shadow: var(--shadow); margin-bottom: 0.8rem;
}
.step-list li::before {
  content: counter(steps); min-width: 2rem; height: 2rem;
  background: var(--primary); color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; flex-shrink: 0;
}

/* ── Team ── */
.team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-top: 1.5rem; }
.team-card { background: var(--white); border-radius: var(--radius); padding: 2rem 1.5rem; text-align: center; box-shadow: var(--shadow); }
.team-avatar { width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--primary-light)); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #fff; margin: 0 auto 1rem; }
.team-card h3 { font-size: 1.1rem; margin-bottom: 0.3rem; }
.team-card p { font-size: 0.88rem; color: var(--text-muted); margin: 0; }

/* ── Info box ── */
.info-box { background: #e8f4fd; border-left: 4px solid var(--blue); padding: 1rem 1.2rem; border-radius: 0 var(--radius) var(--radius) 0; margin: 1rem 0; font-size: 0.92rem; }
.warn-box  { background: var(--amber-light); border-left: 4px solid var(--amber); padding: 1rem 1.2rem; border-radius: 0 var(--radius) var(--radius) 0; margin: 1rem 0; font-size: 0.92rem; }

/* ── Footer ── */
footer { background: var(--nav-bg); color: rgba(255,255,255,0.65); padding: 2rem 1.5rem; font-size: 0.82rem; }
.footer-inner { max-width: 1100px; margin: 0 auto; }
footer a { color: rgba(255,255,255,0.8); }
footer p { margin-bottom: 0.4rem; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .nav-toggle { display: block; }
  .nav-links { display: none; flex-direction: column; position: absolute; top: var(--nav-height); left: 0; right: 0; background: var(--nav-bg); padding: 1rem; gap: 0.2rem; }
  #navbar.open .nav-links { display: flex; }
  .hero { padding: 3rem 1rem 2.5rem; }
}
.grafici-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}
.grafici-grid figure {
  margin: 0;
  background: #f8f8f8;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}
.grafici-grid img {
  width: 100%;
  display: block;
}
.grafici-grid figcaption {
  padding: 0.6rem 0.8rem;
  font-size: 0.83rem;
  color: #555;
  text-align: center;
}
.btn-webvowl {
  display: inline-block;
  background: var(--primary);
  color: #fff;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: background 0.2s;
}
.btn-webvowl:hover { background: var(--primary-light); color: #fff; }
.webvowl-note { font-size: 0.85rem; color: #555; margin-top: 0.75rem; }
'''

(DOCS / 'style.css').write_text(CSS, encoding='utf-8')
print('style.css ✓')

# ── index.html ────────────────────────────────────────────────────────────────

INDEX = page('Home', f'''
<div class="hero">
  <h1>Gender Gap nella Toponomastica di Bologna</h1>
  <p>Un Knowledge Graph RDF per analizzare e visualizzare il divario di genere
     nelle intitolazioni stradali della città di Bologna.</p>
  <div class="hero-stat">
    {PCT_F}%
    <small>delle strade dedicate a persone è intitolata a una donna</small>
  </div>
</div>

<div class="section-alt"><div class="section">
  <h2>Il Progetto</h2>
  <p>Questo progetto nasce nell'ambito del corso di <em>Metodologie e Tecniche di Simulazione</em>
  (GEPID 2024–25, Università di Bologna) con l'obiettivo di costruire un
  <strong>Knowledge Graph (KG)</strong> dello stradario bolognese e analizzare la distribuzione
  di genere nelle intitolazioni. Su <strong>{N_TOTAL:,} strade</strong> censite, solo <strong>{N_FEMALE}</strong>
  ({PCT_F}%) sono intitolate a donne identificate. Il gap è drammatico: le strade maschili
  superano quelle femminili in un rapporto di circa 16 a 1.</p>

  <p>Il KG è stato costruito a partire dagli
  <a href="https://opendata.comune.bologna.it/" target="_blank">Open Data del Comune di Bologna</a>,
  classificando ogni intitolazione con l'ausilio di modelli linguistici avanzati
  (LLM) e arricchendo i dati biografici tramite l'<a href="https://www.wikidata.org/" target="_blank">API di Wikidata</a>.</p>

  <div class="stat-grid">
    <div class="stat-box stat-male">
      <div class="number">{N_MALE}</div>
      <div class="label">Strade maschili</div>
    </div>
    <div class="stat-box stat-female">
      <div class="number">{N_FEMALE}</div>
      <div class="label">Strade femminili</div>
    </div>
    <div class="stat-box stat-topo">
      <div class="number">{N_TOPO}</div>
      <div class="label">Toponimi / istituzionali</div>
    </div>
    <div class="stat-box stat-pct">
      <div class="number">{PCT_F}%</div>
      <div class="label">Quota femminile (su pers.)</div>
    </div>
  </div>
</div></div>

<div class="section">
  <h2>Il Team</h2>
  <p>Progetto sviluppato da due studentesse del corso di Laurea Magistrale
  in Geography and Environmental Processes in the Digital Age (GEPID).</p>
  <div class="team-grid">
    <div class="team-card">
      <div class="team-avatar">S</div>
      <h3>Susanna Cioni</h3>
      <p>Università di Bologna<br>GEPID 2024–25</p>
    </div>
    <div class="team-card">
      <div class="team-avatar">L</div>
      <h3>Laura Tonsi</h3>
      <p>Università di Bologna<br>GEPID 2024–25</p>
    </div>
  </div>
</div>

<div class="section-alt"><div class="section">
  <h2>Struttura del sito</h2>
  <div class="card-grid">
    <div class="card"><h3><a href="topic.html">Il Tema</a></h3>
      <p>Il gender gap toponomastico: cos'è, perché è importante, il contesto bolognese.</p></div>
    <div class="card"><h3><a href="methodology.html">Metodologia</a></h3>
      <p>Come è stato costruito il KG: dati, classificazione, arricchimento Wikidata, strumenti usati.</p></div>
    <div class="card"><h3><a href="sparql.html">Query SPARQL</a></h3>
      <p>Cinque query sul KG con codice, spiegazione e risultati. Tutte le keyword obbligatorie.</p></div>
    <div class="card"><h3><a href="llm.html">LLM &amp; Prompt</a></h3>
      <p>Le tre tecniche di prompting, i modelli confrontati (Claude, ChatGPT, Gemini, DeepSeek, Copilot) e le sfide.</p></div>
    <div class="card"><h3><a href="results.html">Risultati</a></h3>
      <p>Grafici interattivi sul divario di genere e classificazione professionale. Tabella delle strade femminili.</p></div>
    <div class="card"><h3><a href="proposals.html">Proposte</a></h3>
      <p>34 candidature per nuove intitolazioni stradali a donne, persone trans e non binarie.</p></div>
  </div>
</div></div>

<div class="section">
  <h2>Risorse</h2>
  <ul>
    <li><a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH" target="_blank">Repository GitHub del progetto</a></li>
    <li><a href="https://opendata.comune.bologna.it/explore/dataset/rifter_arcstra_li/information/" target="_blank">Open Data Comune di Bologna — Archi Stradali</a></li>
    <li><a href="https://opendata.comune.bologna.it/explore/dataset/le-aree-verdi-e-le-vie-di-bologna-dedicate-alle-donne/information/" target="_blank">Open Data — Vie dedicate alle donne</a></li>
    <li><a href="https://www.wikidata.org/" target="_blank">Wikidata</a></li>
    <li><a href="https://w3id.org/italia/onto/CPV/" target="_blank">Ontologia CPV — Persone</a></li>
    <li><a href="https://w3id.org/italia/onto/CLV/" target="_blank">Ontologia CLV — Luoghi</a></li>
  </ul>
</div>
''', active='index.html')

(DOCS / 'index.html').write_text(INDEX, encoding='utf-8')
print('index.html ✓')

# ── topic.html ────────────────────────────────────────────────────────────────

TOPIC = page('Il Tema', '''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>Il Tema: Gender Gap Toponomastico</h1>
  <p>Le strade che percorriamo ogni giorno raccontano chi siamo — o meglio, chi <em>non</em> siamo.</p>
</div>

<div class="section">
  <h2>Cos'è il gender gap toponomastico</h2>
  <p>La <strong>toponomastica urbana</strong> — l'insieme dei nomi attribuiti a vie, piazze, parchi e spazi pubblici —
  è uno specchio della memoria collettiva di una città. Ogni intitolazione è una scelta: si decide chi merita
  di essere ricordato nello spazio condiviso, chi entra nella coscienza quotidiana dei cittadini.</p>

  <p>Quando la grande maggioranza delle strade è intitolata a uomini, la città stessa diventa un testo
  che racconta una storia parziale: la storia di chi ha detenuto il potere, l'accesso all'istruzione,
  la visibilità pubblica. Le donne, i cui contributi sono stati spesso ignorati o sminuiti dalla storiografia
  tradizionale, restano assenti dallo spazio urbano.</p>

  <div class="info-box">
    <strong>Dati europei:</strong> secondo il progetto <a href="https://equalstreetnames.org/" target="_blank">Equal Street Names</a>,
    nella maggior parte delle città europee meno del 15% delle strade intitolate a persone porta il nome di una donna.
    Bologna, con il 5,8%, è significativamente al di sotto di questa media già bassa.
  </div>

  <h2>Il caso di Bologna</h2>
  <p>Bologna è una città progressista, con una lunga tradizione di amministrazione di sinistra e di
  attenzione alle questioni di genere. Eppure, il suo stradario racconta un'altra storia.
  Su <strong>1.960 archi stradali</strong> censiti:</p>

  <ul>
    <li><strong>1.066</strong> sono intitolati a persone di genere maschile</li>
    <li><strong>66</strong> sono intitolati a persone di genere femminile</li>
    <li><strong>828</strong> sono toponimi, nomi istituzionali o riferimenti a luoghi</li>
  </ul>

  <p>Il rapporto tra strade maschili e femminili è di circa <strong>16:1</strong>.
  Per ogni donna ricordata nello spazio pubblico bolognese, ci sono sedici uomini.</p>

  <h2>Le tre categorie di classificazione</h2>
  <p>Ogni intitolazione stradale del dataset è stata classificata in una di tre categorie:</p>
  <ul>
    <li><strong>Male</strong> — intitolata a una persona di genere maschile, o a un gruppo denominato
    con sostantivo maschile (es. <em>Fratelli Cervi</em>, <em>Ragazzi del \'99</em>).</li>
    <li><strong>Female</strong> — intitolata a una persona di genere femminile.</li>
    <li><strong>Toponimo</strong> — intitolata a un luogo, un concetto, un'istituzione, un mestiere,
    un evento storico, o un nome di famiglia senza un referente individuale identificabile.</li>
  </ul>

  <div class="warn-box">
    <strong>Nota critica — Fratelli Marincola:</strong> il Passaggio Fratelli Marincola è intitolato
    a Giorgio <em>e</em> Isabella Marincola, fratello e sorella, entrambi partigiani.
    L'uso del termine grammaticale "fratelli" rende invisibile la presenza di Isabella.
    Abbiamo classificato questa strada come <em>Male</em> per rispettare la denominazione ufficiale,
    ma segnaliamo esplicitamente questa ingiustizia linguistica.
  </div>

  <h2>Perché costruire un Knowledge Graph</h2>
  <p>Un semplice foglio di calcolo può contare le strade, ma un Knowledge Graph permette
  di <em>connettere</em> le informazioni: la persona alla sua professione, al suo contesto storico,
  alle sue date di nascita e morte, ad altre risorse sul web (Wikidata, Wikipedia).
  Questa connettività è ciò che trasforma un dataset in conoscenza navigabile e riusabile.</p>

  <p>Il KG di questo progetto utilizza le ontologie italiane
  <a href="https://w3id.org/italia/onto/CLV/" target="_blank">CLV</a> (luoghi) e
  <a href="https://w3id.org/italia/onto/CPV/" target="_blank">CPV</a> (persone),
  seguendo gli standard del Semantic Web e garantendo l'interoperabilità con altri dataset aperti.</p>
</div>
''', active='topic.html')

(DOCS / 'topic.html').write_text(TOPIC, encoding='utf-8')
print('topic.html ✓')

# ── methodology.html ──────────────────────────────────────────────────────────

METHODOLOGY = page('Metodologia', '''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>Metodologia</h1>
  <p>Dal dataset grezzo del Comune di Bologna al Knowledge Graph arricchito: i passi del progetto.</p>
</div>

<div class="section">
  <h2>Flusso di lavoro</h2>
  <ol class="step-list">
    <li><div><strong>Acquisizione dati</strong><br>
      Download degli <a href="https://opendata.comune.bologna.it/" target="_blank">Open Data del Comune di Bologna</a>:
      il dataset degli archi stradali (<em>rifter_arcstra</em>, 1.960 record) e il dataset
      "Vie dedicate alle donne" (157 record). I dati sono in formato CSV.</div></li>
    <li><div><strong>Classificazione di genere</strong><br>
      Per ogni strada è stato identificato il referente (persona, luogo, concetto) e assegnata
      la categoria <em>Male</em>, <em>Female</em> o <em>Toponimo</em>.
      Questa operazione — la più impegnativa — è stata condotta con l'ausilio di LLM
      (DeepSeek, Gemini, ChatGPT, Claude, Copilot) e validata manualmente.</div></li>
    <li><div><strong>Costruzione del Knowledge Graph</strong><br>
      Lo script <code>genera_ttl.py</code> (Python + <a href="https://rdflib.readthedocs.io/" target="_blank">rdflib</a>)
      legge il CSV classificato e genera il file <code>bologna_KG_corretto.ttl</code>
      in formato Turtle (6.783 triple). Ogni strada è un nodo <code>clv:Street</code>;
      le strade dedicate a persone sono collegate tramite <code>clv:isDedicatedTo</code> a un nodo <code>cpv:Person</code>.</div></li>
    <li><div><strong>Arricchimento biografico via Wikidata</strong><br>
      Per le ~470 persone identificate, lo script <code>wikidata_fetch.py</code> interroga
      l'<a href="https://www.wikidata.org/w/api.php" target="_blank">API JSON di Wikidata</a>
      recuperando professione (P106), data/luogo di nascita (P569/P19) e
      data/luogo di morte (P570/P20). I dati sono salvati nel file <code>F_M DATE.xlsx</code>.</div></li>
    <li><div><strong>Classificazione professionale</strong><br>
      Lo script <code>classifica_professioni.py</code> assegna una delle 12 macro-categorie
      a ciascuna delle 1.192 persone classificate (1.091 uomini + 67 donne storiche + 34 proposte),
      usando il matching per parole chiave sulle professioni Wikidata.</div></li>
    <li><div><strong>Proposte di intitolazione</strong><br>
      Il gruppo di ricerca ha identificato e documentato 34 candidature
      (29 attive + 5 future) per nuove intitolazioni a donne, persone trans e non binarie
      con legame con Bologna o rilevanza nazionale. I dati sono in
      <code>proposte_intitolazioni_future.csv</code> e <code>proposte_KG.ttl</code>.</div></li>
  </ol>

  <h2>Struttura del Knowledge Graph</h2>
  <p>Il KG utilizza due ontologie del Semantic Web italiano:</p>
  <ul>
    <li><a href="https://w3id.org/italia/onto/CLV/" target="_blank"><strong>CLV</strong></a>
    (Core Location Vocabulary) — per modellare le strade</li>
    <li><a href="https://w3id.org/italia/onto/CPV/" target="_blank"><strong>CPV</strong></a>
    (Core Person Vocabulary) — per modellare le persone</li>
  </ul>

  <p>Esempio di triple per una strada femminile:</p>
  <pre class="code-block"><code>&lt;https://w3id.org/bologna/resource/street/abc123&gt;
    a clv:Street ;
    clv:hasStreetName "VIA LAURA BASSI" ;
    clv:isDedicatedTo &lt;https://w3id.org/bologna/resource/person/def456&gt; .

&lt;https://w3id.org/bologna/resource/person/def456&gt;
    a cpv:Person ;
    cpv:fullName "Laura Bassi Veratti" ;
    cpv:sex "Female" .</code></pre>

  <p>Per le proposte di intitolazione, abbiamo esteso il vocabolario con una proprietà custom:</p>
  <pre class="code-block"><code>@prefix ex: &lt;https://w3id.org/bologna/ontology#&gt; .

&lt;https://w3id.org/bologna/resource/person/...&gt;
    a cpv:Person ;
    cpv:fullName "Maria Dalle Donne" ;
    cpv:sex "Female" ;
    ex:proposta "true" ;
    ex:statoProposta "attiva" .</code></pre>

  <h2>Visualizzazione dell'ontologia (WebVOWL)</h2>
  <p>Lo schema delle classi e proprietà è disponibile nel file <code>schema.ttl</code> in formato OWL/Turtle.
  Puoi esplorarlo interattivamente con <strong>WebVOWL</strong>, uno strumento open source per la
  visualizzazione grafica di ontologie OWL sviluppato dall'Università di Stoccarda.</p>
  <div style="text-align:center; margin:2rem 0">
    <a class="btn-webvowl"
       href="https://vowl.visualdataweb.org/webvowl.html#iri=https://lauratonsi.github.io/PROGETTO_KNOWLEDGE_GRAPH/schema.ttl"
       target="_blank" rel="noopener">
      Apri lo schema in WebVOWL &rarr;
    </a>
    <p class="webvowl-note">WebVOWL carica <code>schema.ttl</code> da GitHub Pages e mostra le classi
    (<em>Street</em>, <em>Person</em>), la proprietà oggetto <em>isDedicatedTo</em> e le proprietà dato
    (<em>hasStreetName</em>, <em>sex</em>, <em>fullName</em>, <em>proposta</em>, <em>statoProposta</em>)
    come grafo interattivo navigabile.</p>
  </div>

  <h2>Strumenti utilizzati</h2>
  <div class="card-grid">
    <div class="card">
      <h3>Python 3 + rdflib</h3>
      <p>Generazione e manipolazione del KG in formato Turtle.
      <a href="https://rdflib.readthedocs.io/" target="_blank">rdflib</a> è la libreria Python
      standard per il Semantic Web.</p>
    </div>
    <div class="card">
      <h3>openpyxl</h3>
      <p>Lettura e scrittura del file <code>F_M DATE.xlsx</code> con i dati biografici
      delle 1.160 persone censite.</p>
    </div>
    <div class="card">
      <h3>Wikidata API</h3>
      <p>Recupero automatico di professioni e date biografiche per ~470 persone tramite
      <a href="https://www.wikidata.org/w/api.php" target="_blank">wbsearchentities</a> e
      <code>wbgetentities</code>.</p>
    </div>
    <div class="card">
      <h3>SPARQL-Anything</h3>
      <p>Tool Java per eseguire query SPARQL CONSTRUCT su file CSV, usato nelle
      fasi iniziali del progetto per generare le triple RDF.</p>
    </div>
    <div class="card">
      <h3>LLM (5 modelli)</h3>
      <p>DeepSeek, Gemini, ChatGPT, Claude e Copilot per la classificazione di genere
      e l'arricchimento del KG. Vedi la sezione
      <a href="llm.html">LLM &amp; Prompt</a> per il confronto.</p>
    </div>
    <div class="card">
      <h3>Chart.js + HTML/CSS/JS</h3>
      <p>Visualizzazioni interattive in questo sito. Tutto il codice è pubblicamente
      disponibile nel <a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH" target="_blank">repository GitHub</a>.</p>
    </div>
  </div>

  <h2>Note metodologiche complete</h2>
  <p>La documentazione dettagliata delle scelte classificatorie (santi → Toponimo,
  soprannomi storici → Male/Female, Fratelli → Male, persone transgender, casi critici)
  è disponibile nel file
  <a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH/blob/classificazioni-corrette/NOTE_METODOLOGICHE.md" target="_blank">NOTE_METODOLOGICHE.md</a>
  nel repository.</p>
</div>
''', active='methodology.html')

(DOCS / 'methodology.html').write_text(METHODOLOGY, encoding='utf-8')
print('methodology.html ✓')

# ── sparql.html ───────────────────────────────────────────────────────────────

with open(BASE / 'queries/q1_conteggio_per_genere.sparql', encoding='utf-8') as f: Q1 = f.read()
with open(BASE / 'queries/q2_strade_dedicate_a_donne.sparql', encoding='utf-8') as f: Q2 = f.read()
with open(BASE / 'queries/q3_tipologia_via_per_genere.sparql', encoding='utf-8') as f: Q3 = f.read()
with open(BASE / 'queries/q4_regex_nomi_composti.sparql', encoding='utf-8') as f: Q4 = f.read()
with open(BASE / 'queries/q5_persone_con_dati_opzionali.sparql', encoding='utf-8') as f: Q5 = f.read()

SPARQL = page('Query SPARQL', f'''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>Query SPARQL sul Knowledge Graph</h1>
  <p>Cinque query che interrogano il KG bolognese.
  Utilizzano tutte le keyword obbligatorie: OPTIONAL, DISTINCT, UNION, FILTER, REGEX, LIMIT, ORDER BY.</p>
</div>

<div class="section">
  <div class="info-box">
    Il Knowledge Graph è disponibile come file Turtle nel repository:
    <a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH/blob/classificazioni-corrette/bologna_KG_corretto.ttl" target="_blank">
    bologna_KG_corretto.ttl</a> (6.783 triple).
    Per eseguire le query localmente: <code>python run_queries.py</code> (usa
    <a href="https://rdflib.readthedocs.io/" target="_blank">rdflib</a>).
  </div>

  <h2>Query 1 — Conteggio strade per genere</h2>
  <p><strong>Domanda:</strong> quante strade di Bologna sono dedicate a uomini e quante a donne?
  Questa è la risposta principale al gender gap.<br>
  <strong>Keyword:</strong> <code>DISTINCT</code>, <code>COUNT</code>, <code>GROUP BY</code>, <code>ORDER BY</code></p>
  <pre class="code-block"><code>{sparql_highlight(Q1)}</code></pre>
  <h4>Risultati:</h4>
  <div class="table-wrap"><table>
    <tr><th>?genere</th><th>?numero_strade</th></tr>
    <tr><td>Male</td><td>1066</td></tr>
    <tr><td>Female</td><td>66</td></tr>
  </table></div>
  <p style="font-size:0.88rem;color:var(--text-muted)">Le 828 strade classificate come Toponimo non hanno un nodo <code>cpv:Person</code>
  associato e non compaiono in questa query, che filtra solo i nodi con <code>cpv:sex</code>.</p>

  <h2>Query 2 — Lista delle strade dedicate a donne</h2>
  <p><strong>Domanda:</strong> quali strade di Bologna sono intitolate a donne?<br>
  <strong>Keyword:</strong> <code>DISTINCT</code>, <code>FILTER</code>, <code>ORDER BY</code>, <code>LIMIT</code></p>
  <pre class="code-block"><code>{sparql_highlight(Q2)}</code></pre>
  <h4>Primi 5 risultati (su 66 totali):</h4>
  <div class="table-wrap"><table>
    <tr><th>?nomeVia</th><th>?nomePersona</th></tr>
    <tr><td>LARGO MARIELE VENTRE</td><td>Maria Rachele Ventre</td></tr>
    <tr><td>PIAZZA NILDE IOTTI</td><td>Nilde Iotti</td></tr>
    <tr><td>VIA ADA NEGRI</td><td>Ada Negri</td></tr>
    <tr><td>VIA ADELAIDE BORGHI MAMO</td><td>Adelaide Borghi Mamo</td></tr>
    <tr><td>VIA ADELAIDE RISTORI</td><td>Adelaide Ristori</td></tr>
  </table></div>

  <h2>Query 3 — Tipologia delle strade femminili</h2>
  <p><strong>Domanda:</strong> le strade intitolate a donne sono prevalentemente "Via" o "Piazza/Piazzale"?
  La tipologia riflette una gerarchia simbolica nel riconoscimento pubblico.<br>
  <strong>Keyword:</strong> <code>UNION</code>, <code>FILTER</code>, <code>DISTINCT</code>, <code>ORDER BY</code></p>
  <pre class="code-block"><code>{sparql_highlight(Q3)}</code></pre>
  <h4>Risultati aggregati:</h4>
  <div class="table-wrap"><table>
    <tr><th>?tipologia</th><th>Conteggio</th></tr>
    <tr><td>Via</td><td>45</td></tr>
    <tr><td>Piazza / Piazzale</td><td>8</td></tr>
  </table></div>
  <p style="font-size:0.88rem;color:var(--text-muted)">Le restanti intitolazioni femminili sono Largo, Passaggio, Rotonda, Vicolo.
  Solo 8 donne hanno una piazza o un piazzale a loro nome.</p>

  <h2>Query 4 — REGEX: strade "Fratelli" e donne di nome "Maria"</h2>
  <p><strong>Domanda:</strong> quante strade usano il termine "FRATELLI" (cancellando la presenza femminile)?
  E quante donne onorate hanno "MARIA" nel nome?<br>
  <strong>Keyword:</strong> <code>REGEX</code>, <code>FILTER</code>, <code>DISTINCT</code>, <code>ORDER BY</code></p>
  <pre class="code-block"><code>{sparql_highlight(Q4)}</code></pre>
  <h4>Risultati 4a (strade "Fratelli"):</h4>
  <div class="table-wrap"><table>
    <tr><th>?nomeVia</th><th>?nomePersona</th></tr>
    <tr><td>PASSAGGIO FRATELLI MARINCOLA</td><td>Fratelli Marincola (Giorgio e Isabella)</td></tr>
    <tr><td>VIA FRATELLI CERVI</td><td>Fratelli Cervi</td></tr>
    <tr><td>VIA FRATELLI ROSSELLI</td><td>Fratelli Rosselli</td></tr>
    <tr><td>VIA FRATELLI DANDOLO</td><td>Fratelli Dandolo</td></tr>
  </table></div>
  <p style="font-size:0.88rem;color:var(--text-muted)">Il caso di Isabella Marincola è emblematico:
  una staffetta partigiana afrodiscendente resa invisibile dal sostantivo maschile "fratelli".</p>

  <h2>Query 5 — OPTIONAL: persone con più strade dedicate</h2>
  <p><strong>Domanda:</strong> ci sono personaggi a cui sono dedicate più strade?
  OPTIONAL mostra anche le persone con una sola strada (con <code>?nomeVia2</code> non valorizzato).<br>
  <strong>Keyword:</strong> <code>OPTIONAL</code>, <code>DISTINCT</code>, <code>FILTER</code>, <code>ORDER BY</code>, <code>LIMIT</code></p>
  <pre class="code-block"><code>{sparql_highlight(Q5)}</code></pre>
  <h4>Esempi di risultati:</h4>
  <div class="table-wrap"><table>
    <tr><th>?nomePersona</th><th>?genere</th><th>?nomeVia1</th><th>?nomeVia2</th></tr>
    <tr><td>Laura Bassi Veratti</td><td>Female</td><td>VIA LAURA BASSI</td><td>PIAZZA LAURA BASSI</td></tr>
    <tr><td>Ondina Valla</td><td>Female</td><td>VIA ONDINA VALLA</td><td><em>(non valorizzato)</em></td></tr>
    <tr><td>Giuseppe Garibaldi</td><td>Male</td><td>VIA GARIBALDI</td><td>PIAZZA GARIBALDI</td></tr>
  </table></div>
  <p style="font-size:0.88rem;color:var(--text-muted)">Laura Bassi è l'unica donna con sia una via che una piazza a lei dedicata a Bologna.</p>
</div>
''', active='sparql.html')

(DOCS / 'sparql.html').write_text(SPARQL, encoding='utf-8')
print('sparql.html ✓')

# ── llm.html ──────────────────────────────────────────────────────────────────

LLM_PAGE = page('LLM & Prompt', '''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>LLM &amp; Prompt Engineering</h1>
  <p>Tre tecniche di prompting, cinque modelli confrontati, e le sfide incontrate.</p>
</div>

<div class="section">
  <h2>Ruolo degli LLM nel progetto</h2>
  <p>I Large Language Models sono stati usati in due fasi distinte:</p>
  <ol>
    <li><strong>Classificazione di genere</strong> delle 1.960 strade (Male / Female / Toponimo),
    la parte più onerosa e soggetta a ambiguità.</li>
    <li><strong>Generazione di triple RDF</strong> per arricchire il KG con dati biografici
    e per costruire le proposte di intitolazione.</li>
  </ol>
  <p>In entrambe le fasi abbiamo applicato le tre tecniche di prompting standard e confrontato
  i risultati di cinque modelli diversi.</p>

  <h2>Tecnica 1 — Zero-shot Prompting</h2>
  <p>Il modello risponde senza esempi preliminari. Usato per classificazioni rapide di strade
  con nome inequivocabile.</p>

  <div class="prompt-label">Prompt</div>
  <div class="prompt-box">
    Classifica questa intitolazione stradale bolognese in una delle tre categorie:
    <strong>Male</strong> (persona maschile), <strong>Female</strong> (persona femminile),
    <strong>Toponimo</strong> (luogo, concetto, istituzione, famiglia).<br><br>
    Strada: <em>VIA LAURA BASSI</em><br>
    Rispondi con una sola parola.
  </div>
  <div class="prompt-label">Risposta (Claude, ChatGPT, Gemini)</div>
  <div class="response-box">Female</div>

  <div class="prompt-label">Prompt (caso ambiguo)</div>
  <div class="prompt-box">
    Classifica questa intitolazione stradale bolognese: <em>VIA VITTORIA</em><br>
    Rispondi con una sola parola: Male, Female, o Toponimo.
  </div>
  <div class="prompt-label">Risposta variabile tra modelli</div>
  <div class="response-box">
    <strong>ChatGPT:</strong> Female (confonde con persona)<br>
    <strong>Claude:</strong> Toponimo (riconosce che si riferisce a un concetto astratto)<br>
    <strong>Gemini:</strong> Toponimo<br>
    <strong>DeepSeek:</strong> Female<br>
    <strong>Copilot:</strong> Toponimo
  </div>

  <h2>Tecnica 2 — Few-shot Prompting</h2>
  <p>Prima di fare la domanda principale, si forniscono esempi di input-output.
  Aumenta significativamente la coerenza su casi ambigui e nomi di famiglia.</p>

  <div class="prompt-label">Prompt</div>
  <div class="prompt-box">
    Classifica le intitolazioni stradali bolognesi in Male, Female o Toponimo.<br>
    Esempi:<br>
    VIA DANTE → Male (poeta, uomo)<br>
    VIA LAURA BASSI → Female (fisica, donna)<br>
    VIA DRAPPERIE → Toponimo (mestiere)<br>
    VIA ACHILLINI → Toponimo (nome di famiglia)<br>
    VIA FRATELLI CERVI → Male (collettivo maschile, uomini)<br><br>
    Ora classifica: <em>VIA CARRACCI</em>
  </div>
  <div class="prompt-label">Risposta (tutti i modelli)</div>
  <div class="response-box">
    Toponimo — la Via Carracci si riferisce alla famiglia di pittori bolognesi (Annibale, Agostino, Ludovico),
    non a un singolo individuo identificabile.
  </div>

  <h2>Tecnica 3 — Chain-of-Thought (CoT)</h2>
  <p>Si chiede al modello di ragionare esplicitamente prima di rispondere.
  Usata per i casi più complessi e per la generazione di triple RDF.</p>

  <div class="prompt-label">Prompt (classificazione)</div>
  <div class="prompt-box">
    Devi classificare questa strada bolognese: <em>PASSAGGIO FRATELLI MARINCOLA</em><br><br>
    Ragiona passo per passo:<br>
    1. A chi è dedicata questa strada?<br>
    2. Di che genere sono i referenti storici?<br>
    3. Il nome grammaticale suggerisce un genere specifico?<br>
    4. Qual è la classificazione corretta?
  </div>
  <div class="prompt-label">Risposta (Claude)</div>
  <div class="response-box">
    1. Il Passaggio Fratelli Marincola è dedicato a Giorgio e Isabella Marincola,
    fratello e sorella partigiani afrodiscendenti attivi nella Resistenza italiana.<br>
    2. I referenti storici sono uno di genere maschile (Giorgio) e una di genere femminile (Isabella).<br>
    3. Il termine "Fratelli" è grammaticalmente maschile, anche quando include donne —
    è il maschile inclusivo italiano, che cancella la presenza femminile.<br>
    4. Classificazione: <strong>Male</strong>, in base alla denominazione ufficiale.
    Nota: questa scelta rende invisibile Isabella Marincola, che merita riconoscimento esplicito.
  </div>

  <div class="prompt-label">Prompt (generazione RDF)</div>
  <div class="prompt-box">
    Usando le ontologie CLV (<code>https://w3id.org/italia/onto/CLV/</code>) e
    CPV (<code>https://w3id.org/italia/onto/CPV/</code>),
    genera le triple RDF in formato Turtle per questa intitolazione:<br><br>
    Strada: VIA LAURA BASSI<br>
    Persona: Laura Bassi Veratti, fisica e accademica, 1711–1778, Bologna<br>
    Genere: Female<br><br>
    Pensa prima alla struttura del grafo, poi scrivi il Turtle.
  </div>
  <div class="prompt-label">Risposta (Claude)</div>
  <div class="response-box">
<pre style="font-size:0.85rem;line-height:1.5">@prefix clv: &lt;https://w3id.org/italia/onto/CLV/&gt; .
@prefix cpv: &lt;https://w3id.org/italia/onto/CPV/&gt; .

&lt;https://w3id.org/bologna/resource/street/via-laura-bassi&gt;
    a clv:Street ;
    clv:hasStreetName "VIA LAURA BASSI" ;
    clv:isDedicatedTo &lt;https://w3id.org/bologna/resource/person/laura-bassi&gt; .

&lt;https://w3id.org/bologna/resource/person/laura-bassi&gt;
    a cpv:Person ;
    cpv:fullName "Laura Bassi Veratti" ;
    cpv:sex "Female" .</pre>
  </div>

  <h2>Confronto tra modelli</h2>
  <div class="table-wrap"><table class="llm-table">
    <tr>
      <th>Aspetto</th>
      <th>Claude</th>
      <th>ChatGPT</th>
      <th>Gemini</th>
      <th>DeepSeek</th>
      <th>Copilot</th>
    </tr>
    <tr>
      <td>Classificazioni zero-shot accurate</td>
      <td class="check">✓ Alta</td>
      <td class="check">✓ Alta</td>
      <td class="partial">~ Media</td>
      <td class="partial">~ Media</td>
      <td class="partial">~ Media</td>
    </tr>
    <tr>
      <td>Gestione nomi ambigui (es. Vittoria, Serena)</td>
      <td class="check">✓ Corretto</td>
      <td class="cross">✗ Confonde</td>
      <td class="check">✓ Corretto</td>
      <td class="cross">✗ Confonde</td>
      <td class="check">✓ Corretto</td>
    </tr>
    <tr>
      <td>Generazione Turtle RDF con ontologie corrette</td>
      <td class="check">✓ Ottima</td>
      <td class="partial">~ Buona</td>
      <td class="partial">~ Buona</td>
      <td class="partial">~ Discreta</td>
      <td class="partial">~ Buona</td>
    </tr>
    <tr>
      <td>Ragionamento esplicito (CoT)</td>
      <td class="check">✓ Dettagliato</td>
      <td class="check">✓ Buono</td>
      <td class="partial">~ Superficiale</td>
      <td class="partial">~ Superficiale</td>
      <td class="partial">~ Medio</td>
    </tr>
    <tr>
      <td>Sensibilità alle questioni di genere</td>
      <td class="check">✓ Alta</td>
      <td class="check">✓ Alta</td>
      <td class="partial">~ Media</td>
      <td class="cross">✗ Bassa</td>
      <td class="partial">~ Media</td>
    </tr>
    <tr>
      <td>Conoscenza storia locale bolognese</td>
      <td class="partial">~ Media</td>
      <td class="partial">~ Media</td>
      <td class="partial">~ Media</td>
      <td class="cross">✗ Scarsa</td>
      <td class="partial">~ Media</td>
    </tr>
  </table></div>

  <h2>Sfide e soluzioni</h2>
  <div class="card-grid">
    <div class="card">
      <h3>Nomi ambigui di genere</h3>
      <p><em>Via Vittoria</em>, <em>Via Serena</em>, <em>Via Letizia</em> sono nomi femminili ma
      si riferiscono a concetti astratti o eventi storici. I modelli zero-shot li classificano
      spesso come Female.</p>
      <p><strong>Soluzione:</strong> few-shot prompting con esempi di questi pattern;
      validazione manuale di tutti i casi dubbi.</p>
    </div>
    <div class="card">
      <h3>Soprannomi storici</h3>
      <p><em>Via Dante</em>, <em>Via Donatello</em>, <em>Via Caravaggio</em>:
      il modello deve sapere che si tratta di persone reali, non di concetti.</p>
      <p><strong>Soluzione:</strong> few-shot con esempi di artisti, scrittori e poeti italiani
      noti per soprannome.</p>
    </div>
    <div class="card">
      <h3>Allucinazioni sui QID Wikidata</h3>
      <p>Chiedendo agli LLM i codici Wikidata (QID) delle persone, i modelli spesso
      inventavano QID plausibili ma errati (es. Q1064 restituito come Carducci era Manzoni).</p>
      <p><strong>Soluzione:</strong> ricerca programmatica via API Wikidata
      (<code>wbsearchentities</code>) senza passare per LLM per i QID.</p>
    </div>
    <div class="card">
      <h3>Rate limiting Wikidata</h3>
      <p>L'API Wikidata impone limiti alle richieste ravvicinate. Alcune ricerche
      restituivano risultati vuoti per throttling.</p>
      <p><strong>Soluzione:</strong> aggiunto attesa tra le richieste (<code>time.sleep()</code>)
      e sistema di cache locale in <code>wikidata_cache.json</code>.</p>
    </div>
    <div class="card">
      <h3>Identità transgender</h3>
      <p>Marcella Di Folco (1943–2010) è nata con un nome maschile ma ha vissuto come donna.
      Wikidata la classifica in modo inconsistente tra le versioni.</p>
      <p><strong>Soluzione:</strong> classificazione manuale come <em>Female</em>,
      rispettando l'identità autodichiarata, con documentazione esplicita nella
      <a href="https://github.com/lauratonsi/PROGETTO_KNOWLEDGE_GRAPH/blob/classificazioni-corrette/NOTE_METODOLOGICHE.md" target="_blank">nota metodologica</a>.</p>
    </div>
    <div class="card">
      <h3>Figure locali non su Wikidata</h3>
      <p>~15 persone di rilevanza puramente locale (es. Vittorio Sabena, Don Giuseppe Nozzi,
      Carlo Pelagalli) non erano documentate su Wikidata.</p>
      <p><strong>Soluzione:</strong> ricerca manuale su ANPI Bologna,
      Storia e Memoria di Bologna, archivi parrocchiali e segnalazioni del gruppo di ricerca.</p>
    </div>
  </div>
</div>
''', active='llm.html')

(DOCS / 'llm.html').write_text(LLM_PAGE, encoding='utf-8')
print('llm.html ✓')

# ── results.html ──────────────────────────────────────────────────────────────

RESULTS = page('Risultati', f'''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>Risultati</h1>
  <p>Visualizzazioni del divario di genere e classificazione professionale delle 1.192 persone nel KG.</p>
</div>

<div class="section">
  <h2>Il divario in numeri</h2>
  <div class="stat-grid">
    <div class="stat-box stat-male"><div class="number">{N_MALE}</div><div class="label">Strade maschili</div></div>
    <div class="stat-box stat-female"><div class="number">{N_FEMALE}</div><div class="label">Strade femminili</div></div>
    <div class="stat-box stat-topo"><div class="number">{N_TOPO}</div><div class="label">Toponimi</div></div>
    <div class="stat-box stat-pct"><div class="number">{PCT_F}%</div><div class="label">Quota femminile</div></div>
  </div>

  <h2>Distribuzione strade per genere</h2>
  <div class="chart-wrap" style="max-width:400px">
    <canvas id="donutChart"></canvas>
  </div>

  <h2>Categorie professionali per genere</h2>
  <p>Confronto tra la distribuzione per categoria professionale degli uomini onorati (1.091),
  delle donne storicamente onorate (67) e delle donne proposte (34).
  I dati rivelano pattern significativi: le donne già onorate sono concentrate
  nello spettacolo (25,4%), mentre le proposte correggono questo squilibrio con
  un forte peso della Resistenza (32,4%) e dell'attivismo civile (17,6%).</p>
  <div class="chart-wrap-full">
    <canvas id="barChart"></canvas>
  </div>

  <h2>Strade dedicate a donne (123 intitolazioni a persone)</h2>
  <p>Tabella filtrabile delle strade bolognesi intitolate a donne identificate.
  Escluse le intitolazioni a sante, nomi generici e nominativi non individuali (157 totali nel dataset del Comune).</p>

  <div style="display:flex;flex-wrap:wrap;gap:0.8rem;align-items:center;margin-bottom:1rem">
    <input type="text" id="search-box" placeholder="Cerca nome, professione, quartiere…">
    <div class="filters" id="tfilters">
      <button class="filter-btn active" data-f="">Tutte</button>
      <button class="filter-btn" data-f="Via">Solo Vie</button>
      <button class="filter-btn" data-f="Piazza">Piazze</button>
    </div>
  </div>

  <div class="table-wrap">
    <table id="women-table">
      <thead><tr>
        <th>Intitolazione</th>
        <th>Nome completo</th>
        <th>Professione</th>
        <th>Dati anagrafici</th>
        <th>Anno</th>
        <th>Quartiere</th>
      </tr></thead>
      <tbody id="women-tbody"></tbody>
    </table>
  </div>
  <p id="women-count" style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem"></p>
</div>

<div class="section">
  <h2>Grafici — Gender Gap</h2>
  <p>Visualizzazioni statiche del divario di genere nella toponomastica bolognese.</p>
  <div class="grafici-grid">
    <figure>
      <img src="grafici_gender_gap/01_gender_gap_globale.png" alt="Gender gap globale" loading="lazy">
      <figcaption>Distribuzione globale Male / Female / Toponimo</figcaption>
    </figure>
    <figure>
      <img src="grafici_gender_gap/02_distribuzione_quartieri.png" alt="Distribuzione per quartiere" loading="lazy">
      <figcaption>Distribuzione del gender gap per quartiere</figcaption>
    </figure>
    <figure>
      <img src="grafici_gender_gap/03_evoluzione_storica.png" alt="Evoluzione storica" loading="lazy">
      <figcaption>Evoluzione storica delle intitolazioni femminili</figcaption>
    </figure>
    <figure>
      <img src="grafici_gender_gap/04_lunghezza_strade.png" alt="Lunghezza strade" loading="lazy">
      <figcaption>Lunghezza media delle strade per genere dell'intitolazione</figcaption>
    </figure>
  </div>

  <h2>Grafici — Classificazione Professionale</h2>
  <p>Confronto tra le macro-categorie professionali degli uomini, delle donne storiche e delle candidature proposte.</p>
  <div class="grafici-grid">
    <figure>
      <img src="grafici_professioni_rivisti/01_divario_storico_categorie.png" alt="Divario storico per categorie" loading="lazy">
      <figcaption>Divario di genere per categoria professionale (persone storiche)</figcaption>
    </figure>
    <figure>
      <img src="grafici_professioni_rivisti/02_focus_nuove_proposte.png" alt="Focus nuove proposte" loading="lazy">
      <figcaption>Distribuzione professionale delle 34 proposte di intitolazione</figcaption>
    </figure>
    <figure>
      <img src="grafici_professioni_rivisti/03_top_professioni_femminili.png" alt="Top professioni femminili" loading="lazy">
      <figcaption>Principali categorie nelle strade già dedicate a donne</figcaption>
    </figure>
  </div>
</div>
''', active='results.html',
extra_head='<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>',
extra_js=f'''<script>
const WOMEN = {WOMEN_JS};
const CAT_LABELS = {CAT_LABELS_JS};
const M_DATA = {M_DATA_JS};
const F_DATA = {F_DATA_JS};
const P_DATA = {P_DATA_JS};

// Donut chart
new Chart(document.getElementById('donutChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['Uomini (1066)', 'Donne (66)', 'Toponimi (828)'],
    datasets: [{{ data: [1066, 66, 828],
      backgroundColor: ['#1b3a6b','#8b1a4a','#9e9e9e'],
      borderWidth: 2, borderColor: '#fff'
    }}]
  }},
  options: {{ plugins: {{ legend: {{ position: 'bottom' }} }}, cutout: '60%' }}
}});

// Bar chart
new Chart(document.getElementById('barChart'), {{
  type: 'bar',
  data: {{
    labels: CAT_LABELS,
    datasets: [
      {{ label: 'Uomini storici %', data: M_DATA, backgroundColor: 'rgba(27,58,107,0.8)' }},
      {{ label: 'Donne storiche %', data: F_DATA, backgroundColor: 'rgba(139,26,74,0.8)' }},
      {{ label: 'Proposte %',       data: P_DATA, backgroundColor: 'rgba(26,107,58,0.8)' }},
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ ticks: {{ maxRotation: 35, font: {{ size: 11 }} }} }},
      y: {{ beginAtZero: true, title: {{ display: true, text: '% sul totale del gruppo' }} }}
    }}
  }}
}});

// Women table
const tbody = document.getElementById('women-tbody');
const countEl = document.getElementById('women-count');
let activeFilter = '';
let searchVal = '';

function renderTable() {{
  const q = searchVal.toLowerCase();
  const rows = WOMEN.filter(w => {{
    const matchSearch = !q || [w.nome,w.label,w.professione,w.quartiere,w.dati]
      .some(s => s.toLowerCase().includes(q));
    const matchFilter = !activeFilter || w.tipologia.includes(activeFilter);
    return matchSearch && matchFilter;
  }});
  tbody.innerHTML = rows.map(w => `<tr>
    <td><strong>${{w.label}}</strong></td>
    <td>${{w.nome}}</td>
    <td>${{w.professione}}</td>
    <td>${{w.dati}}</td>
    <td>${{w.anno}}</td>
    <td>${{w.quartiere}}</td>
  </tr>`).join('');
  countEl.textContent = `${{rows.length}} / ${{WOMEN.length}} intitolazioni visualizzate`;
}}

document.getElementById('search-box').addEventListener('input', e => {{
  searchVal = e.target.value; renderTable();
}});
document.querySelectorAll('#tfilters .filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#tfilters .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.f; renderTable();
  }});
}});
renderTable();
</script>''')

(DOCS / 'results.html').write_text(RESULTS, encoding='utf-8')
print('results.html ✓')

# ── proposals.html ────────────────────────────────────────────────────────────

N_ACTIVE = sum(1 for p in proposals if p['stato']=='attiva')
N_FUTURE = sum(1 for p in proposals if p['stato']=='futura')

PROPOSALS_PAGE = page('Proposte', f'''
<div class="hero" style="padding:3.5rem 1.5rem 3rem">
  <h1>Proposte di Intitolazione</h1>
  <p>{N_ACTIVE} candidature attive e {N_FUTURE} future per nuove strade a donne,
  persone trans e non binarie con un legame con Bologna o rilevanza nazionale.</p>
</div>

<div class="section">
  <div class="info-box">
    <strong>Criteri di ammissibilità (D.P.R. 223/1989):</strong>
    Le strade possono essere intitolate a persone decedute da almeno <strong>10 anni</strong>.
    Le proposte <em>attive</em> soddisfano questo requisito; le proposte <em>future</em>
    riguardano persone ancora in vita, decedute di recente, o con data di morte incerta.
  </div>

  <div class="stat-grid" style="margin-bottom:2rem">
    <div class="stat-box"><div class="number" style="color:var(--green)">{N_ACTIVE}</div><div class="label">Proposte attive</div></div>
    <div class="stat-box"><div class="number" style="color:var(--amber)">{N_FUTURE}</div><div class="label">Proposte future</div></div>
    <div class="stat-box"><div class="number" style="color:var(--primary)">{N_ACTIVE+N_FUTURE}</div><div class="label">Totale candidature</div></div>
  </div>

  <h2>Filtra le proposte</h2>
  <div class="filters" id="state-filters">
    <button class="filter-btn active" data-stato="">Tutte</button>
    <button class="filter-btn" data-stato="attiva">Solo attive</button>
    <button class="filter-btn" data-stato="futura">Solo future</button>
  </div>
  <div class="filters" id="cat-filters">
    <button class="filter-btn active" data-cat="">Tutte le categorie</button>
    <button class="filter-btn" data-cat="Resistenza e antifascismo">Resistenza</button>
    <button class="filter-btn" data-cat="Sindacalismo e attivismo civile">Attivismo</button>
    <button class="filter-btn" data-cat="Scienze e medicina">Scienze</button>
    <button class="filter-btn" data-cat="Arte visiva e architettura">Arte</button>
    <button class="filter-btn" data-cat="Politica e diritto">Politica</button>
    <button class="filter-btn" data-cat="Istruzione ed educazione">Istruzione</button>
  </div>

  <p id="prop-count" style="font-size:0.85rem;color:var(--text-muted);margin:0.5rem 0 1rem"></p>
  <div class="card-grid" id="proposals-grid"></div>
</div>
''', active='proposals.html',
extra_js=f'''<script>
const PROPOSALS = {PROPOSALS_JS};
let statoFilter = '';
let catFilter = '';

function renderProps() {{
  const grid = document.getElementById('proposals-grid');
  const filtered = PROPOSALS.filter(p =>
    (!statoFilter || p.stato === statoFilter) &&
    (!catFilter || p.categoria === catFilter)
  );
  document.getElementById('prop-count').textContent =
    `${{filtered.length}} / ${{PROPOSALS.length}} proposte visualizzate`;

  grid.innerHTML = filtered.map(p => {{
    const badgeClass = p.stato === 'attiva' ? 'badge-active' : 'badge-future';
    const badgeText = p.stato === 'attiva' ? 'Attiva' : 'Futura';
    const cardClass = p.stato === 'futura' ? 'card future' : 'card';
    const eleg = p.eleggibile && p.eleggibile !== '' ?
      `<p class="card-meta">Eleggibile dal: ${{p.eleggibile}}</p>` : '';
    const fonte = p.fonte && p.fonte.startsWith('http') ?
      `<p class="card-fonte"><a href="${{p.fonte}}" target="_blank">Fonte →</a></p>` : '';
    return `<div class="${{cardClass}}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem">
        <h3>${{p.nome}}</h3>
        <span class="badge ${{badgeClass}}">${{badgeText}}</span>
      </div>
      <p class="card-meta">${{p.categoria}}</p>
      <p><strong>${{p.professione.split(';')[0]}}</strong></p>
      <p>🗓 ${{p.nascita}} — ${{p.morte}}</p>
      <p style="font-size:0.87rem;color:var(--text-muted)">${{p.punti}}</p>
      ${{eleg}}
      <p style="font-size:0.84rem"><em>Legame con Bologna:</em> ${{p.legame}}</p>
      ${{fonte}}
    </div>`;
  }}).join('');
}}

document.querySelectorAll('#state-filters .filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#state-filters .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); statoFilter = btn.dataset.stato; renderProps();
  }});
}});
document.querySelectorAll('#cat-filters .filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('#cat-filters .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); catFilter = btn.dataset.cat; renderProps();
  }});
}});
renderProps();
</script>''')

(DOCS / 'proposals.html').write_text(PROPOSALS_PAGE, encoding='utf-8')
print('proposals.html ✓')

print('\nSite built successfully in docs/')
print(f'Files: {", ".join(p.name for p in sorted(DOCS.iterdir()))}')
