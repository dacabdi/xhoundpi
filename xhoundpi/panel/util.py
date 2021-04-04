""" Smalle utilities to deal with panel related logic """

from typing import Tuple
import numpy as np

def copyto_withpos(dest: np.ndarray, src: np.ndarray, pos: Tuple[int, int]):
    """
    Copy numpy array with positioning and non-matching sizes
    """
    dest[pos[0]:pos[0]+src.shape[0], pos[1]:pos[1]+src.shape[1]] = src
    return dest
