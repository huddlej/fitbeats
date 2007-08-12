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
