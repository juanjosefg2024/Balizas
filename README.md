# <u>Simulación de posicionamiento en interiores con RSSI</u>
Se trata de implementar una simulación básica de posicionamiento en interiores utlizando valores `RSSI` previamente estimados en el escenario propuesto.
Consta de 3 códigos:
*  escenario_sim.py
*  trayectoria.py
*  rssi_trayectoria.py
*  sim_tray_trilateracion_v3.py



## 🧭 Simulador de trayectoria
Para la simulación de la trayectoria dentro de un escenario definido en base a la propuesta, es necesario conocer los requisitos y las funciones adicionales para la ejecución del simulador.
### 🛠️ Requisitos 
```bash
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario
from trayectoria import recorrido
```
### 🌐 Simulación de escenario
La creación del escenario se realiza de manera programable. Para ello, se llama a la función `crear_escenario()` que es importada desde `escenario_sim.py`.
Para montar el escenario se pide por terminal el `número de balizas`, el `ancho` y el `largo` del escenario. Con respecto al número de balizas:
* Si es igual o menor a 4 se colocan en las esquinas del área.
* Si es mayor a 4, se colocan 4 en las esquinas y el resto se les asignará coordenadas XY por terminal.  

Además, teniendo en cuenta el área y la densidad de puntos previamente establecidad, se monta el **FingerPrinting** necesario para llevar a cabo el posicionamiento por puntos vecinos.
Las funciones que componen `escenario_sim.py` son:
```bash
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo

def rejilla(largo, ancho,x_beacons,y_beacons):
    dens_puntos=0.5
    x=[]
    y=[]
    index_x=[]
    index_y=[]
    final_largo = largo+dens_puntos
    final_ancho = ancho+dens_puntos
    for i in np.arange(0,final_largo,dens_puntos):
        for j in np.arange(0,final_ancho,dens_puntos):
            x.append(round(i,2))
            y.append(round(j,2))
    
    for i in range(len(x)):
        for j in range(len(x_beacons)):
            if x[i] == x_beacons[j] and y[i] == y_beacons[j]:
                index_x.append(i)
                index_y.append(i)
    for i in sorted(index_x,reverse=True):
        del x[i]
        del y[i]
    return x,y

def beacons_pos(num_beacons,largo,ancho):



    x_beacons=[0,0,largo,largo]
    y_beacons=[0,ancho,0,ancho]

    if num_beacons > 4:
        for j in range(num_beacons-4):
            x_beacons.append(float(input(f"Coordenadas X de la baliza {j}: ")))
            y_beacons.append(float(input(f"Coordenadas Y de la baliza {j}: ")))

    else:
        x_beacons=x_beacons[:num_beacons]
        y_beacons=y_beacons[:num_beacons]

    return x_beacons,y_beacons

def crear_escenario():

    num_beacons=int(input("Número de balizas: "))
    largo = int(input("Longitud del largo del escenario: "))
    ancho = int(input("longitud del ancho del escenario: "))

    x_beacons,y_beacons = beacons_pos(num_beacons,largo,ancho)
    x_puntos,y_puntos = rejilla(largo, ancho,x_beacons,y_beacons)

    escenario = {
        'x' : x_puntos,
        'y' : y_puntos
    }
    for j in range (len(x_beacons)):
        escenario[f'RSSI{j}'] = []
    escenario = calcular_rssi_nodo(escenario,x_beacons,y_beacons)

    return escenario , x_beacons, y_beacons, largo, ancho

if __name__ == "__main__":
    escenario ,  x_beacons, y_beacons, largo, ancho = crear_escenario()

```
Se requiere de la función `calcular_rssi_nodo` que se importa desde `rssi_trayectoria.py`.
### 📶 Cálculo los valores RSSI
Con esta función se trata de calcular los valores `RSSI` del nodo respecto a las balizas que conforman el escenario. Esta función se utiliza tanto para la creación del **FingerPrinting** como para la trayectoria del nodo.
En esta función se va a requerir de las siguientes dos ecuaciones:
<div align="center">

**Distancia entre puntos**

$$d_{i,j} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$$

**Log-Distance Path Loss Model (RSSI)**
$$RSSI = P_{tx} - 10*FreeSpaceFactor* \log_{10}(d)$$
</div>


La función `calcular_rssi_nodo()` se muestra a continuación.


```bash
import numpy as np

def calcular_rssi_nodo(trayectoria, x_beacons,y_beacons):
    txpower=-59
    n=2.5
    rssi=[]
    
    for j in range (len(x_beacons)):
        for i in range (len((trayectoria['x']))):
            d = (np.sqrt((trayectoria['x'][i] - x_beacons[j])**2 + (trayectoria['y'][i] - y_beacons[j])**2 ))
            rssi = txpower - 10*n*np.log10(d)
            trayectoria[f'RSSI{j}'].append(rssi)
    return trayectoria

```
### Trayectoria

