import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement


def escenario():
    
    # Address de las 5 beacons
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
    df = pd.read_excel('setup.xlsx')
    escenario = df.to_dict('list')
    for j in range (num_beacons):
        escenario[f'RSSI{j}'] = []

    # Obtener y guardar el RSSI con respecto a las beacons
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
                    if 0 in rssi_n: # Esperar a recibir RSSI de todas la beacons para tomar las muestras
                            print("Todiavia no se ha recibido RSSI de todas las balizas: ",rssi_n)
                    else: # Tomar las muestras
                        for j in range(len(escenario['x'])):
                            print(j)
                            for i in range(len(address_beacons)):
                                escenario[f'RSSI{i}'].append(rssi_n[i])
                            array_rssi[indice] = []
                            input(f"Siguiente punto...") # Se toma la muestra y pulsar ENTER tras cambiar de punto

        if len(escenario['RSSI0']) == len(escenario['x']):
            break

    # Crear archivo del FingerPRinting
    df2 = pd.DataFrame(escenario)
    df2.to_excel('escenario_.xlsx', index=False)
    print(df2)

if __name__ == "__main__":
    escenario()

