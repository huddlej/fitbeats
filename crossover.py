"""
Crossover classes implementing various Crossover algorithms
"""
from random import random, randint
import sys

class Crossover(object):
    """
    Abstract base Crossover object contains standard methods 
    """
    def mate(self, parent1, parent2):
        """
        @param Organism parent1
        @param Organism parent2
        """
        raise Exception("mate method is not implemented.")

class OnePointCrossover(Crossover):
    """
    The simplest crossover.
    """
    def mate(self, parent1, parent2):
        x = len(parent1)
        crossPoint = randint(1, x - 1)

        child1, child2 = parent1.copy(), parent2.copy()
        
        temp = parent1[crossPoint:]
        child1[crossPoint:] = parent2[crossPoint:]
        child2[crossPoint:] = temp
        
        return (child1, child2)

class TwoPointCrossover(Crossover):
    """
    Based on the algorithm presented by Holland (1975) and Goldberg (1989b)
    """    
    def mate(self, parent1, parent2):
        pass

class PartExchangeCrossover(Crossover):
    def mate(self, parent1, parent2):
        # TODO: Rewrite for array data structure
        child1 = self.copy()
        child2 = partner.copy()
        
        # Select a random instrument to exchange
        instrument = randint(0, self.instrument_length - 1)
        
        # Calculate the range of genes represented by the chosen instrument row
        range_start = instrument * self.length
        range_end = (instrument + 1) * self.length
        
        for i in range(range_start, range_end):
            # Copy genes from partner sources
            child1.genes[str(i)], child2.genes[str(i)] = child2.genes[str(i)], child1.genes[str(i)]
            
        return (child1, child2)

class GroupPartExchangeCrossover(Crossover):
    def mate(self, parent1, parent2):
        # TODO: Rewrite for array data structure
        child1 = self.copy()
        child2 = partner.copy()

        # Select a random number of instrument to exchange        
        #totalExchange = randint(1, self.instrument_length)
        totalExchange = randint(1, self.instrument_length / 2)
        
        instrument_length = range(self.instrument_length)
        exchangeinstrument_length = []
        for i in range(totalExchange):
            index = randint(0, len(instrument_length) - 1)
            exchangeinstrument_length.append(instrument_length.pop(index))
        
        for instrument in exchangeinstrument_length:
            # Calculate the range of genes represented by the chosen instrument row
            range_start = instrument * self.length
            range_end = (instrument + 1) * self.length
            
            for i in range(range_start, range_end):
                # Copy genes from partner sources
                child1.genes[str(i)], child2.genes[str(i)] = child2.genes[str(i)], child1.genes[str(i)]
            
        return (child1, child2)
