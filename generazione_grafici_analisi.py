import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Impostazione dello stile grafico per i plot
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
cartella_output = "grafici_gender_gap"
os.makedirs(cartella_output, exist_ok=True)

# Caricamento del dataset
df = pd.read_csv('bologna_KG_ready.csv', sep=',')

# Pulizia e preparazione dati
df['DATA_ISTIT'] = pd.to_datetime(df['DATA_ISTIT'], errors='coerce')
df['ANNO_ISTIT'] = df['DATA_ISTIT'].dt.year

# 1. Analisi Globale: Proporzione del Gender Gap
gender_counts = df['GENERE'].value_counts()
plt.figure(figsize=(8, 8))
color_map = {'Male': '#3498db', 'Female': '#e74c3c', 'Toponimo': '#95a5a6'} # Adatta i codici se diversi nel tuo CSV
colors = [color_map.get(x, '#cccccc') for x in gender_counts.index]
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title('Distribuzione Toponomastica per Genere a Bologna', weight='bold')
plt.savefig(f'{cartella_output}/01_gender_gap_globale.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Analisi Spaziale: Distribuzione per Quartiere
plt.figure(figsize=(12, 7))
sns.countplot(data=df, y='Quartiere', hue='GENERE', palette=color_map, order=df['Quartiere'].value_counts().index)
plt.title('Impatto del Gender Gap per Quartiere', weight='bold')
plt.xlabel('Numero di Intitolazioni')
plt.ylabel('Quartiere')
plt.legend(title='Genere', loc='lower right')
plt.savefig(f'{cartella_output}/02_distribuzione_quartieri.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Analisi Temporale: Evoluzione delle intitolazioni femminili nel tempo
df_storico = df.dropna(subset=['ANNO_ISTIT'])
plt.figure(figsize=(14, 6))
sns.histplot(data=df_storico, x='ANNO_ISTIT', hue='GENERE', multiple="stack", bins=30, palette=color_map)
plt.title('Evoluzione Storica delle Intitolazioni Stradali (M vs F)', weight='bold')
plt.xlabel('Anno di Istituzione')
plt.ylabel('Frequenza')
plt.savefig(f'{cartella_output}/03_evoluzione_storica.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Analisi Urbanistica: Lunghezza media delle strade per genere
plt.figure(figsize=(8, 6))
sns.barplot(data=df, x='GENERE', y='LUNGHEZ', palette=color_map, errorbar=None)
plt.title('Lunghezza Media delle Strade per Genere', weight='bold')
plt.xlabel('Genere')
plt.ylabel('Lunghezza Media (metri)')
plt.savefig(f'{cartella_output}/04_lunghezza_strade.png', dpi=300, bbox_inches='tight')
plt.close()

# Report testuale a terminale
print("--- METRICHE KNOWLEDGE GRAPH: GENDER GAP BOLOGNA ---")
print(f"Totale archi stradali analizzati: {len(df)}")
print("\nConteggio assoluto per genere:")
print(gender_counts.to_string())
print("\nLunghezza media (metri) delle strade per genere:")
print(df.groupby('GENERE')['LUNGHEZ'].mean().round(2).to_string())
print(f"\nI grafici pronti per la pubblicazione web sono stati salvati nella cartella: '{cartella_output}'")