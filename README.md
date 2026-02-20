# <u>Simulación de posicionamiento en interiores con RSSI</u>
Se trata de implementar una simulación básica de posicionamiento en interiores utlizando valores `RSSI` previamente estimados en el escenario propuesto.
Consta de 3 códigos:
*  escenario_sim.py
*  rssi_trayectoria.py
*  sim_tray_vecinos_v2.py


## 🧭 Simulador de trayectoria
Para la simulación de la trayectoria dentro de un escenario definido en base a la propuesta, es necesario conocer los requisitos y las funciones adicionales para la ejecución del simulador.
### 🛠️ Requisitos 
```bash
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario
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
from rssi_trayectoria import calcular_rssi_nodo

def rejilla(largo, ancho,x_beacons,y_beacons):
    dens_puntos=0.2
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

    return escenario , x_beacons, y_beacons

if __name__ == "__main__":
    escenario ,  x_beacons, y_beacons = crear_escenario()
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
    n=1.8
    rssi=[]
    
    for j in range (len(x_beacons)):
        for i in range (len((trayectoria['x']))):
            d = (np.sqrt((trayectoria['x'][i] - x_beacons[j])**2 + (trayectoria['y'][i] - y_beacons[j])**2 ))
            rssi = txpower - 10*n*np.log10(d)
            trayectoria[f'RSSI{j}'].append(rssi)
    return trayectoria

```

### 🧭 Simulación de la trayectoria del nodo
Para el desarrollo de la simulación, en primer lugar se realiza una función `posicionamiento()`para calcular la posición del nodo teniendo en cuenta el escenario planteado y los valores `RSSI` del nodo. Las posiciones finales estimadas serán las del punto del **FingerPrinting** más cercano.


```bash
def posicionamiento (rssi_n,escenario):

    aux=[]
    x_vecino=[]
    y_vecino=[]
    rssi_vecino=[]
    distancia=[]
    columnas_rssi=[]
    for col in escenario.keys():
        if col.startswith('RSSI'):
            columnas_rssi.append(col)
    
    for i in range(len(escenario['x'])):
        escenario_rssi = np.array([escenario[col][i] for col in columnas_rssi])
        distancia = np.linalg.norm(rssi_n - escenario_rssi)

        aux.append(round(float(distancia), 2))

    indice = np.argsort(aux)[:1]
    for j in indice:
        x_vecino.append(escenario['x'][j])
        y_vecino.append(escenario['y'][j])
        rssi_vecino.append([escenario[col][j] for col in columnas_rssi])

    return x_vecino,y_vecino,rssi_vecino
```
Para la simulación de la trayectoria que va a seguir el nodo, se obtienen las coordenadas XY del archivo 'trayectoria.xslx'. Para diseñar una trayectoria es necesaria cambiar las coordenadas en dicho archivo.
Además, se implementa las líneas de código para la representación báscica de la trayectoria en el escenario.
```bash
# Requisitos
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario


def run_simulacion():
    # Creación de escenario
    escenario,x_beacons,y_beacons = crear_escenario() 

    # Trayectoria del nodo
    archivo_trayectoria = 'trayectoria.xlsx'
    df2 = pd.read_excel(archivo_trayectoria)
    trayectoria = df2.to_dict(orient='list')

    # Se crean tantas columnas RSSI como número de balizas haya en el escenario
    for j in range (len(x_beacons)):
        trayectoria[f'RSSI{j}'] = []
    
    # Se calculan los valores RSSI correspondientes
    trayectoria = calcular_rssi_nodo(trayectoria,x_beacons,y_beacons)
    
    # Se obtienen las coordenadas XY estimadas
    num_puntos=len(trayectoria['RSSI0'])
    for j in range(num_puntos):
        rssi=[]
        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j])
        Xi,Yi,RSSI = posicionamiento (rssi,escenario)


    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    ax.scatter(x_beacons, y_beacons, color='red', marker='^') # Representación de las balizas
    #ax.scatter(escenario['x'], escenario['y'], color='green') # Representación de los puntos del FingerPrinting
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
        Xi_r = trayectoria['x']
        Yi_r = trayectoria['y']
            
        Xi,Yi,RSSI = posicionamiento (rssi,escenario) # Trayectoria estimada
        punto=ax.scatter(Xi, Yi,color='red') # Trayectoria propuesta
        ax.scatter(Xi_r, Yi_r,color='blue',marker='s')
        plt.draw()
        plt.pause(1)
        #punto.remove()


    plt.ioff()
    plt.show()
if __name__ == "__main__":
    run_simulacion()
```