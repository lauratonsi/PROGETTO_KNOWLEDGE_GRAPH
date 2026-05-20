import pandas as pd
df = pd.read_csv('bologna_entita_uniche.csv', sep=';')
df.to_csv('bologna_entita_uniche_comma.csv', sep=',', index=False)
exit()