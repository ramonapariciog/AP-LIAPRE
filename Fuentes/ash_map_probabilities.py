import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import re
import time

def get_date(nombre, campo="mes"):
    pattern = r"\d{4}"
    tiempo = re.findall(pattern=pattern, string=nombre)
    fechast = "-".join(tiempo)
    tstruct = time.strptime(fechast, "%d%m-%Y-%H%M")
    if campo == "mes":
        return int(time.strftime("%m", tstruct))
    elif campo == "day":
        return int(time.strftime("%d", tstruct))
    elif campo == "year":
        return int(time.strftime("%Y", tstruct))


cmap = matplotlib.cm.autumn
cmap_reversed = matplotlib.cm.get_cmap('autumn_r')
plt.ion()
tabla = pd.read_csv("dataimg.txt", header=0, index_col=0)
imags = tabla.Nombre.unique()
grupos = tabla.groupby(["Nombre"])
malas = []
zonas = []
for nim in imags:
    zona = tabla.iloc[grupos.indices[nim]]
    try:
        zona["mes"] = get_date(nim)
        zona["day"] = get_date(nim, "day")
        zona["year"] = get_date(nim, "year")
        zonas.append(zona)
    except ValueError:
        malas.append(nim)
zonas = pd.concat(zonas)
zonas.reset_index(inplace=True)
julio_octubre = np.logical_and(zonas.mes.values > 6, zonas.mes.values < 11)
noviembre_junio = np.logical_not(julio_octubre)
fig, axes = plt.subplots(2, 2, figsize=(15,15))
axes = axes.reshape(-1,)
colors = ["r", "b"]
for i, coord in enumerate(zonas.columns[3:5]):
    axes[i * 2].hist(zonas[coord].values[julio_octubre],
                     bins=200, normed=True, color=colors[i])
    axes[i * 2].set_title("julio - octubre {0}".format(coord))
    axes[(i * 2) + 1].hist(zonas[coord].values[noviembre_junio],
                           bins=200, normed=True, color=colors[i])
    axes[(i * 2) + 1].set_title("noviembre - junio {0}".format(coord))
fig.suptitle("Histogramas de las zonas con permanencia de ceniza", fontsize=18)
fig.savefig("Histogramas_coordenadas.png")
plt.show()

volcan = [-98.62253, 19.02364]
fig2, axes = plt.subplots(1, 2, figsize=(13, 7))
axes = axes.reshape(-1,)
temporadas = [julio_octubre, noviembre_junio]
titles = ["julio-octubre", "noviembre-junio"]
Hs = {}
for i, temporada in enumerate(temporadas):
    H, longitud, latitud = np.histogram2d(zonas.longitud.values[temporada],
                                          zonas.latitud.values[temporada],
                                          bins=400,
                                          range=None, normed=None, weights=None)
    cm = axes[i].hist2d(zonas.longitud.values[temporada],
                        zonas.latitud.values[temporada], normed=True,
                        bins=400, cmap=plt.cm.Purples, vmin=0, vmax=0.8)
    # H, longitud, latitud = np.histogram2d(zonas.longitud.values[temporada],
    #                                       zonas.latitud.values[temporada],
    #                                       bins=400, normed=True)
    axes[i].grid(linestyle="--", color="b", linewidth=0.5, alpha=0.7)
    axes[i].scatter(volcan[0], volcan[1], marker="o", color="g", s=40)
    axes[i].set_title(titles[i], fontsize=14)
    latitudarray = np.repeat(latitud[:-1], 400)
    longitudarray = np.tile(longitud[:-1], 400)
    histogramaarray = H.ravel()
    dataprob = np.hstack(tup=(histogramaarray.reshape(-1,1),
                              longitudarray.reshape(-1,1),
                              latitudarray.reshape(-1,1)))
    df = pd.DataFrame(data=dataprob,
                      columns=["Probabilidad", "longitud", "latitud"])
    df.to_csv(titles[i]+".csv")
    Hs.update({titles[i]: {"dataframe": df}})
cax,kw = mpl.colorbar.make_axes([ax for ax in axes])
plt.colorbar(cm[3], cax=cax, **kw)
fig2.suptitle("Histogramas bidimensionales de zona con permanencia de ceniza",
              fontsize=18)
fig2.savefig("Histogramas2D_coordenadas.png")
plt.show()
plt.figure()
plt.hist2d(zonas.longitud.values[julio_octubre], zonas.latitud.values[julio_octubre])
plt.figure()
plt.hist2d(zonas.longitud.values[noviembre_junio], zonas.latitud.values[noviembre_junio])
plt.show()
