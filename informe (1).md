# Informe: Las 5 V aplicadas al proyecto de sensores industriales

## 5. Las 5 V aplicadas al proyecto

Las cifras de esta tabla salen de ejecutar el análisis sobre `sensores_industriales.csv`. Las columnas del archivo son `id_registro`, `fecha_hora`, `id_sensor`, `planta`, `temperatura_c` y `vibracion_mm_s`.

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación futura? |
|---|---|---|---|
| **Volumen** | Cada lectura de cada sensor genera un registro nuevo, así que el tamaño crece de forma lineal con el número de sensores y el tiempo. El archivo actual tiene 100,000 registros y pesa unos 4.6 MB, que aún se maneja bien con `pandas` en una sola máquina. Si el sistema siguiera 30 días con los mismos 40 sensores, serían unos 1.7 millones de filas (proyección: 40 sensores × 1,440 min × 30 días). | El CSV contiene **100,000 registros** de **40 sensores** repartidos en 4 plantas (10 por planta), con exactamente 2,500 lecturas por sensor. | **CSV actual.** La proyección a 30 días es una estimación y no está en el archivo. |
| **Velocidad** | Los sensores reportan de forma periódica y las alertas de temperatura pierden valor si se detectan tarde. En el archivo, cada sensor registra una lectura **cada 60 segundos**, sin huecos. Con 40 sensores, entran 40 lecturas por minuto (2,400 por hora). | S001 genera una lectura por minuto desde el 01/09/26 00:00. Las 2,500 marcas de tiempo distintas cubren de forma continua 1 día y 17 h 39 min (hasta el 02/09/26 17:39). | **CSV actual** para la frecuencia de muestreo (1 lectura/min por sensor). **Ampliación futura** para la ingesta en tiempo real: el archivo es un lote histórico y no un flujo (*streaming*). |
| **Variedad** | El sistema mide dos magnitudes físicas distintas (temperatura y vibración) y se organiza por planta y sensor. Todo el archivo es **estructurado y tabular**: 1 identificador, 1 fecha en texto, 2 columnas categóricas (`id_sensor`, `planta`) y 2 numéricas. El archivo no tiene datos semiestructurados ni no estructurados. | Fotos de cámaras termográficas, bitácoras de mantenimiento en texto libre o lecturas de presión y humedad en formato JSON, combinadas con las lecturas actuales de temperatura y vibración. | **Ampliación futura.** Ninguno de esos tipos de dato aparece en el CSV actual. |
| **Veracidad** | Es la confiabilidad de lo medido: una lectura errónea genera falsas alarmas o deja pasar fallas reales. En este archivo no hay nulos ni registros duplicados, y los valores están en rangos físicamente plausibles. Hay dos puntos a vigilar. La fecha viene como **texto `dd/mm/aa hh:mm`**, y `pandas` la interpretó mal al leerla sin indicar el formato. El archivo tampoco trae una columna que indique si el sensor estaba calibrado o falló. | 0 valores nulos en las 6 columnas, 0 `id_registro` duplicados, temperatura entre 45.00 y 104.99 °C, vibración entre 0.50 y 5.50 mm/s. Cada `id_sensor` pertenece a una sola planta. | **CSV actual** para las verificaciones anteriores. Un indicador de calibración o estado del sensor sería **ampliación futura**. |
| **Valor** | El valor está en convertir lecturas en decisiones: detectar sobrecalentamientos, comparar plantas y priorizar inspecciones. Con el umbral de 85 °C usado en el análisis, el sistema ya puede señalar dónde actuar primero. | **6,954 lecturas superan 85 °C (6.95 %)**. Planta_3 tiene más alertas (1,777), seguida de Planta_1 (1,737), Planta_4 (1,732) y Planta_2 (1,708). La lectura máxima fue **104.99 °C**, registrada por el sensor **S023** (Planta_3) el 01/09/26 a las 22:23. | **CSV actual** para el conteo de alertas. El **mantenimiento predictivo**, que cruzaría temperatura y vibración con el historial de fallas, es **ampliación futura**: el archivo no trae fallas registradas. |

> Nota: el umbral de 85 °C viene del código del análisis, no del archivo. Las diferencias entre plantas son pequeñas (el promedio de temperatura va de 66.53 a 66.77 °C), así que con estos datos no se puede afirmar que una planta esté realmente peor que otra.

## 6. Tipos de datos y procesamiento tradicional

### Clasificación de los elementos

| Elemento | Clasificación | Justificación |
|---|---|---|
| El CSV de sensores | **Estructurado** | Tiene un esquema fijo y conocido: 6 columnas, cada una con un tipo definido (`id_registro` entero, `temperatura_c` y `vibracion_mm_s` decimales, `id_sensor` y `planta` categóricas, `fecha_hora` texto con formato fijo). Cada fila tiene los mismos campos y se puede consultar directamente con `pandas` o SQL. |
| Un mensaje JSON enviado por un sensor | **Semiestructurado** | Trae etiquetas clave-valor que describen sus propios datos, pero no obliga a un esquema rígido: pueden variar los campos de un mensaje a otro o venir anidados (por ejemplo, un objeto `lecturas` dentro del mensaje). Hay que interpretarlo antes de pasarlo a una tabla. |
| Una fotografía de una máquina | **No estructurado** | Es una matriz de píxeles sin campos ni columnas. La información útil (una grieta, un cambio de color o una fuga) solo se obtiene con técnicas de visión por computadora. |
| El texto libre de un reporte de mantenimiento | **No estructurado** | Está en lenguaje natural, sin formato fijo. Para extraer datos como la máquina afectada o la causa de la falla se necesita procesamiento de lenguaje natural o lectura manual. |

