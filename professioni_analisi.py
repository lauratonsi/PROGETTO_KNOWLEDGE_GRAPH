import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configurazione ambiente grafico
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
cartella_output = "grafici_professioni_rivisti"
os.makedirs(cartella_output, exist_ok=True)

# Caricamento del dataset
df = pd.read_csv('classificazione_professioni.csv')

# Filtri logici
df_storica = df[df['tipo'] == 'storica']
df_proposte = df[df['tipo'] == 'proposta']
df_femminile = df[df['genere'] == 'F']

colori_genere = {'M': '#3498db', 'F': '#e74c3c'}

# 1. Divario Storico Esistente per Macro Categoria
plt.figure(figsize=(12, 8))
sns.countplot(
    data=df_storica, 
    y='macro_categoria', 
    hue='genere', 
    palette=colori_genere, 
    order=df_storica['macro_categoria'].value_counts().index
)
plt.title('Divario di Genere Storico per Macro Categoria', weight='bold')
plt.xlabel('Numero di Entità (Solo Vie Esistenti)')
plt.ylabel('Macro Categoria')
plt.legend(title='Genere', loc='lower right')
plt.savefig(f'{cartella_output}/01_divario_storico_categorie.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Focus sulle Nuove Proposte (Tutte Femminili)
plt.figure(figsize=(10, 6))
sns.countplot(
    data=df_proposte, 
    y='macro_categoria', 
    color='#2ecc71', 
    order=df_proposte['macro_categoria'].value_counts().index
)
plt.title('Ambiti Professionali delle Nuove Proposte (100% Femminili)', weight='bold')
plt.xlabel('Numero di Proposte')
plt.ylabel('Macro Categoria')
plt.savefig(f'{cartella_output}/02_focus_nuove_proposte.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Top 15 Professioni Specifiche (Solo Donne: Storiche + Proposte)
plt.figure(figsize=(10, 8))
sns.countplot(
    data=df_femminile, 
    y='professione_originale', 
    color='#e74c3c',
    order=df_femminile['professione_originale'].value_counts().head(15).index
)
plt.title('Top 15 Professioni (Figure Femminili Totali)', weight='bold')
plt.xlabel('Frequenza')
plt.ylabel('Professione Originale')
plt.savefig(f'{cartella_output}/03_top_professioni_femminili.png', dpi=300, bbox_inches='tight')
plt.close()

# Report testuale
print("--- METRICHE AGGIORNATE: PROFESSIONI ---")
print(f"Entità storiche analizzate: {len(df_storica)}")
print(f"Nuove proposte femminili inserite: {len(df_proposte)}")
print("\nRipartizione delle Proposte per Categoria:")
print(df_proposte['macro_categoria'].value_counts().to_string())
print(f"\nNuovi grafici salvati nella cartella: '{cartella_output}'")