"""Functions to process the image."""
import numpy as np
from numpy.ma import masked_array

from skimage.morphology import diamond  # , disk
from skimage import morphology  # , filters

import matplotlib.pyplot as plt


def morp(arr, selema=diamond(8), selemb=diamond(4)):
    """Apply the morphology transformation over the image array."""
    # res = morphology.binary_(arr, selem=selema)
    # res = morphology.binary_opening(arr, selem=selema)
    res = morphology.binary_dilation(arr, selem=selemb)
    res = morphology.binary_closing(res, selem=selema)
    return res


def binarizacion(thresholds, out2, arreq, orig_array):
    """Binarize the image array to extract the ash object."""
    plt.figure()
    # rso = morp(np.logical_and(out2 < thr, out2>tl))
    thresh = thresholds[0]
    thr = thresh(out2)
    rso = morp(out2 < thr)
    rso = np.logical_or(morphology.binary_opening(arreq < 5,
                                                  diamond(2)), rso)
    rso = morphology.binary_dilation(rso, diamond(2))
    rso = morphology.binary_closing(rso, diamond(7))
    v1a = masked_array(arreq, rso)
    v1b = masked_array(orig_array, np.logical_not(rso))
    fig = plt.figure()
    plt.imshow(v1a, cmap='gray', interpolation='nearest')
    plt.imshow(v1b, cmap='Reds', interpolation='nearest')
    plt.title('Pluma Popocatepetl')
    plt.savefig('Pluma_popo_PRUEBA.png')
    plt.show()
    return fig
