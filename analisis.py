#importar librerias
import matplotlib as mlp
import pandas as pd

#definir ruta
ruta_csv = "data/sensores_industriales.csv"

# Leer el archivo en un dataframe
df = pd.read_csv (ruta_csv)

# mostrar las primeras filas
print(df.head(10))

df.info()
