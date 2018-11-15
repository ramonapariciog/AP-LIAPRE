import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import pickle

def min_max(array):
    return (np.min(array), np.max(array))

# Nombre de la tabla
# temporada = 'noviembre-junio'
temporada = 'julio-octubre'
ftemporada = temporada + '.csv'
sizes = pickle.load(open("binsize_temporadas.pck", "rb"))

# Carga la tabla
tabla = pd.read_csv(ftemporada, header=0, index_col=0)

# Coordenadas del volcan
volcan = [-98.62253, 19.02364]

# valores para longitud y latitud
latitudarray = tabla.latitud.values
longitudarray = tabla.longitud.values

# valores del histograma
histogramaarray = tabla.Probabilidad.values
latitudmm = min_max(latitudarray)
longitudmm = min_max(longitudarray)
longitudaxis = np.linspace(longitudmm[0], longitudmm[1], sizes[temporada]['long'][0]-1)
latitudaxis = np.linspace(latitudmm[0], latitudmm[1], sizes[temporada]['lat'][0]-1)

X, Y = np.meshgrid(longitudaxis, latitudaxis)

# Calcula el paso en longitud-latitud para poder calcular los puntos del volcan
# en la imagen
# pasolongitud = np.diff(longitudaxis).mean()
# pasolatitud = np.diff(latitudaxis).mean()

# Calcula el punto en pixeles de acuerdo a los limites de la imagen
# para el volcan
# pixx = (volcan[0] - longitudmm[0]) / pasolongitud
# pixy = (volcan[1] - latitudmm[0]) / pasolatitud

# Genera la grafica en contornos
plt.figure(figsize=(10, 10))
cm = plt.contourf(X, Y, histogramaarray.reshape(sizes[temporada]['H']),
                  cmap=plt.cm.Purples, vmin=0, vmax=histogramaarray.max()*0.9)
            #  locator=ticker.LogLocator(), cmap=plt.cm.PuBu_r)
plt.grid(alpha=0.6, linestyle='--')
plt.scatter(volcan[0], volcan[1], marker="^", color="g", s=80)
plt.title('Histograma temporada '+ temporada)
plt.colorbar(cm)
plt.savefig(temporada + '.png')
