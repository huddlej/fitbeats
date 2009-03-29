"""
fitness.py

Fitness Functions

Each of these functions calculates the actual fitness of a genetic individual
based on the individual's dimensions and the expected fitness based on
a joining function and its linear parameters, "a" and "b".
"""

from random import randint
from math import floor, ceil
from collections import deque

def temporal_beat_density(individual, ft):
    """
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """
    dim_row = individual.instrument_length
    dim_col = individual.length
    fitness = 0.0

    row_range = xrange(dim_row)
    for column_index in xrange(dim_col):
        actual_total = 0
        for row_index in row_range:
            # Calculate actual values
            if(individual.genes[row_index][column_index].value > 0):
                actual_total += 1

        #Calculate expected values
        expected_total = ft.values[column_index][1]
        fitness += (expected_total - actual_total)**2
        #print "Expected: %i, Actual: %i" % (expected_total, actual_total)
    return fitness

def instrument_beat_density(individual, ft):
    """
    Calculate beat density over the length of a pattern for each instrument.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """
    dim_col = individual.length
    fitness = 0.0
    
    column_range = xrange(dim_col)
    for value in ft.values:
        row_index = value[0]
        expected_value = value[1]
        actual_value = 0

        for column_index in column_range:
            # Calculate actual values
            if(individual.genes[row_index][column_index].value > 0):
                actual_value += 1

        # Calculate fitness as square of the difference between expected and 
        # actual values.
        fitness += (expected_value - actual_value)**2
        
    return fitness

def unison(individual, ft):
    """
    Determine the degree to which the requested number of instruments are
    not playing in unison.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """
    dim_col = individual.length
    fitness = 0.0    
    actual_value = 0

    value_count = len(ft.values)
    
    # If there is only one instrument, it is already in unison with itself.
    if value_count == 1:
        return 0

    rows_a = xrange(value_count - 1)
    rows_b = xrange(1, value_count)
    for i in rows_a:
        row_a = ft.values[i]
        for j in rows_b:
            row_b = ft.values[j]
                
            for column_index in xrange(dim_col):
                # If value in instrument i is not the same as value in master_row, 
                # decrease fitness by increasing total
                if individual.genes[row_a][column_index] != individual.genes[row_b][column_index]:
                    actual_value += 1

        # Calculate fitness as square of the difference between expected and 
        # actual values.
        expected_value = 0
        fitness += (expected_value - actual_value)**2

    return fitness

def double_rhythms(individual, ft):
    """
    Determine the degree to which the requested number of instruments are
    not playing in double rhythm.
    
    @param PatternOrganism individual
    @param FitnessTrajectory ft
    """
    dim_row = individual.instrument_length
    dim_col = individual.length
    fitness = 0.0

    unified_instruments = [int(i) for i in ft.rows.split(",")]
    master_row = ft.master_row

    if not master_row in unified_instruments:
        unified_instruments.append(master_row)

    # Calculate distances between beats for each instrument row.
    distances = {}
    column_range = xrange(dim_col)
    for instrument_row in unified_instruments:
        distances[instrument_row] = []
        count = 0
        
        for column_index in column_range:
            beat = individual.genes[instrument_row][column_index].toscalar()
            if beat:
                distances[instrument_row].append(count)
                count = 0
                continue
            count += 1

    if len(distances[instrument_row]) > 0:
        distances[instrument_row][0] += count

    # Remove the master row from the list if it is listed
    try:
        index = unified_instruments.index(master_row)
        unified_instruments.pop(index)
    except ValueError:
        pass

    # Compare each instrument row's beat spacings to the master row's
    actual_value = 0
    master_distance = deque(distances[master_row])
    
    for instrument_row in unified_instruments:
        distance = deque(distances[instrument_row])
        match = False
        for j in xrange(len(distance)):
            if j > 0:
                distance.rotate(1)
            
            if distance == master_distance:
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

if __name__ == "__main__":
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = "fitbeat_project.settings"
    import doctest
    doctest.testmod()
    
