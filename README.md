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
        var = (np.sqrt((rssi_n[0] - rssia)**2 + (rssi_n[1] - rssib)**2 + (rssi_n[2] - rssic)**2))
        aux.append(round(float(var), 2))

    indices = np.argsort(aux)[:3] # indices de los 3 valores minimos (3 vecinos)
    
    for j in indices:
        x_vecino.append(escenario['x'][j])
        y_vecino.append(escenario['y'][j])
        rssi_vecino.append([escenario['RSSIA'][j],escenario['RSSIB'][j],escenario['RSSIC'][j]])
        
    return x_vecino,y_vecino,rssi_vecino
```
# Función 'trilateracion_2d'
Esta función trata de estimar las coordenadas x e y del nodo, a partir de la trilateriación de los puntos vecinos.

```bash
def trilateracion_2d(rssi_n,escenario):
    # Posiciones de los puntos vecinos
    X, Y, rssi = posicionamiento(rssi_n,escenario) # posicion y rssi de los puntos mas cercano
    n=2.5
    txpower=-59
    r=[]    
    x=[]
    y=[]
    x = X
    y = Y
    dn=[]
    di=[]
    aux=0.01
    for i in range(3):
        dn.append(10**((txpower-rssi_n[i])/(10*n)))

    for i in range(3):

        # Distancias del vecino a cada beacon
        di = []
        for j in range(3):
            di.append(10 ** ((txpower - rssi[i][j]) / (10 * n)))

        # Diferencia entre las distancias del nodo y la de los vecinos con respecto a las beacons
        radio = np.sqrt(
            (dn[0] - di[0])**2 +
            (dn[1] - di[1])**2 +
            (dn[2] - di[2])**2
        )
        if radio < aux:
            return X[0], Y[0]
        r.append(radio)


    A = -2*(x[1]-x[0])
    B = -2*(y[1]-y[0])
    C = -2*(x[2]-x[0])
    D= -2*(y[2]-y[0])
    E = r[0]**2 - r[1]**2 + x[1]**2 - x[0]**2 + y[1]**2 - y[0]**2
    F = r[0]**2 - r[2]**2 + x[2]**2 - x[0]**2 + y[2]**2 - y[0]**2
    determinante = B*C-A*D
    if determinante == 0:
        x = None
        y = None
    else:
        x = np.abs((E*D-B*F)/(determinante))
        y = np.abs((A*F-E*C)/(determinante))
    
    return x,y
```
# Función 'run_simulation'

En esta función se carga el archivo 'escenario.xlsx'
Se define las posiciones de las 3 balizas
Se usan varios valores de RSSI (del nodo) para realizar pruebas.
Calcula la posición estimada de cada uno (vecino más cercano).
Representación gráfica

```bash
    archivo = '~/Escritorio/escenario.xlsx'
    df = pd.read_excel(archivo)
    escenario = df.to_dict(orient='list')

    pos_beacons = [(0,0),(0,4),(4,0)]
    x_beacons=[b[0] for b in pos_beacons]
    y_beacons=[b[1] for b in pos_beacons]
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
