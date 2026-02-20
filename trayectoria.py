
import numpy as np
import matplotlib.pyplot as plt


def recorrido(largo, ancho, paso):

    x = []
    y = []

    xmin = 0.25
    xmax = largo - 0.25
    ymin = 0.25
    ymax = ancho - 0.25

    for xi in np.arange(xmin, xmax + paso, paso):
        x.append(round(xi, 3))
        y.append(round(ymin, 3))

    for yi in np.arange(ymin + paso, ymax + paso, paso):
        x.append(round(xmax, 3))
        y.append(round(yi, 3))

    for xi in np.arange(xmax - paso, xmin - paso, -paso):
        x.append(round(xi, 3))
        y.append(round(ymax, 3))

    for yi in np.arange(ymax - paso, ymin, -paso):
        x.append(round(xmin, 3))
        y.append(round(yi, 3))

    xcentro = largo / 2
    ycentro = ancho / 2

    for d in np.arange(0.5, min(xcentro, ycentro), paso):
        x.append(round(d, 3))
        y.append(round(d, 3))

    x0 = round(xcentro, 3)
    y0 = round(ycentro, 3)

    x.append(x0)
    y.append(y0)

    x.append(x0)
    y.append(y0 + 1)

    x.append(x0 + 1)
    y.append(y0 + 1)

    x.append(x0 + 1)
    y.append(y0)

    x.append(x0)
    y.append(y0)

    return x, y