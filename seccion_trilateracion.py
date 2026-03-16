
from nicegui import ui
import numpy as np
import threading
import queue
from scipy.ndimage import gaussian_filter
import configparser
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

q = queue.Queue()
escaneo = False
ble = BLERadio()
puntos_beacons2 = ""
punto_nodo2 = ""
puntos_acumulados2 = ""

def obtener_arg_tri():

    # Usar archivo config.ini para la modificación de los valores de las variables
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # address_beacons = list(config['beacons_add'].values())
    # num_beacons = int(config['beacons_pos']['num_beacons'])
    # x_beacons = [float(x) for x in config['beacons_pos']['x_beacons'].split(',')]
    # y_beacons = [float(y) for y in config['beacons_pos']['y_beacons'].split(',')]
    # z_beacons = [float(z) for z in config['beacons_pos']['z_beacons'].split(',')]
    # txpower = float(config['datos']['txpower'])
    # n = float(config['datos']['n'])

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

    txpower=-65
    n=1.8
    arg_tri = (address_beacons,num_beacons,x_beacons,y_beacons,z_beacons,txpower,n)
    return arg_tri


def trilateracion_3d(rssi_n,x_beacons,y_beacons,z_beacons,txpower,n):

    xi=[]
    yi=[]
    zi=[]
    ri=[]


    indice = np.nanargmax(rssi_n)
    r0 = 10**((txpower-rssi_n[indice])/(10*n))
    x0, y0, z0 = x_beacons[indice], y_beacons[indice], z_beacons[indice]

    for i in range(len(x_beacons)):
        if i != indice and not np.isnan(rssi_n[i]):
            xi.append(x_beacons[i])
            yi.append(y_beacons[i])
            zi.append(z_beacons[i])
            d = (10**((txpower-rssi_n[i])/(10*n)))
            ri.append(d)

    xi = np.array(xi)
    yi = np.array(yi)
    zi = np.array(zi)
    ri = np.array(ri)
    
    A = np.column_stack([2*(xi - x0), 
                         2*(yi - y0),
                         2*(zi - z0),
                         ])
    B = (xi**2 + yi**2 + zi**2 - ri**2) - (x0**2 + y0**2 + z0**2 - r0**2)

    posiciones, residuals, rank, s  = np.linalg.lstsq(A, B, rcond=None)
    return posiciones[0],posiciones[1],posiciones[2]


def func_boton():
    global escaneo
    
    if escaneo:
        ui.notify("Ya está escaneando")
        return
    
    escaneo = True
    arg_tri = obtener_arg_tri()
    t2 = threading.Thread(target=simulacion_trilateracion,args=arg_tri,daemon=True)
    t2.start()
    ui.notify("Empieza a escanear")


def simulacion_trilateracion(address_beacons,num_beacons,x_beacons,y_beacons,z_beacons,txpower,n):


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
                        Xi,Yi,Zi = trilateracion_3d (rssi_n,x_beacons,y_beacons,z_beacons,txpower,n)
                        q.put((rssi_n.copy(),Xi,Yi))


def actualizar_tabla_rssi():
    global puntos_beacons2, puntos_acumulados2

    if not q.empty():
        rssi_n,Xi,Yi = q.get()
        for i, rssi in enumerate(rssi_n):
            filas[i]['RSSI'] = rssi

        tabla.rows = list(filas)
        label_x.set_text(f'X: {Xi:.2f} m')
        label_y.set_text(f'Y: {Yi:.2f} m')
        px2 = (Xi * 700)/10.72
        py2 = (Yi * 699.283)/10.72
        x_svg2, y_svg2 = ajuste(px2, py2)
        punto_nodo2 = f'<circle cx="{x_svg2}" cy="{y_svg2}" r="8" fill="blue" stroke="white" stroke-width="2" />'
        puntos_acumulados2 += punto_nodo2
        #imagen_plano.content = puntos_beacons2 + punto_nodo2
        imagen_plano.content = puntos_beacons2 + puntos_acumulados2



def ajuste(x, y):
 
    w_img = 700
    h_img = 699.281
 
    w_img_real = 980
    h_img_real = 979
 
    # SVG para que la posición de los puntos estén en proporción a la imagen
    x_svg = x * w_img_real / w_img
    y_svg = y * h_img_real / h_img
 
    return x_svg, y_svg
 


def build_seccion_trilateracion():
    global filas, tabla, label_x, label_y, x_beacons, y_beacons,imagen_plano,width, puntos_beacons2
    width = '700px'

    address_beacons,num_beacons,x_beacons,y_beacons,z_beacons,txpower,n = obtener_arg_tri()

    filas = [
        {'Balizas': f'Baliza {i+1}', 'RSSI' : ''} for i in range(num_beacons)
        ]
    
    with ui.row().style("flex-wrap: nowrap; width: 100%").classes('gap-2'):
        with ui.column().classes('flex-[1]'):

            ui.label('TRILATERACIÓN').classes('text-xl font-bold')

            ui.button('Iniciar posicionamiento', on_click=func_boton)

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
            puntos_beacons2 = ""
            for x, y in zip(x_beacons, y_beacons):
                px = (x * 700)/10.72
                py = (y * 699.283)/10.72
                x_svg, y_svg = ajuste(px, py)
                puntos_beacons2 += ''.join(f'<circle cx="{x_svg}" cy="{y_svg}" r="8" fill="red" stroke="white" stroke-width="2" />')
            imagen_plano.content = puntos_beacons2

    ui.timer(0.1,actualizar_tabla_rssi)


