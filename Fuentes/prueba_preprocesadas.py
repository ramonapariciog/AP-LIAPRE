"""Ash detection over raster files."""
import os
import sys
import re
import numpy as np
from numpy.ma import masked_array
from osgeo import gdal
from osgeo import gdalconst
from osgeo.gdalconst import *
import matplotlib.pyplot as plt

driver = gdal.GetDriverByName("GTiff")
driver.Register()


# from matplotlib import colors
# from skimage.filters import try_all_threshold
from skimage.filters import (threshold_yen, threshold_isodata,
                             threshold_mean, threshold_otsu)
from libs import ConvCordinates, morp  # , binarizacion
def construct_mask(array, pxx, pxy, radio=200):
    """Construye zona de cercania al volcan.
    Parametros:
    radio -  int millas nauticas.
    """
    radio_milla = radio  # millas marinas
    pixel_lenght = 1e3  # metros
    millan = 1.852e3
    radio_m = radio_milla * millan
    radio_pix = radio_m / pixel_lenght
    mask = np.zeros(array.shape)
    for i, row in enumerate(array):
        for j, px in enumerate(row):
            rad = np.sqrt((pxy - i)**2 + (pxx - j)**2)
            rad = rad.astype(int)
            if rad < radio_pix:
                mask[i, j] = 1
    return mask.astype(bool)

def graficar(**kwargs):
    """Grafica las imagenes."""
    pixx = kwargs.get('pixx')
    pixy = kwargs.get('pixy')
    coordsx = kwargs.get('coordsx')
    coordsy = kwargs.get('coordsy')
    flatmat = kwargs.get('flatmat')
    vthre = kwargs.get('vthre')
    img_binaria = kwargs.get('img_binaria')
    mask_rad = kwargs.get('mask_rad')
    img_name = kwargs.get('img_name')

    fig, axes = plt.subplots(1, 2, figsize=(21,11))
    axes = axes.reshape(-1,)
    hx, hy, hz = axes[0].hist(flatmat[flatmat < 0], bins=50)
    axes[0].set_title("a) Histograma", fontsize=18)
    for tick in axes[0].xaxis.get_major_ticks():
        tick.label.set_fontsize(18)
    for tick in axes[0].yaxis.get_major_ticks():
        tick.label.set_fontsize(18)
    axes[0].vlines(x=vthre, ymin=0, ymax=hx.max(), linestyle='-.',
                   color='brmc'[1], label="Umbral de media", alpha=0.5)
    axes[0].legend(fontsize=18)
    axes[0].set_ylabel("$p(pi_{ij})$", fontsize=18)
    axes[0].set_xlabel("$pi_{ij}$", fontsize=18)

    va = masked_array(mat, img_binaria)
    vb = masked_array(mat, np.logical_not(img_binaria))

    axes[1].scatter(x=pixx, y=pixy, s=100, c='green', marker="^")
    cm = axes[1].imshow(va, cmap='gray')
    axes[1].imshow(vb, cmap='Reds')
    #cm = axes[0].imshow(mat, cmap='gray')
    axes[1].set_xticks(np.linspace(0, mat.shape[1], 7))
    axes[1].set_xticklabels(["%.3f" % c for c in np.linspace(coordsx[0], coordsx[1], 7)],
                            fontsize=16, rotation=60)
    axes[1].set_yticks(np.linspace(0, mat.shape[0], 7))
    axes[1].set_yticklabels(['%.3f' % c for c in np.linspace(coordsy[0], coordsy[1], 7)],
                            fontsize=16)
    axes[1].grid(color="gray", alpha=0.7)
    axes[1].set_title("b) Imagen Binarizada, dilatada y cerrada", fontsize=16)
    fig.colorbar(cm, ax=axes[1], orientation="horizontal")
    fig.tight_layout()
    fig.savefig(os.path.join(folder_png, img_name + ".png"))
    plt.close(fig)

# para correr:
# python preprocesamiento ../img_modis
# python preprocesamiento /home/pr/Escritorio/proyecto_ceniza/img_modis
#if len(sys.argv) > 1:
#    folder = sys.argv[1]
#else:
#    folder = "../MODIS_COLIMA"

ruta = 'C:/Users/CARLOS/Documents/ESIME/TESIS/MODIS_COLIMA'
directorios1n = [f for f in os.listdir(ruta)
                 if os.path.isdir(os.path.join(ruta, f))]
patron = "^(MOD|mod).*B3.mB3.$"

