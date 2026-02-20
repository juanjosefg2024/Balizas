import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rssi_trayectoria import calcular_rssi_nodo

def rejilla(largo, ancho,x_beacons,y_beacons):
    dens_puntos=0.2
    x=[]
    y=[]
    index_x=[]
    index_y=[]
    final_largo = largo+dens_puntos
    final_ancho = ancho+dens_puntos
    for i in np.arange(0,final_largo,dens_puntos):
        for j in np.arange(0,final_ancho,dens_puntos):
            x.append(round(i,2))
            y.append(round(j,2))
    
    for i in range(len(x)):
        for j in range(len(x_beacons)):
            if x[i] == x_beacons[j] and y[i] == y_beacons[j]:
                index_x.append(i)
                index_y.append(i)
    for i in sorted(index_x,reverse=True):
        del x[i]
        del y[i]
    return x,y

def beacons_pos(num_beacons,largo,ancho):



    x_beacons=[0,0,largo,largo]
    y_beacons=[0,ancho,0,ancho]

    if num_beacons > 4:
        for j in range(num_beacons-4):
            x_beacons.append(float(input(f"Coordenadas X de la baliza {j}: ")))
            y_beacons.append(float(input(f"Coordenadas Y de la baliza {j}: ")))

    else:
        x_beacons=x_beacons[:num_beacons]
        y_beacons=y_beacons[:num_beacons]

    return x_beacons,y_beacons

def crear_escenario():

    num_beacons=int(input("Número de balizas: "))
    largo = int(input("Longitud del largo del escenario: "))
    ancho = int(input("longitud del ancho del escenario: "))

    x_beacons,y_beacons = beacons_pos(num_beacons,largo,ancho)
    x_puntos,y_puntos = rejilla(largo, ancho,x_beacons,y_beacons)

    escenario = {
        'x' : x_puntos,
        'y' : y_puntos
    }
    for j in range (len(x_beacons)):
        escenario[f'RSSI{j}'] = []
    escenario = calcular_rssi_nodo(escenario,x_beacons,y_beacons)

    return escenario , x_beacons, y_beacons, largo, ancho

if __name__ == "__main__":
    escenario ,  x_beacons, y_beacons, largo, ancho = crear_escenario()