Se propone el siguiente diseño de trayectoria adaptable a las dimensiones del escenario.
```bash

import numpy as np

def recorrido(largo, ancho, paso):

    x = []
    y = []

    xmin = 0.25
    xmax = largo - 0.25
    ymin = 0.25
    ymax = ancho - 0.25

    for xi in np.arange(xmin, xmax + paso, paso):
        x.append(round(xi, 3))
        y.append(round(ymin, 3))

    for yi in np.arange(ymin + paso, ymax + paso, paso):
        x.append(round(xmax, 3))
        y.append(round(yi, 3))

    for xi in np.arange(xmax - paso, xmin - paso, -paso):
        x.append(round(xi, 3))
        y.append(round(ymax, 3))

    for yi in np.arange(ymax - paso, ymin, -paso):
        x.append(round(xmin, 3))
        y.append(round(yi, 3))

    xcentro = largo / 2
    ycentro = ancho / 2

    for d in np.arange(0.5, min(xcentro, ycentro), paso):
        x.append(round(d, 3))
        y.append(round(d, 3))

    x0 = round(xcentro, 3)
    y0 = round(ycentro, 3)

    x.append(x0)
    y.append(y0)

    x.append(x0)
    y.append(y0 + 1)

    x.append(x0 + 1)
    y.append(y0 + 1)

    x.append(x0 + 1)
    y.append(y0)

    x.append(x0)
    y.append(y0)

    return x, y

```

### 🧭 Simulación de la trayectoria del nodo
Para el desarrollo de la simulación, en primer lugar se realiza una función `trilateracion_2d()` para calcular la posición del nodo teniendo en cuenta el escenario planteado y los valores `RSSI` del nodo. Las posiciones finales estimadas serán las resultante de realizar la trilateración. Para la trilateración, se realiza con respecto a todas las beacons del escenario (xi, yi, ri) y se utiliza como referencia la posición XY (x0, y0) de la beacon de la cual se obtiene el mayor RSSI y la distancia (r0) del nodo a dicha beacon.


```bash
def trilateracion_2d(rssi_n,x_beacons,y_beacons):

    n=2.5
    txpower=-59
    xi=[]
    yi=[]
    ri=[]


    indice = np.argmax(rssi_n)
    r0 = 10**((txpower-rssi_n[indice])/(10*n))
    x0, y0 = x_beacons[indice], y_beacons[indice]

    for i in range(len(x_beacons)):
        if i != indice:
            xi.append(x_beacons[i])
            yi.append(y_beacons[i])
            d = (10**((txpower-rssi_n[i])/(10*n))) # Distancia del nodo a las beacons
            ri.append(d)

    xi = np.array(xi)
    yi = np.array(yi)
    ri = np.array(ri)
    
    A = np.column_stack([2*(xi - x0), 2*(yi - y0)])
    B = (xi**2 + yi**2 - ri**2) - (x0**2 + y0**2 - r0**2)

    posiciones, residuals, rank, s  = np.linalg.lstsq(A, B, rcond=None)
    return posiciones[0],posiciones[1]


def run_simulacion():

    escenario,x_beacons,y_beacons, largo, ancho = crear_escenario()

    # Se añaden las posciones XY de la trayectoria o recorrido simulado
    x_tray,y_tray = recorrido(largo,ancho,0.25)
    trayectoria = {'x' : x_tray,
                   'y' : y_tray
    }

    
    # Se crean tantas columnas RSSI como beacons haya
    for j in range (len(x_beacons)):
        trayectoria[f'RSSI{j}'] = []
    # Rellenar las columnas RSSI teniendo en cuenta las posiciones
    trayectoria = calcular_rssi_nodo(trayectoria,x_beacons,y_beacons)
    
    num_puntos=len(trayectoria['RSSI0'])
    for j in range(num_puntos):
        rssi=[]
        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j]) # Variable RSSI del nodo en el recorrido establecido con respecto a cada beacons

    # Representacion punto a punto
    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    ax.scatter(x_beacons, y_beacons, color='red', marker='s') # Representación de las beacons
    ax.set_title('Simulación de posicionamiento')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.legend()
    ax.grid()
    plt.pause(1)

    for j in range(num_puntos):
        rssi=[]

        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j])
        Xi_r = trayectoria['x'][j]
        Yi_r = trayectoria['y'][j]
        Xi,Yi = trilateracion_2d (rssi,x_beacons,y_beacons) # Estimación de posición mediante trilateracion

        ea = np.sqrt((Xi_r-Xi)**2 + (Yi_r-Yi)**2)
        er = (ea/(np.sqrt(Xi_r**2 + Yi_r**2)))*100
        # print(f"Error absoluto {ea}, Porcentaje de error {er}") # Descomentar para ver el error absoluto entre posiciones y el porcentaje de error
        punto=ax.scatter(Xi, Yi,color='blue') # Representación de las posiciones estimadas
        plt.draw()
        plt.pause(0.1)
        #punto.remove() # Descomentar para visualizar solamente la posición actual
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_simulacion()
```