listarutas= []
for dir1 in directorios1n:
    concatenado = os.path.join(ruta, dir1)
    directorios2 = os.listdir(concatenado)
    for dir2 in directorios2:
        concatenados2 = os.path.join(concatenado, dir2)
        directorios3 = os.listdir(concatenados2)
        for dir3 in directorios3:
            concate3 = os.path.join(concatenados2, dir3)
            if os.path.isdir(concate3):
                imagns = [f for f in os.listdir(concate3)
                          if re.match(pattern=patron, string=f) is not None]
                for imag in imagns:
                    listarutas.append(os.path.join(concate3, imag))
# La carpeta que almacena las figuras a evaluar
# -------------------------------------------------
folder_png = "../procesadas"
if not os.path.exists(folder_png):
    os.mkdir(folder_png)
# -------------------------------------------------

# para la seleccion de las imagenes que cumplan la convencion de nombres
# modDDMM_AAAA_HHmm_b31mb32
# -------------------------------------------------
# patron = r'(mod|MOD)+[\d\w]+'
# files = [f for f in os.listdir(folder)
#          if (re.match(pattern=patron, string=f) is not None) and (f[-3:] not in ["hdr", "hdf", "HDF", "HDR"])]
# print(files)

#ruta = 'C:/Users/CARLOS/AP-LIAPRE/img_modis'

#
print("Leyendo ", len(listarutas), " imagenes")
#print("Leyendo {0} imagenes".format(tama))
#print("Leyendo %s %s de %d imagenes"%(tama, fil, cosa))
lenfiles = len(listarutas)
# Guarda los mensajes de error en tiempo de ejecucion
# --------------------------------------------------
logerror = open('logerror.txt', 'w')
# --------------------------------------------------
# print('Imagen {0}  {1} de {2}'.format(f, i, lenfiles))
# f = files[3]
for i_f, f in enumerate(listarutas):
    try:
        imag = gdal.Open(f, GA_ReadOnly)
        band = imag.GetRasterBand(1)
        conv = ConvCordinates(imag)
        # ***********************************************************
        # nota:
        # modificar clase para quitar lo de las coordenadas limite
        # ***********************************************************
        # lista = [-99, -96, 20.5, 17.5]  # Popocatepetl, alrededores
        lista = [-104.11, -103, 20, 19]  # Colima, alrededores
        # volcan = [-98.62253, 19.02364] # punto del Popocatepetl
        volcan = [-103.61, 19.51]  # punto del Colima

        # coordenadas de volcan en imagen pixx y pixy
        pixx, pixy, cosa, mat = list(conv.locationpoint(band, lista,
                                                        volcan))

        # coordenadas limite de la imagen
        coordsx, coordsy = conv.band_limits()

        # pixeles que no tengan infinito como valor
        inds_fine = np.logical_not(np.isnan(mat.ravel()))  # retirar nan

        # se hace unidimensional y se filtran los valores con infinito para
        # calcular el histograma
        flatmat = mat.ravel()[inds_fine]

        # Solo los valores menores a cero (SPLIT Window)
        pix_v = flatmat[flatmat < 0]

        # se calcula el umbral de media con los valores menores a cero
        vthre = threshold_mean(pix_v)

        # Se discriminan los pixeles por debajo del umbral, i.e., mat< vthre
        # son los pixeles de ceniza
        img_binaria = morp(mat < vthre)

        # Se construye la mascara de radio de 200 mn
        mask_rad = construct_mask(mat, pixx, pixy)

        # Se aṕlica la mascara a la imagen binarizada con el umbral
        img_binaria = np.logical_and(img_binaria, mask_rad)

        # para graficar
        # --------------------------------------------------------------
        params = dict(pixx=pixx, pixy=pixy, coordsx=coordsx, coordsy=coordsy,
                      flatmat=flatmat, vthre=vthre, img_binaria=img_binaria,
                      mask_rad=mask_rad, img_name=f.split("\\")[-1])

        graficar(**params)
        # --------------------------------------------------------------
        # import pickle
        # Salvar un objeto a un archivo binario
        # pickle.dump(params, open("params.pck", "wb"))

        # Leer un objeto guardado en un archivo binario
        # params = pickle.load(open("params.pck", "rb"))

        print("{0} de {1}".format(i_f, lenfiles))
    except Exception as err:
        # Esto es solo para evaluar si hubo errores en el proceso
        logstr = 'Error con imagen {0} {1} de {2}: {3}'.format(f, i_f, lenfiles,str(err).upper())
        print(logstr)
        logerror.write(logstr + '\n')
        continue
logerror.close()
