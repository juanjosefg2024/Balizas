import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import threading
import queue
import pandas as pd
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

q = queue.Queue()

def posicionamiento (rssi_n,escenario):
    # Se calcula la distancia entre el nodo y los puntos del FingerPrinting
    # Se devuelve las coordenadas XY del punto más cercano
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

    return x_vecino,y_vecino

def run_simulacion():

    # Se selecciona el excel con las coordenadas XY de las muestras a recoger
    archivo = '~/setup/escenario.xlsx'
    df = pd.read_excel(archivo)
    escenario = df.to_dict(orient='list')
    ble = BLERadio()
    B1 = "FE:2F:2E:23:53:2F"
    B2 = "F9:AA:8D:12:63:70"
    B3 = "ED:6F:72:1B:F1:83"
    B4 = "DC:04:2E:9D:49:62"
    B5 = "D6:F4:62:94:9C:6A"
    address_beacons = [B1,B2,B3,B4,B5]
    num_beacons = len(address_beacons)
    address_indice = {addr: i for i, addr in enumerate(address_beacons)}
    rssi_n = np.zeros(num_beacons)

    array_rssi = [[] for i in range(num_beacons)]

    while True:
        for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
            rssi = advertisement.rssi
            address = str(advertisement.address).split('"')[1]
            if address in address_beacons:
                indice = address_indice[address]
                array_rssi[indice].append(rssi)
                if len(array_rssi[indice]) == 10:
                    datos = np.array(array_rssi[indice])

                    # Filtro gaussiano para evitar fluctuaciones
                    aux = gaussian_filter(datos, sigma=1)
                    valores = np.sort(aux.flatten())
                    val=valores[3:-3]
                    media = np.mean(val)
                    rssi_n[indice] = media
                    Xi,Yi = posicionamiento (rssi_n,escenario)
                    array_rssi[indice] = []
                    # Se mandan las coordenas estimadas para la visualización
                    q.put((Xi,Yi))
            
def run_visualizacion():
    area_inn = 115
    lado =  np.sqrt(area_inn)
    b1 = [lado/2,(lado/2)-0.3,2.2]
    b2 = [5.35,0.52,1.9]
    b3 = [2.95,lado-0.52,1.9]
    b4 = [6.7,lado-0.52,1.9]
    b5 = [2.95,0.52,1.9]

    x_beacons=[b1[0],b2[0],b3[0],b4[0],b5[0]]
    y_beacons=[b1[1],b2[1],b3[1],b4[1],b5[1]]

    plt.ion()
    fig,ax = plt.subplots(figsize=(10,10))
    imagen = plt.imread("sala_innovacion.png") # Plano de la sala de innovación
    ax.imshow(imagen,extent=[0,lado,0,lado])
    ax.scatter(x_beacons, y_beacons, color='red', marker='s') # Representación de las beacons
    ax.set_title('Simulación de posicionamiento')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    punto, = ax.plot([], [], 'bo') 
    while True:
        try:
            Xi, Yi = q.get()
            punto.set_data([Xi],[Yi]) # Representación de la posición estimada en tiempor real
            fig.canvas.draw() 
            fig.canvas.flush_events()
        except queue.Empty:
           pass
        plt.pause(0.01)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_simulacion,daemon=True)
    t1.start()

    run_visualizacion()