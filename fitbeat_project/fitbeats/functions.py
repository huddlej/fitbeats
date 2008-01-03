"""
functions.py

Joining functions and helper functions.
"""

from random import randint
from math import floor, ceil
from collections import deque

"""
Joining Functions

These are simple mathematical functions linearly parameterized by 
the constants "a" and "b" which shift the function domain to fit the user's
requested initial and final fitness values.
"""
    
def bezier(p0, p1, p2, p3, t):
    """
    @param p0
    @param p1
    @param p2
    @param p3
    @param t
    """
    #calculate the polynomial coefficients
    cx = 3.0 * (p1[0] - p0[0])
    bx = 3.0 * (p2[0] - p1[0]) - cx
    ax = p3[0] - p0[0] - cx - bx
        
    cy = 3.0 * (p1[1] - p0[1])
    by = 3.0 * (p2[1] - p1[1]) - cy
    ay = p3[1] - p0[1] - cy - by
        
    # calculate the curve point at parameter value t
    tSquared = t * t
    tCubed = tSquared * t
    
    x = (ax * tCubed) + (bx * tSquared) + (cx * t) + p0[0]
    y = (ay * tCubed) + (by * tSquared) + (cy * t) + p0[1]
    result = (x, y)

    return result

"""
Helper functions
"""

def calculate_magnitude(d):
    dmagnitude = 0
    for i in d:
       dmagnitude += i**2
    dmagnitude = dmagnitude ** 0.5
    
    return dmagnitude
    
def normalize(d):
    dnorm = []
    dmagnitude = calculate_magnitude(d)
    
    for i in d:
       dnorm.append(float(i) / dmagnitude)
    
    return dnorm

def calculate_cos(x, y):
    """
    Calculate the cosine simlarity between two vectors
    
    @param list x
    @param list y
    @return float cos the cosine similarity between the two vectors
    """
    x = normalize(x)
    y = normalize(y)
    
    cos = 0
    for key in xrange(len(x)):
        x_i = x[key]
        y_i = y[key]
        cos += x_i*y_i
    
    return cos
    
def similarity(x, y):
    return calculate_cos(x, y)
