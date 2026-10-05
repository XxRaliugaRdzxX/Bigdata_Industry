#importar librerias
import matplotlib as mlp
import pandas as pd

#definir ruta
ruta_csv = "data/sensores_industriales.csv"

# Leer el archivo en un dataframe
df = pd.read_csv (ruta_csv)

# mostrar las primeras filas
#print(df.head(10))

print("Cantidad de registros")
matrix = df.shape[0]
print(matrix)

print("\nCantidad de sensores distintos")
sensores_unicos = df['id_sensor'].nunique()
print(sensores_unicos)

print("\nEl registro con la temperatura más alta detectada fue:")
temperatura_max = df['temperatura_c'].idxmax()
print("Registro:",temperatura_max)

print("\nDatos de la fila con la temperatura más alta detectada")
datos_temperatura_max = df.loc[temperatura_max]
sensor_max = datos_temperatura_max['id_sensor']
sensor_fecha = datos_temperatura_max['fecha_hora']
print("El sensor que registro la temperatura más alta fue:", sensor_max)
print("La fecha cuando el sensor detecto la temperatura más alta fue:", sensor_fecha)