Que `fecha_hora` esté guardada como texto no hace semiestructurado al CSV: el archivo sigue teniendo un esquema fijo, y solo hay que indicar el formato al convertirla a fecha.

### Por qué 100,000 registros no convierten el archivo en Big Data

Big Data no se define por un número de filas. Se define porque el volumen, la velocidad y la variedad juntos superan lo que las herramientas tradicionales (un script y una sola máquina) pueden manejar. El archivo actual no cumple esas condiciones:

- **Volumen pequeño:** los 100,000 registros pesan unos 4.6 MB (unos 46 bytes por registro). Cabe sin problema en la memoria de una laptop y `pandas` lo carga y agrupa en una sola máquina.
- **Velocidad baja:** es un archivo histórico que se lee completo de una vez, no un flujo continuo. Entran 40 lecturas por minuto, una tasa que un proceso simple absorbe.
- **Variedad nula:** todo es tabular y estructurado, sin JSON, imágenes ni texto libre.
- **El análisis ya está resuelto con herramientas tradicionales:** el conteo de registros, el promedio por planta, el máximo y las alertas se calculan con un `groupby` en un solo script.

### Limitaciones que aparecerían al aumentar la escala

Las cifras de esta tabla son proyecciones que usan los ~46 bytes por registro del archivo actual, con una lectura por minuto por sensor.

| Escenario (proyección) | Filas | Tamaño aproximado del CSV |
|---|---|---|
| Los 40 sensores actuales durante 30 días | 1,728,000 | ~80 MB |
| Los 40 sensores durante 1 año | 21,024,000 | ~1 GB |
| 4,000 sensores durante 1 día | 5,760,000 | ~270 MB |
| 4,000 sensores durante 1 año | 2,102,400,000 | ~97 GB |

Con esos tamaños empezarían estas limitaciones:

1. **Memoria RAM:** `pandas` carga todo el archivo en memoria, y en memoria suele ocupar más que en disco, sobre todo con columnas de texto. Con decenas de GB el script se vuelve lento o falla por falta de memoria.
2. **Una sola máquina:** el procesamiento no se reparte entre varios equipos. Al crecer los datos, cada análisis tarda más y no se puede ampliar solo agregando nodos.
3. **Sin consultas eficientes:** un CSV no tiene índices, así que cada consulta recorre todo el archivo. También se pierde la lectura concurrente y el control de acceso que ofrece una base de datos.
4. **No sirve para tiempo real:** el script se corre a mano sobre un archivo cerrado. Detectar un sobrecalentamiento al momento requeriría ingesta continua (*streaming*), no leer el CSV completo cada vez.
5. **No soporta otros tipos de dato:** un CSV no almacena JSON anidado, fotografías ni reportes de texto. Esos datos requieren otro almacenamiento (por ejemplo, un *data lake* o una base de datos documental) y técnicas de análisis distintas.
6. **Calidad de datos más difícil de vigilar:** con millones de filas por día, revisar a mano los nulos, los duplicados o las fechas mal interpretadas ya no es viable y hay que automatizarlo.

Para ese punto se suelen usar formatos columnares (como Parquet), bases de datos de series de tiempo y procesamiento distribuido (como Spark).

## Resultados del análisis usados en el informe

| Métrica | Resultado |
|---|---|
| Registros | 100,000 |
| Sensores distintos | 40 |
| Plantas | 4 |
| Temperatura promedio por planta | Planta_1: 66.62 °C, Planta_2: 66.53 °C, Planta_3: 66.77 °C, Planta_4: 66.67 °C |
| Registro con la temperatura más alta | Fila 53742 (índice de `pandas`), `id_registro` 53743 |
| Sensor y fecha de ese registro | S023, 01/09/26 22:23 |
| Lecturas con temperatura > 85 °C | 6,954 |
| Planta con más alertas | Planta_3, con 1,777 |

## Código complementario

Este bloque se puede añadir al final de tu script. No modifica nada de lo que ya hace y calcula lo que se usó en Veracidad y Velocidad.

```python
# --- Complemento para las 5 V ---
print("\nValores nulos por columna")
print(df.isna().sum())

print("\nRegistros duplicados (id_registro)")
print(df['id_registro'].duplicated().sum())

# Indicar el formato evita que pandas interprete mal día y mes
df['fecha'] = pd.to_datetime(df['fecha_hora'], format="%d/%m/%y %H:%M")
print("\nPeriodo cubierto:", df['fecha'].min(), "->", df['fecha'].max())

intervalo = df[df['id_sensor'] == 'S001']['fecha'].diff().dropna().median()
print("Intervalo entre lecturas de un sensor:", intervalo)
```
