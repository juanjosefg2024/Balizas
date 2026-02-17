### Simulación de posicionamiento en interiores con RSSI
Se trata de implementar una simulación básica de posicionamiento en interiores utlizando valores RSSI previamente estimados en el escenario propuesto.
Es un escenario basico con 3 balizas en las coordenadas [(0,0),(4,0),(0,4)]

# Requisitos
```bash
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```
# Valores RSSI estimados por coordenada
Se querie del archivo 'escenario.xlsx'.
Tener en cuenta el path de dicho archivo

## Funciones del código
# Función 'posicionamiento'
Esta función trata de calcular la distancia del nodo con cada uno de los puntos calculados del escenario para posteriormente obtener las coordenadas xy y el valor RSSI del punto vecino más cercano.

```bash
def posicionamiento (rssi_n,escenario):

    aux=[]
    x_vecino=[]
    y_vecino=[]
    rssi_vecino=[]
    var=[]

    for i in range(len(escenario['x'])):
        rssia = escenario['RSSIA'][i]
        rssib = escenario['RSSIB'][i]
        rssic = escenario['RSSIC'][i]
        var = np.sqrt((rssi_n[0] - rssia)**2 + (rssi_n[1] - rssib)**2 + (rssi_n[2] - rssic)**2)
        aux.append(round(float(var), 2))

    indices = np.argsort(aux)[:1] # indices del valores minimos
    #indices = np.argsort(aux)[:3] # Indices de los 3 valores minimos (3 vecinos)

    
    for j in indices:
        x_vecino.append(escenario['x'][j])
        y_vecino.append(escenario['y'][j])
        rssi_vecino.append([escenario['RSSIA'][j],escenario['RSSIB'][j],escenario['RSSIC'][j]])
    return x_vecino,y_vecino,rssi_vecino
```
# Función 'run_simulation'
archivo = '~/Escritorio/escenario.xlsx'
    df = pd.read_excel(archivo)
    escenario = df.to_dict(orient='list')

    pos_beacons = [(0,0),(0,4),(4,0)]
    x_beacons=[b[0] for b in pos_beacons]
    y_beacons=[b[1] for b in pos_beacons]

# Valores RSSI del nodo. Como ejemplo he usado 
En esta función se carga el archivo 'escenario.xlsx'
Se define las posiciones de las 3 balizas
Se usan varios valores de RSSI (del nodo) para realizar pruebas.
Calcula la posición estimada de cada uno (vecino más cercano).
Representación gráfica
```bash
    rssi_n=[
        [-53.51544993,-60.50514998,-60.50514998],
        [-60.50514998,-53.51544993,-61.96643034],
        [-60,-55,-61],
        [-58.2,-60.5,-60],
        [-55,-60.7,-61],
        [-60.07421924,-59,-60.07421924],
        [-60.50514998,-61.96643034,-53.51544993],
        [-61.96643034,-60.50514998,-60.50514998]
    ]
    num_puntos=len(rssi_n)

    plt.figure(figsize=(10,10))
    plt.scatter(x_beacons, y_beacons, color='red', marker='^') # Beacons
    plt.scatter(escenario['x'], escenario['y'], color='green') # Puntos del footprint
    for i in range(num_puntos):
        Xi,Yi,RSSI = posicionamiento (rssi_n[i],escenario) # Posicionamiento estimado
        plt.scatter(Xi, Yi,color='red') # Posición estimada correspondiente a un punto del footprint
        print(RSSI)

    plt.title('Simulación de posicionamiento')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend()
    plt.grid()
    plt.show()
```
