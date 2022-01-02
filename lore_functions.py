# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 10:21:45 2021

@author: jon-f
"""

from skimage.transform import resize
import numpy as np
import datetime as dt
import string
import csv

datafile = 'jonbot.csv'


# checks if msg is of format "-lore mm/dd/year text......"
def isLoreFormat(msg):
    checkedN = [msg[6:8], msg[9:11], msg[12:16]]
    try:
        checkedS = [msg[5], msg[16]]
    except IndexError:
        checkedS = [msg[5]]
    flag = True
    for text in checkedN:
        if not text.isnumeric():
            flag = False
    for text in checkedS:
        if text != ' ':
            flag = False
    return flag

# checks if msg is of format "-lookup mm/dd/yyyy mm/dd/yyyy"
def isDateLookupFormat(msg):
    checkedN = [msg[8:10], msg[11:13], msg[14:18], msg[19:21], msg[22:24], msg[25:29]]
    checkedS = [msg[7], msg[18]]
    flag = True
    for text in checkedN:
        if not text.isnumeric():
            flag = False
    for text in checkedS:
        if text != ' ':
            flag = False
    return flag

def textToDTObj(text):
    # converts mm/dd/yyyy to datetime obj
    dtobj = dt.datetime.strptime(text, '%m/%d/%Y')
    return dtobj

def extractDates(msg):
    # gets lookup command and returns the two dates
    t1 = textToDTObj(msg[8:18])
    t2 = textToDTObj(msg[19:29])
    return t1, t2

def prepare(plaintext):
    stripped = plaintext.translate(str.maketrans('', '', string.punctuation))\
        .lower()
    return stripped

# comomands for image hexing
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

def hamming_distance(hash1, hash2):
    dist = sum(n1 != n2 for n1, n2 in zip(hash1, hash2))
    return dist

def hash_match(hash1, hash2, percent_match=.6):
    # returns True if at least percent_match % 
    if len(hash1) == 0 or len(hash2) == 0:
        return (False, 0)
    result = 1-hamming_distance(hash1, hash2)/len(hash1)
    return result > percent_match, result

def generateUID(UIDlen=5):

    reader = csv.reader(open(datafile))
    currentUIDs = []
    for line in reader:
        try:
            currentUIDs.append(line[5])
        except:
            pass
    
    rng = np.random.default_rng()
    letters = list(string.ascii_uppercase)
    UID = ''.join(rng.choice(letters, size=UIDlen))
    
    while UID in currentUIDs:
        UID = ''.join(rng.choice(letters, size=UIDlen))

    return UID