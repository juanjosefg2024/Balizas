import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario
from trayectoria import recorrido

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
            d = (10**((txpower-rssi_n[i])/(10*n))) # Distancia del nodo a las 3 beacons
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
            rssi.append(trayectoria[f'RSSI{i}'][j]) # Variable RSSI del nodo en el recorrido establecido

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