"""Contains the class to subset the selected area of the raster file."""
import numpy as np


class ConvCordinates:
    """Coordinates to slice array class."""

    def __init__(self, imag):
        """Create the dictionary.

        Dictionary longitude and latitude origin and step in image.
        From the official site:
        --------------------------------------------------------------
        Xp = padfTransform[0] + P*padfTransform[1] + L*padfTransform[2]
        Yp = padfTransform[3] + P*padfTransform[4] + L*padfTransform[5]
        where P is for pixel and L for line
        --------------------------------------------------------------

        Parameters
        imag : gdal image object.
        """
        coordsval = np.asarray(imag.GetGeoTransform())
        coords = dict(lono=coordsval[0], lato=coordsval[3],
                      lonst=coordsval[1], latst=coordsval[5])
        coords.update(dict(ncols=imag.RasterXSize,
                           nrows=imag.RasterYSize))
        self.coords = coords

    def calcmatlims(self, coordd, cols=True):
        """Calcule the pixel limits from longitude or latitude.

        Parameters
        ----------------------------------------------------
        coordd : dictionary with the coordinates points asked to
                 transform to pixels.
        cols : boolean, True for columns by default.
        output
        ----------------------------------------------------
        limsarr : dictionary with the limit pixels correspondant to
                  the geo coordinates in image.
        """
        coords = self.coords
        if cols:
            ncols = (coordd['lons'] - coordd['lono']) / coords['lonst']
            inicol = (coordd['lono'] - coords['lono']) / coords['lonst']
            limsarr = dict(inicol=int(inicol), endcol=int(inicol + ncols))
        else:
            nrows = (coordd['lats'] - coordd['lato']) / coords['latst']
            inirow = (coordd['lato'] - coords['lato']) / coords['latst']
            limsarr = dict(inirow=int(inirow), endrow=int(inirow + nrows))
        return limsarr

    def coords2pixels(self, band, coordlist):
        """Convert coordinates to pixel index and return array.

        Parameters
        __________
        coordict : coord dictionary with the innitial-final
                   latitude, and longitude
        band : Raster band to analyse

        Returns
        __________
        numpy array with data band.
        """
        labels = ['lono', 'lons', 'lato', 'lats']
        cdict = dict(zip(labels, coordlist))
        array = band.ReadAsArray()
        rows = self.calcmatlims(cdict, False)
        cols = self.calcmatlims(cdict)
        return array, rows, cols

    def locationpoint(self, band, limits, point, slicmark=False):
        """Get the point over the subset array from longitude and latitude."""
        coords = self.coords
        pixx = (point[0] - coords['lono']) / coords['lonst']
        pixy = (point[1] - coords['lato']) / coords['latst']
        array, ro, co = self.coords2pixels(band, limits)
        sliced = array[ro['inirow']:ro['endrow'],
                       co['inicol']:co['endcol']]
        if slicmark:
            pixx = pixx - co['inicol']
            pixy = pixy - ro['inirow']
        return pixx, pixy, sliced, array

    def band_limits(self):
        """Get the image square limits."""
        coords = self.coords
        px = lambda x: coords['lono'] + coords['lonst'] * x
        py = lambda x: coords['lato'] + coords['latst'] * x
        limsx = [coords['lono'], px(coords['ncols'])]
        limsy = [coords['lato'], py(coords['nrows'])]
        return limsx, limsy
