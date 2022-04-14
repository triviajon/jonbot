# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 19:55:28 2021

@author: jon-f
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from skimage.transform import resize

def binary_array_to_hex(arr):

	bit_string = ''.join(str(int(b)) for b in arr.flatten())
	width = int(np.ceil(len(bit_string)/4))
	return '{:0>{width}x}'.format(int(bit_string, 2), width=width)

def image_to_edgehex(numpy_image):
    numpy_array = resize(numpy_image, (64, 64))
    
    size = numpy_array.shape
    grayscale = np.zeros(size[:-1])
    grayscale1der = np.zeros(size[:-1])
    
    for i in range(size[0]):
        for j in range(size[1]):
            
            if size[2] == 4:
                val = numpy_array[i, j]
                n_val = (0.299*val[0]+0.587*val[1]+0.114*val[2])*val[3]
            elif size[2] == 3:
                val = numpy_array[i, j]
                n_val = 0.299*val[0]+0.587*val[1]+0.114*val[2]
            else:
                n_val = numpy_array[i, j]
            
            grayscale[i, j] = n_val
            
            if i == 0 or j == 0:
                continue
            
            sub = grayscale[i-1:i+1, j-1:j+1]
            
            dIdx = 1/2 * ((sub[0, 1] - sub[0, 0]) + (sub[1, 1] - sub[1, 0]))
            dIdy = 1/2 * ((sub[1, 0] - sub[0, 0]) + (sub[1, 1] - sub[0, 1]))
            
            dIdp = abs(dIdx/2 + dIdy/2)
            if dIdp < 0.03:
                continue
            
            grayscale1der[i, j] = 1
        
    return binary_array_to_hex(grayscale1der)

def dilate(image_file):
    numpy_array = resize(image_file, (64, 64))
    
    size = numpy_array.shape[:-1]
    dilated = np.zeros(size)
    
    for i in range(size[0]):
        for j in range(size[1]):
            
            sub = image_file[i-1:i+1, j-1:j+1]
    
            if (sub == 1).any():
                dilated[i, j] = 1
    return dilated

def hamming_distance(hash1, hash2):
    dist = sum(n1 != n2 for n1, n2 in zip(hash1, hash2))
    return dist

def hash_match(hash1, hash2, percent_match=60):
    # returns True if at least percent_match % 
    return hamming_distance(hash1, hash2)/len(hash1) < percent_match/100