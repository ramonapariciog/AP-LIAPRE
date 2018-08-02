"""Improve the image object segments with RAG Filtering."""
import numpy as np
from skimage import color, segmentation  # , filters
from skimage.future import graph
import matplotlib.pyplot as plt


def muestra_banda(array):
    """Equalize the image histogram."""
    imflat = np.ravel(array)
    image_histogram, bins = np.histogram(imflat, 256, normed=True)
    cdf = image_histogram.cumsum()
    cdf = 255 * cdf / cdf[-1]
    image_equalized = np.interp(imflat, bins[:-1], cdf)
    image_equalized = image_equalized.reshape(array.shape)
    return image_equalized


def mejorar_pluma(array, n_segments=2000):
    """Function to improve the ash footprint shape with RAG filtering.

    Parameters
    --------------------------------------------------
    array :
       2D array image with nonzero values for all the pixels above 0.
    n_segments :
       Number of pixels for the RAG filtering. The value of 2000 is selected
       by empiricaly observation. More pixels during the rearrange values
    output
    --------------------------------------------------
    filtered array with the dilate-closed object.
    """
    # equalizar histograma para unicamente negativos
    arreq = muestra_banda(array).reshape(array.shape)
    arreq = arreq.astype(int)
    labels1 = segmentation.slic(arreq, compactness=30, n_segments=n_segments)
    out1 = color.label2rgb(labels1, arreq, kind='avg')
    gra = graph.rag_mean_color(arreq, labels1)
    labels2 = graph.cut_threshold(labels1, gra, 29)
    out2 = color.label2rgb(labels2, arreq, kind='avg')
    fig, axe = plt.subplots(nrows=2, sharex=True,
                            sharey=True, figsize=(6, 8))
    axe[0].imshow(out1)
    ma = axe[1].imshow(out2)
    fig.colorbar(ma)
    for a in axe:
        a.axis('off')
    plt.tight_layout()
    fig.show()
    return fig, out1, out2
    # Call the threshold methods
