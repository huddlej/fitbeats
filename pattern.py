"""
pattern.py

Represents all elements population of organisms:

 * Gene
 * Organism
 * Population
"""
import Numeric
import copy
from random import random, choice
from pygene.gene import IntGene
from pygene.organism import Organism
from pygene.population import Population
from functions import *
from mutator import *
from hydrogen import savePatternToXml

class PatternGene(IntGene):
    mutProb = 0.02
    
    randMin = 0
    randMax = 1

    def __repr__(self):
        return str(self.value)
        
    def __cmp__(this, other):
        if isinstance(other, int):
            return cmp(this.value, other)
        else:
            return cmp(this.value, other.value)
        
class PatternOrganism(Organism):    
    def __init__(self, **kw):
        self.mutProb = 0.02
        self.crossoverRate = 0.9
        self.partExchangeProb = 0

        self.genes = Numeric.array([[self.gene() 
                                    for i in xrange(self.length)]
                                    for j in xrange(self.instrument_length)], 'O')
    
    def __repr__(self):
        return str(self.genes)

    def __str__(self):
        return str(self.genes)

    def __len__(self):
        return self.length
    
    def __getitem__(self, key):
        if not isinstance(key, int) and not isinstance(key, slice):
            raise TypeError("Type is: %s" % type(key))
            
        length = Numeric.shape(self.genes)[1]
        if isinstance(key, int) and key >= length:
            raise IndexError("""Request key %i is greater than the length 
                              of the object: %i""" % (key, length))
        elif isinstance(key, slice) and key.start >= length:
            raise IndexError("""Request key %i is greater than the length 
                              of the object: %i""" % (key.start, length))
            
        return self.genes[:, key]
    
    def __setitem__(self, key, value):
        if not isinstance(key, int) and not isinstance(key, slice):
            raise TypeError("Type is: %s" % type(key))
            
        length = Numeric.shape(self.genes)[1]
        if isinstance(key, int) and key >= length:
            raise IndexError("""Request key %i is greater than the length 
                              of the object: %i""" % (key, length))
        elif isinstance(key, slice) and key.start >= length:
            raise IndexError("""Request key %i is greater than the length 
                              of the object: %i""" % (key.start, length))

        self.genes[:, key] = value
    
    def fitness(self):
        # Only evaluate this individual's fitness once
        try:
            if self.fitness_value:
                return self.fitness_value
        except:
            pass

        trajectory_set = self.trajectory_set
        n = len(trajectory_set)
        fitness = 0

        if n == 0:
            return fitness

        # Calculate fitness for each trajectory
        for trajectory in trajectory_set:
            fitness_function = eval(trajectory.function.name)
            fitness += fitness_function(self, trajectory)

        self.fitness_value = float(fitness) / n
        return self.fitness_value

    def mate(self, partner):
        """
        Mate this organism with another using the organism's crossover method. 
        """
        if not self.crossover:
            raise Exception('No crossover operator specified.')
        
        #print "crossover..."
        if random() < self.crossoverRate:
            return self.crossover.mate(self, partner)
        else:
            return (self, partner)

    def copy(self):
        """
        Perform copy as parent would but make sure fitness value is cleared.
        """
        #copy = self.__class__(**genes)
        self_copy = copy.deepcopy(self)
        self_copy.fitness_value = None
        return self_copy
    
    def partExchange(self, partner):
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

    def groupPartExchange(self, partner):
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
        
    def mutate(self):
        """
        Implement the mutation phase, invoking
        stochastic mutation method on the entire
        organism.
        """
        mutant = self.copy()
        fitness = self.fitness()
        
        # If random value meets mutation probability, then mutate!
        if len(self.mutators) > 0 and random() < self.mutProb:
            # choose a random mutator
            while True:
                mutator = eval(choice(self.mutators))
                operator = mutator(mutant)
                #mutator, args = mutatorSet
                #operator = mutator(mutant, **args)

                # TODO: Replace hard-coded values with variable parameters
                if self.limit_mutation:
                    if fitness < 30 and operator.mutationImpact == "LARGE":
                        continue
                    elif fitness < 10 and operator.mutationImpact == "MEDIUM":
                        continue
                    else:
                        break
                else:
                    break
            
            #print "mutating..."
            mutant = operator.mutate()
        
        return mutant
        
    def xmlDump(self, fileobject):
        savePatternToXml(self, self.length, fileobject, False)

    def xmlDumps(self):
        savePatternToXml(self, self.length, "", True)

class PatternPopulation(Population):
    """
    Contains and manages a population of 2 dimensional patterns (arrays).
    """    
    def diversity(self, n=10):
        """
        Calculate the diversity of the top n organisms in the population.
        """
        similarities = []
        
        for i in xrange(n - 1):
            g1 = [y.value for x in self.organisms[i].genes.tolist() for y in x]
            
            for j in xrange(i+1, n):
                g2 = [y.value for x in self.organisms[j].genes.tolist() for y in x]
                s = similarity(g1, g2)
                similarities.append(s)
                
        total = sum(similarities)
        length = len(similarities)
        diversity = total / length
        
        return diversity
        
    def gen(self, nfittest=None, nchildren=None):
        """
        Executes a generation of the population.
        """
        # Add new random organisms, if required
        if self.numNewOrganisms:
            for i in xrange(self.numNewOrganisms):
                self.add(self.__class__())
    
        # Select n individuals to be parents
        #print "selecting..."
        parents = self.selector.select(self.organisms, self.childCount)
        #print "organisms: ", len(self.organisms)
        #print "parents: ", len(parents)
        children = []
        
        for i in xrange(self.childCount):
            # Choose first parent
            parent1 = parent2 = choice(parents)
        
            # Choose second parent not equal to first parent
            maxwait = 100
            i = 0
            while parent1.genes.tolist() == parent2.genes.tolist():
                if i > maxwait:
                    raise Exception("Waited too long for a different parent.")
                parent2 = choice(parents)
                i += 1
        
            # Reproduce
            #print "Before mating"
            child1, child2 = parent1 + parent2
            #print "After mating"

            # Mutate children
            child1 = child1.mutate()
            child2 = child2.mutate()
        
            children.extend([child1, child2])

        #print "Done mating..."
        children.extend(parents)
        children.sort()

        # Set parents and children as the new population
        self.organisms = children
        #print "Set organisms"
