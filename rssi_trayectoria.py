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
