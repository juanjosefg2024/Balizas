import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo
from escenario_sim import crear_escenario

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

    indice = np.argsort(aux)[:3]
    for j in indice:
        x_vecino.append(escenario['x'][j])
        y_vecino.append(escenario['y'][j])
        rssi_vecino.append([escenario[col][j] for col in columnas_rssi])

    return x_vecino,y_vecino,rssi_vecino

def trilateracion_2d(rssi_n,escenario):

    X, Y, rssi = posicionamiento(rssi_n,escenario)
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

def run_simulacion():

    escenario,x_beacons,y_beacons = crear_escenario()

    # Trayectoria del nodo
    archivo_trayectoria = '~/Escritorio/trayectoria.xlsx'
    df2 = pd.read_excel(archivo_trayectoria)
    trayectoria = df2.to_dict(orient='list')

    for j in range (len(x_beacons)):
        trayectoria[f'RSSI{j}'] = []
    
    trayectoria = calcular_rssi_nodo(trayectoria,x_beacons,y_beacons)
    
    num_puntos=len(trayectoria['RSSI0'])
    for j in range(num_puntos):
        rssi=[]
        for i in range(len(x_beacons)):
            rssi.append(trayectoria[f'RSSI{i}'][j])
        Xi,Yi,RSSI = posicionamiento (rssi,escenario)


    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    ax.scatter(x_beacons, y_beacons, color='red', marker='^') # Beacons
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
        Xi_r = trayectoria['x']
        Yi_r = trayectoria['y']
            
        Xi,Yi = trilateracion_2d (rssi,escenario) # Posicionamiento estimado
        punto=ax.scatter(Xi, Yi,color='red') # Posición estimada correspondiente a un punto del footprint
        ax.scatter(Xi_r, Yi_r,color='blue',marker='s')
        plt.draw()
        plt.pause(1)
        #punto.remove()


    plt.ioff()
    plt.show()
if __name__ == "__main__":
    run_simulacion()