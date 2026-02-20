import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario
from trayectoria import recorrido



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

def run_simulacion():

    escenario,x_beacons,y_beacons, largo, ancho = crear_escenario()

    x_tray,y_tray = recorrido(largo,ancho,0.25)
    trayectoria = {'x' : x_tray,
                   'y' : y_tray
    }


    for j in range (len(x_beacons)):
        trayectoria[f'RSSI{j}'] = []
    
    trayectoria = calcular_rssi_nodo(trayectoria,x_beacons,y_beacons)
    
    num_puntos=len(trayectoria['RSSI0'])
    for j in range(num_puntos):
        rssi=[]
        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j])
        Xi,Yi,RSSI = posicionamiento (rssi,escenario)

    Xi_r = trayectoria['x']
    Yi_r = trayectoria['y']

    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    ax.scatter(x_beacons, y_beacons, color='red', marker='^') # Beacons
    ax.plot(Xi_r, Yi_r,'b-',zorder=1)
    ax.plot(Xi_r, Yi_r,'bs',zorder=1)
    #ax.scatter(escenario['x'], escenario['y'], color='green') # Puntos del footprint
    ax.set_title('Simulación de posicionamiento')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.legend()
    ax.grid()

    plt.pause(1)

    for j in range(num_puntos):
        rssi=[]
        #ax.scatter(escenario['x'], escenario['y'], color='green') # Puntos del footprint
        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j])

        Xi,Yi,RSSI = posicionamiento (rssi,escenario) # Posicionamiento estimado
        punto=ax.scatter(Xi, Yi,color='red') # Posición estimada correspondiente a un punto del footprint


        plt.draw()
        #plt.pause(1)
        #punto.remove()



    plt.ioff()
    plt.show()
if __name__ == "__main__":
    run_simulacion()