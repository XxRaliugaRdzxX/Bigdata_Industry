#impportar librerias
import matplotlib as mlp
import pandas as pd

# Leer el archivo en un dataframe
df = pd.read_csv('sensores_industriales')

# mostrar las primeras filas
print(df.head())