import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
from skimage import filters
from osgeo import gdal
import pandas as pd

from ash_detect.clase_division import ConvCordinates

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

def open_image(stringName):
    folder = "img_modis"
    filepath = os.path.join(folder, stringName)
    dataset = gdal.Open(filepath, gdal.GA_ReadOnly)
    # nbands = [i for i in range(1, dataset.RasterCount + 1)]
    band = dataset.GetRasterBand(1)  # nbands[0])
    georef = dataset.GetGeoTransform()
    volcan = [-98.62253, 19.02364]
    lista = [-99, -96, 20.5, 17.5]
    conv = ConvCordinates(dataset)
    pixx, pixy, cosa, mat = list(conv.locationpoint(band, lista, volcan))
    keys = ["long0", "longStx", "longSty", "lat0", "latStx", "latSty"]
    grefs = dict(zip(keys, georef))
    array = band.ReadAsArray()
    rows, cols = band.YSize, band.XSize
    dimensions = dict(rows=rows, cols=cols)
    mask_rad = construct_mask(array, pixx, pixy)
    return array, grefs, dimensions, mask_rad

def correctNames(stname):
    return stname.replace("png.png", "")

def filter_image(array, func_trhesh, mask):
    pix_v = (array[array < 0]).ravel()
    vthre = func_trhesh(pix_v)
    binaryarray = array < vthre
    binaryarray = np.logical_and(binaryarray, mask)
    return binaryarray

def imgToDF(grefs, dimensions, binarimg, nombre):
    rows = dimensions["rows"]
    cols = dimensions["cols"]
    longitudes = np.arange(grefs['long0'],
                           grefs['long0'] + (cols * grefs['longStx']),
                           grefs['longStx'])
    latitudes = np.arange(grefs['lat0'],
                          grefs['lat0'] + (rows * grefs['latSty']),
                          grefs['latSty'])
    y,x = np.where(binarimg)
    data = np.hstack(tup=(x.reshape(-1,1), y.reshape(-1,1),
                          (longitudes[x]).reshape(-1,1),
                          (latitudes[y]).reshape(-1,1)))
    dfim = pd.DataFrame(columns=["pixx", "pixy", "longitud", "latitud"],
                      data=data)
    dfim["Nombre"] = nombre
    return dfim


df = pd.read_csv("figuras/calificaciones.txt", header=0)
df.Imagen = df.Imagen.apply(correctNames)
imagesb = df.loc[df.Calificacion == "Buena"]
threskey = ["isodata", "mean", "yen", "otsu"]
thresfunc = [filters.threshold_isodata,
             filters.threshold_mean,
             filters.threshold_yen,
             filters.threshold_otsu]
thres_dict = dict(zip(threskey, thresfunc))
for i, (image,thresk,_) in enumerate(imagesb.get_values()):
    array, gref, dimensions, mask = open_image(image)
    binaryimg = filter_image(array, thres_dict[thresk], mask)
    coord_dataframe = imgToDF(gref, dimensions, binaryimg, image)
    if i == 0:
        coord_dataframe.to_csv("dataimg.txt", header=True, mode="w")
    else:
        coord_dataframe.to_csv("dataimg.txt", header=False, mode="a")
