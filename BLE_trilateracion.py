import numpy as np
import matplotlib.pyplot as plt
import time
import threading
import queue
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

q = queue.Queue()

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
    area_inn = 115
    lado =  np.sqrt(area_inn)
    x_beacons=[0,0,lado,lado]
    y_beacons=[0,lado,0,lado]
    ble = BLERadio()
    B1 = "FE:2F:2E:23:53:2F"
    B2 = "F9:AA:8D:12:63:70"
    B3 = "ED:6F:72:1B:F1:83"
    B4 = "DC:04:2E:9D:49:62"
    B5 = "D6:F4:62:94:9C:6A"
    address_beacons = [B1,B2,B3,B4]
    num_beacons = len(address_beacons)
    address_indice = {addr: i for i, addr in enumerate(address_beacons)}
    rssi_n = np.zeros(num_beacons)

    
    while True:
        for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
            #if UARTService in advertisement.services:
            rssi = advertisement.rssi
            address = str(advertisement.address).split('"')[1]
            if address in address_beacons:
                indice = address_indice[address]
                rssi_n[indice] = rssi
            print(rssi_n)
            Xi,Yi = trilateracion_2d (rssi_n,x_beacons,y_beacons)
            print(Xi,Yi)
            q.put((Xi,Yi))

            
def run_visualizacion():
    area_inn = 115
    lado =  np.sqrt(area_inn)
    x_beacons=[0,0,lado,lado]
    y_beacons=[0,lado,0,lado]

    
    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    ax.scatter(x_beacons, y_beacons, color='red', marker='s') # Representación de las beacons
    ax.set_title('Simulación de posicionamiento')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.grid()

    punto, = ax.plot([], [], 'bo') 
    while True:
        try:
            Xi, Yi = q.get()
            #punto.remove() # Descomentar para visualizar solamente la posición actual
            #ax.clear()
            #ax.scatter(Xi, Yi, color='blue')
            punto.set_data([Xi],[Yi])
            fig.canvas.draw() 
            fig.canvas.flush_events()
        except queue.Empty:
           pass
        plt.pause(0.01)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_simulacion,daemon=True)
    t1.start()
    #t2 = threading.Thread(target=run_visualizacion)
    #t2.start()

    run_visualizacion()