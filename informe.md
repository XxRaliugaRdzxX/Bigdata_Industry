# Informe: Las 5 V aplicadas al proyecto de sensores industriales

## 5. Las 5 V aplicadas al proyecto

Las cifras de esta tabla salen de ejecutar el análisis sobre `sensores_industriales.csv`. Las columnas del archivo son `id_registro`, `fecha_hora`, `id_sensor`, `planta`, `temperatura_c` y `vibracion_mm_s`.

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación futura? |
|---|---|---|---|
| **Volumen** | Cada lectura de cada sensor genera un registro nuevo, asi que el tamaño crece de forma lineal con el numero de sensores y el tiempo. El archivo actual tiene 100,000 registros y pesa unos 4.6 MB, que aun se maneja bien con `pandas` en una sola maquina. Si el sistema siguiera 30 dias con los mismos 40 sensores, serian unos 1.7 millones de filas (proyeccion: 40 sensores × 1,440 min × 30 dias). | El CSV contiene **100,000 registros** de **40 sensores** repartidos en 4 plantas (10 por planta), con exactamente 2,500 lecturas por sensor. | **CSV actual.** La proyeccion a 30 dias es una estimacion y no esta en el archivo. |
| **Velocidad** | Los sensores reportan de forma periodica y las alertas de temperatura pierden valor si se detectan tarde. En el archivo, cada sensor registra una lectura **cada 60 segundos**, sin huecos. Con 40 sensores, entran 40 lecturas por minuto (2,400 por hora). | S001 genera una lectura por minuto desde el 01/09/26 00:00. Las 2,500 marcas de tiempo distintas cubren de forma continua 1 dia y 17 h 39 min (hasta el 02/09/26 17:39). | **CSV actual** para la frecuencia de muestreo (1 lectura/min por sensor). **Ampliación futura** para la ingesta en tiempo real: el archivo es un lote historico y no un flujo (*streaming*). |
| **Variedad** | El sistema mide dos magnitudes fisicas distintas (temperatura y vibracion) y se organiza por planta y sensor. Todo el archivo es **estructurado y tabular**: 1 identificador, 1 fecha en texto, 2 columnas categoricas (`id_sensor`, `planta`) y 2 numericas. El archivo no tiene datos semiestructurados ni no estructurados. | Fotos de camaras termograficas, bitacoras de mantenimiento en texto libre o lecturas de presion y humedad en formato JSON, combinadas con las lecturas actuales de temperatura y vibracion. | **Ampliación futura.** Ninguno de esos tipos de dato aparece en el CSV actual. |
| **Veracidad** | Es la confiabilidad de lo medido: una lectura erronea genera falsas alarmas o deja pasar fallas reales. En este archivo no hay nulos ni registros duplicados, y los valores estan en rangos fisicamente plausibles. Hay dos puntos a vigilar. La fecha viene como **texto `dd/mm/aa hh:mm`**, y `pandas` la interpreto mal al leerla sin indicar el formato. El archivo tampoco trae una columna que indique si el sensor estaba calibrado o fallo. | 0 valores nulos en las 6 columnas, 0 `id_registro` duplicados, temperatura entre 45.00 y 104.99 °C, vibracion entre 0.50 y 5.50 mm/s. Cada `id_sensor` pertenece a una sola planta. | **CSV actual** para las verificaciones anteriores. Un indicador de calibracion o estado del sensor seria **ampliación futura**. |
| **Valor** | El valor esta en convertir lecturas en decisiones: detectar sobrecalentamientos, comparar plantas y priorizar inspecciones. Con el umbral de 85 °C usado en el analisis, el sistema ya puede señalar donde actuar primero. | **6,954 lecturas superan 85 °C (6.95 %)**. Planta_3 tiene mas alertas (1,777), seguida de Planta_1 (1,737), Planta_4 (1,732) y Planta_2 (1,708). La lectura maxima fue **104.99 °C**, registrada por el sensor **S023** (Planta_3) el 01/09/26 a las 22:23. | **CSV actual** para el conteo de alertas. El **mantenimiento predictivo**, que cruzaría temperatura y vibracion con el historial de fallas, es **ampliacion futura**: el archivo no trae fallas registradas. |

> recordatorio: el punto maximo de 85 °C viene del codigo del analisis, no del archivo. Las diferencias entre plantas son pequeñas (el promedio de temperatura va de 66.53 a 66.77 °C), asi que con estos datos no se puede afirmar que una planta este realmente peor que otra.

## Resultados del analisis usados en el informe

| Metrica | Resultado |
|---|---|
| Registros | 100,000 |
| Sensores distintos | 40 |
| Plantas | 4 |
| Temperatura promedio por planta | Planta_1: 66.62 °C, Planta_2: 66.53 °C, Planta_3: 66.77 °C, Planta_4: 66.67 °C |
| Registro con la temperatura mas alta | Fila 53742 (índice de `pandas`), `id_registro` 53743 |
| Sensor y fecha de ese registro | S023, 01/09/26 22:23 |
| Lecturas con temperatura > 85 °C | 6,954 |
| Planta con mas alertas | Planta_3, con 1,777 |

## Tipo de procesamiento realizado
Batch, debido a que el programa que esta analizando el conjunto de datos ya se encuentra almacenado en un archivo estructurado CSV. Además, todos los registros se analizan de manera global y simultánea en un solo bloque de ejecución, sin que lo datos lleguen de forma continua en tiempo real.

## ¿Cómo puedo emitir una alerta pocos segundos después de un evento?
Streaming, badandonos en una arquitectura de procesamiento de eventos mediante un broker, en donde los sensores se comuniquen por protocolos como MQTT  y un motor de procesamiento evalúe la condición de la lectura y dispare si un evento se presenta

## ¿Cómo generar un informe al terminar el día?
Batch, para poder calcular el conteo de alertas presentadas a lo largo del día es más eficiente procesar todo el volumen de datos al cierre de periodo en lugar de estar recalculando el resumen cada segundo.

## Toma de decision en relación a la necesidad de cada resultado
- Para las alertas es más óptimo utilizar un sistema streaming, de esta manera se tiene al pendiente cada sensor y algun evento que se este presentando en tiempo real
- Por el contrario, si se requiere de un informe al final del periodo resulta más óptimo batch ya que el costo y la complejidad de mantener un flujo continuo no se justifican en esta labo.