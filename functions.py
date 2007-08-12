"""
functions.py

Functions to measure actual fitness values and calculate expected values.
Functions prefaced by an "f" are fitness functions.
"""

from random import randint
from math import floor, ceil
from collections import deque

"""
Fitness Functions

Each of these functions calculates the actual fitness of a genetic individual
based on the individual's dimensions and the expected fitness based on
a joining function and its linear parameters, "a" and "b".
"""
    
def fTemporalBeatDensity(individual, ft):
    """
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """

    dimRow = individual.instrument_length
    dimCol = individual.length
    fitness = 0.0

    rowRange = xrange(dimRow)
    for columnIndex in xrange(dimCol):
        actualTotal = 0
        for rowIndex in rowRange:
            # Calculate actual values
            if(individual.genes[rowIndex][columnIndex].value > 0):
                actualTotal += 1

        #Calculate expected values
        expectedTotal = ft.values[columnIndex][1]
        fitness += (expectedTotal - actualTotal)**2
        #print "Expected: %i, Actual: %i" % (expectedTotal, actualTotal)
    return fitness

def fInstrumentBeatDensity(individual, ft):
    """
    Calculate beat density over the length of a pattern for each instrument.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """

    dimCol = individual.length
    fitness = 0.0
    
    columnRange = xrange(dimCol)
    for value in ft.values:
        rowIndex = value[0]
        expectedValue = value[1]
        actualValue = 0

        for columnIndex in columnRange:
            # Calculate actual values
            if(individual.genes[rowIndex][columnIndex].value > 0):
                actualValue += 1

        # Calculate fitness as square of the difference between expected and 
        # actual values.
        fitness += (expectedValue - actualValue)**2
        
    return fitness

def fUnison(individual, ft):
    """
    Determine the degree to which the requested number of instruments are
    not playing in unison.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """

    dimCol = individual.length
    fitness = 0.0    
    actualValue = 0

    value_count = len(ft.values)
    
    # If there is only one instrument, it is already in unison with itself.
    if value_count <= 1:
        return 0

    rows_a = xrange(value_count - 1)
    rows_b = xrange(1, value_count)
    for i in rows_a:
        row_a = ft.values[i]
        for j in rows_b:
            row_b = ft.values[j]
                
            for columnIndex in xrange(dimCol):
                # If value in instrument i is not the same as value in masterRow, 
                # decrease fitness by increasing total
                if individual.genes[row_a][columnIndex] != individual.genes[row_b][columnIndex]:
                    actualValue += 1

        # Calculate fitness as square of the difference between expected and 
        # actual values.
        expectedValue = 0
        fitness += (expectedValue - actualValue)**2

    return fitness

def fDoubleRhythms(individual, ft):
    """
    Determine the degree to which the requested number of instruments are
    not playing in double rhythm.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """
   
    dimRow = individual.instrument_length
    dimCol = individual.length
    fitness = 0.0

    unifiedInstruments = [int(i) for i in ft.rows.split(",")]
    masterRow = ft.masterRow

    if not masterRow in unifiedInstruments:
        unifiedInstruments.append(masterRow)

    # Calculate distances between beats for each instrument row
    distances = {}
    columnRange = xrange(dimCol)
    for instrumentRow in unifiedInstruments:
        distances[instrumentRow] = []
        count = 0
        
        for columnIndex in columnRange:
            beat = individual.genes[instrumentRow][columnIndex].toscalar()
            if beat:
                distances[instrumentRow].append(count)
                count = 0
                continue
            count += 1

    if len(distances[instrumentRow]) > 0:
        distances[instrumentRow][0] += count

    # Remove the master row from the list if it is listed
    try:
        index = unifiedInstruments.index(masterRow)
        unifiedInstruments.pop(index)
    except ValueError:
        pass

    # Compare each instrument row's beat spacings to the master row's
    actualValue = 0
    masterDistance = deque(distances[masterRow])
    
    for instrumentRow in unifiedInstruments:
        distance = deque(distances[instrumentRow])
        match = False
        for j in xrange(len(distance)):
            if j > 0:
                distance.rotate(1)
            
            if distance == masterDistance:
                match = True
                break
            
        if match:
            """
            print "Match!"
            print "---"
            print individual
            print distances
            """
            continue
        else:
            fitness += 2

    return fitness

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
