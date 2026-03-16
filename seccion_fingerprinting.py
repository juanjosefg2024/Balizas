from nicegui import ui
import pandas as pd
import numpy as np
import threading
import queue
from scipy.ndimage import gaussian_filter
import configparser
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from muestras import muestreo




q1 = queue.Queue()
escaneo = False
ble = BLERadio()
puntos_beacons = ""
punto_nodo = ""
puntos_acumulados = ""

def obtener_arg_fp():

    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # x_beacons = [float(x) for x in config['beacons_pos']['x_beacons'].split(',')]
    # y_beacons = [float(y) for y in config['beacons_pos']['y_beacons'].split(',')]
    # z_beacons = [float(z) for z in config['beacons_pos']['z_beacons'].split(',')]
    # address_beacons = list(config['beacons_add'].values())
    # num_beacons = int(config['beacons_pos']['num_beacons'])

    # B1 = "FE:2F:2E:23:53:2F"
    # B2 = "F9:AA:8D:12:63:70"
    # B3 = "ED:6F:72:1B:F1:83"
    # B4 = "DC:04:2E:9D:49:62"
    # B5 = "D6:F4:62:94:9C:6A"
    # address_beacons = [B1,B2,B3,B4,B5]
    # num_beacons = 5
    # x_beacons = [5.36,5.35,2.95,6.7,2.95]
    # y_beacons = [5.06,0.52,10.2,10.2,0.52]
    # z_beacons = [2.2,1.9,1.9,1.9,1.9]


    B1 = "FE:2F:2E:23:53:2F"
    B2 = "F9:AA:8D:12:63:70"
    B3 = "ED:6F:72:1B:F1:83"
    B4 = "DC:04:2E:9D:49:62"

    address_beacons = [B1,B2,B3,B4]
    num_beacons = 4
    x_beacons = [5.36,5.35,2.95,6.7]
    y_beacons = [5.06,0.52,10.2,10.2]
    z_beacons = [2.2,1.9,1.9,1.9]

    return address_beacons,num_beacons,x_beacons,y_beacons


def func_boton_adj(): 
    global escaneo 
    if escaneo: 
        ui.notify("Ya está escaneando") 
        return 
    escaneo = True 
    ruta = 'archivos_adjuntos/escenario.xlsx' #Archivo de las coordenadas XY y RSSI de las muestras del FingerPrinting 
    df = pd.read_excel(ruta) 
    escenario = df.to_dict(orient='list') 
    address_beacons, num_beacons,x_beacons,y_beacons = obtener_arg_fp() 
    arg_fp = (address_beacons,num_beacons,escenario) 
    t3 = threading.Thread(target=simulacion_fingerprinting,args=arg_fp,daemon=True) 
    t3.start() 
    ui.notify("Iniciando escaneo...")

def func_boton_muestreo():
    global escaneo
    if escaneo: 
        ui.notify("Ya está escaneando")
        return
    
    escaneo = True
    muestras_pos = 'archivos_adjuntos/setup.xlsx' #Archivo de las coordenadas XY de las muestras del FingerPrinting

    address_beacons, num_beacons,x_beacons,y_beacons = obtener_arg_fp()
    escenario = muestreo()

    arg_fp = (address_beacons,num_beacons,escenario)
    t1 = threading.Thread(target=simulacion_fingerprinting,args=arg_fp,daemon=True)
    t1.start()


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
    j = indice[0]
    x_vecino.append(escenario['x'][j])
    y_vecino.append(escenario['y'][j])
    rssi_vecino.append([escenario[col][j] for col in columnas_rssi])

    return x_vecino,y_vecino


