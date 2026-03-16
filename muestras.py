import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()


#-------------------------------------------------------------------
def cargar(escenario,num_beacons,rssi_n):
    for h in range(num_beacons):
        escenario[f'RSSI{h}'].append(rssi_n[h])
    input("Pulsa ENTER cuando hayas cambiado al siguiente punto...")    

    
def muestreo():
    B1 = "FE:2F:2E:23:53:2F"
    B2 = "F9:AA:8D:12:63:70"
    B3 = "ED:6F:72:1B:F1:83"
    B4 = "DC:04:2E:9D:49:62"
    address_beacons = [B1,B2,B3,B4]
    num_beacons = 4
    address_indice = {addr: i for i, addr in enumerate(address_beacons)}
    rssi_n = np.zeros(num_beacons)
    array_rssi = [[] for i in range(num_beacons)]
    escenario = simulacion()
    j=0

    # Obtener y guardar el RSSI con respecto a las beacons
    scanner = ble.start_scan(ProvideServicesAdvertisement)
    for advertisement in scanner:
        if UARTService in advertisement.services:
            rssi = advertisement.rssi
            address = str(advertisement.address).split('"')[1]
            if address in address_beacons:
                indice = address_indice[address]
                array_rssi[indice].append(rssi)
                if all(len(col) >= 5 for col in array_rssi):
                    for h in range(num_beacons):
                        datos = np.array(array_rssi[h])

                        # Filtro gaussiano para evitar fluctuaciones
                        aux = gaussian_filter(datos, sigma=1)
                        valores = np.sort(aux.flatten())
                        val=valores[2:-2]
                        media = np.mean(val)
                        rssi_n[h] = media

                    if np.any(rssi_n == 0): # Esperar a recibir RSSI de todas la beacons para tomar las muestras
                            print("Todavia no se ha recibido RSSI de todas las balizas: ",rssi_n)
                    
                    else: # Tomar las muestras
                        if j < len((escenario['x'])):                      
                            cargar(escenario,num_beacons,rssi_n)
                            j += 1
                            array_rssi = [[] for i in range(num_beacons)]

        if len(escenario['RSSI0']) == len(escenario['x']):
            break

    escenario_df = pd.DataFrame(escenario)
    escenario_df.to_excel('muestras.xlsx', index=False)
    return escenario


def simulacion():
    num_beacons=4
    muestras_pos = 'archivos_adjuntos/setup.xlsx' #Archivo de las coordenadas XY de las muestras del FingerPrinting
    df = pd.read_excel(muestras_pos)
    escenario = df.to_dict('list')
    for j in range (num_beacons):
        escenario[f'RSSI{j}'] = []
    return escenario

if __name__ == "__main__":
    escenario_comp = muestreo()
    print(escenario_comp)





