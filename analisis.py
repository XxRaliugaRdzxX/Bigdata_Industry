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

print("\nEn total hay el número de plantas de:")
n_plantas = df['planta'].nunique()
print(n_plantas)

promedio = df.groupby('planta')['temperatura_c'].mean().reset_index()
print("\nEl promedio de las plantas es:", promedio)

print("\nEl registro con la temperatura más alta detectada fue:")
temperatura_max = df['temperatura_c'].idxmax()
print("Registro:",temperatura_max)

print("\nDatos de la fila con la temperatura más alta detectada")
datos_temperatura_max = df.loc[temperatura_max]
sensor_max = datos_temperatura_max['id_sensor']
sensor_fecha = datos_temperatura_max['fecha_hora']
print("El sensor que registro la temperatura más alta fue:", sensor_max)
print("La fecha cuando el sensor detecto la temperatura más alta fue:", sensor_fecha)

print("\nLecturas registradas mayores a 85 °C")
lim = 85
lect_tem = (df['temperatura_c'] > lim).sum()
print(lect_tem)

print("\nPlanta con más alertas detectadas")
alertas = df[df['temperatura_c']> lim]
conteo_alertas = alertas.groupby('planta')['temperatura_c'].count()

planta_con_mas_alertas = conteo_alertas.idxmax()
total_alertas = conteo_alertas.max()

print("\nLa sucursal con más alertas es la sucursal:", planta_con_mas_alertas)
print("\nCon un total de:", total_alertas)

alertas.to_csv('resultados/alertas.csv', index=False)