def simulacion_fingerprinting(address_beacons,num_beacons,escenario):

    address_indice = {addr: i for i, addr in enumerate(address_beacons)}
    rssi_n = np.zeros(num_beacons)
    array_rssi = [[] for i in range(num_beacons)]
    
    # Obtener el RSSI con respecto a las beacons y calcular la posición del nodo mediante la FingerPrinting
    # while True:
    #     for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
    scanner = ble.start_scan(ProvideServicesAdvertisement)
    for advertisement in scanner:
        if UARTService in advertisement.services:
            rssi = advertisement.rssi
            address = str(advertisement.address).split('"')[1]
            if address in address_beacons:
                indice = address_indice[address]
                array_rssi[indice].append(rssi)

                if sum(len(col) >= 5 for col in array_rssi)>=4:
                    for i in range(num_beacons):
                        datos = np.array(array_rssi[i])

                        # Filtro gaussiano para evitar fluctuaciones
                        aux = gaussian_filter(datos, sigma=1)
                        valores = np.sort(aux.flatten())
                        if len(valores) > 4: 
                            val=valores[2:-2]
                            media = np.mean(val)
                            rssi_n[i] = np.round(media,2)
                        else:
                            media = np.mean(valores)
                            rssi_n[i] = np.round(media,2)
                        array_rssi[i] = []
                    Xi,Yi = posicionamiento (rssi_n,escenario)
                    q1.put((rssi_n.copy(),Xi,Yi))



def actualizar_tabla_rssi():
    global puntos_beacons, puntos_acumulados

    if not q1.empty():
        rssi_n,Xi,Yi = q1.get()
        for i, rssi in enumerate(rssi_n):
            filas[i]['RSSI'] = rssi

        tabla.rows = list(filas)
        label_x.set_text(f'X: {Xi[0]:.2f} m')
        label_y.set_text(f'Y: {Yi[0]:.2f} m')
        px = (Xi[0] * 700)/10.72
        py = (Yi[0] * 699.283)/10.72
        x_svg, y_svg = ajuste(px, py)
        punto_nodo = f'<circle cx="{x_svg}" cy="{y_svg}" r="8" fill="blue" stroke="white" stroke-width="2" />'
        imagen_plano.content = puntos_beacons + punto_nodo
        puntos_acumulados += punto_nodo
        #imagen_plano.content = puntos_beacons + punto_nodo # Visualmente en movimiento
        imagen_plano.content = puntos_beacons + puntos_acumulados # Marcar  recorrido

def ajuste(x, y):
 
    w_img = 700
    h_img = 699.281
 
    w_img_real = 980
    h_img_real = 979
 
    # SVG para que la posición de los puntos estén en proporción a la imagen
    x_svg = x * w_img_real / w_img
    y_svg = y * h_img_real / h_img
 
    return x_svg, y_svg



def build_seccion_fingerprinting():
    global filas, tabla, label_x, label_y, x_beacons, y_beacons,imagen_plano,width, puntos_beacons
    width = '700px'

    address_beacons, num_beacons,x_beacons,y_beacons = obtener_arg_fp()
    filas = [
        {'Balizas': f'Baliza {i+1}', 'RSSI' : ''} for i in range(num_beacons)
        ]
    
    with ui.row().style("flex-wrap: nowrap; width: 100%").classes('gap-2'):
        with ui.column().classes('flex-[1]'):
            ui.label('FINGERPRINTING').classes('text-xl font-bold')
            
            ui.button('Cargar Fingerprinting', on_click=func_boton_adj)

            ui.button('Iniciar muestreo', on_click=func_boton_muestreo)

            ui.label('RSSI de las balizas detectadas')

            tabla = ui.table(
                columns=[
                    {'name':'Balizas','label':'Balizas','field':'Balizas'},
                    {'name':'RSSI','label':'RSSI','field':'RSSI'},
                ],
                rows=filas
            )
            ui.label('Posición estimada:')
            label_x = ui.label(f'X: -- m')
            label_y = ui.label(f'Y: -- m')

        with ui.column().classes('flex-[2]'):
            ui.label('SALA DE INNOVACIÓN').classes('text-lg')
            imagen_plano = ui.interactive_image('sala_innovacion.png').style(f'width: {width}')
            #height = obtener_height()
            puntos_beacons = ""
            for x, y in zip(x_beacons, y_beacons):
                px = (x * 700)/10.72
                py = (y * 699.283)/10.72
                x_svg, y_svg = ajuste(px, py)
                puntos_beacons += ''.join(f'<circle cx="{x_svg}" cy="{y_svg}" r="8" fill="red" stroke="white" stroke-width="2" />')
            imagen_plano.content = puntos_beacons

    ui.timer(0.1,actualizar_tabla_rssi)


