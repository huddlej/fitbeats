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
from fitness import *
from mutator import *
from hydrogen import savePatternToXml
import pisa

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
    mutProb = 0.02
    crossoverRate = 0.9
    
    def __init__(self, **kw):
        self.genes = Numeric.array([[self.gene() 
                                    for i in xrange(self.length)]
                                    for j in xrange(self.instrument_length)], 'O')
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        output = ""
        for i in xrange(Numeric.shape(self.genes)[0] - 1, -1, -1):
            output += "%s %s\n" % (str(self.instruments[i]).ljust(20), " ".join(map(str, self.genes[i].tolist())))
        return output

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
            if self._fitness:
                return self._fitness
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

        self._fitness = float(fitness) / n
        return self._fitness

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
        self_copy._fitness = None
        return self_copy

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
            
            mutant = operator.mutate()
        
        return mutant
        
    def xmlDump(self, fileobject):
        savePatternToXml(self, fileobject, False)

    def xmlDumps(self):
        song = savePatternToXml(self, None, True)
        return song.toxml()

class MultiObjectivePatternOrganism(PatternOrganism):
    """
    Pattern Organism that treats fitness as a vector of objective values
    for the sake of multiobjective optimization.
    """
    def fitness(self):
        # Evaluate the fitness once.
        if not hasattr(self, '_fitness'):
            self._fitness = []
            if len(self.trajectory_set) > 0:
                # Evaluate each trajectory.
                for trajectory in self.trajectory_set:
                    fitness_function = eval(trajectory.function.name)
                    self._fitness.append(fitness_function(self, trajectory))
        return self._fitness
        
    def mutate(self):
        """Mutates the individual without regarding fitness."""
        mutant = self.copy()
        if len(self.mutators) > 0 and random() < self.mutProb:
            # TODO: Mutators should handle mutation with a static method.
            # Choose a random mutator.
            mutator = eval(choice(self.mutators))
            operator = mutator(mutant)
            mutant = operator.mutate()

        return mutant

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
        parents = self.selector.select(self.organisms, self.childCount)
        children = []
        
        for i in xrange(self.childCount):
            # Choose first parent
            parent1 = parent2 = choice(parents)
        
            # Choose second parent not equal to first parent
            maxwait = 400
            i = 0
            while parent1.genes.tolist() == parent2.genes.tolist():
                if i > maxwait:
                    # Try another random set of parents if the first one didn't work.
                    parent1 = parent2 = choice(parents)
                parent2 = choice(parents)
                i += 1
        
            # Reproduce
            child1, child2 = parent1 + parent2

            # Mutate children
            child1 = child1.mutate()
            child2 = child2.mutate()
        
            children.extend([child1, child2])

        children.extend(parents)
        children.sort()

        # Set parents and children as the new population
        self.organisms = children

    def worst(self):
        return max(self)

class DictPopulation(Population):
    def __init__(self, childCount, selector, *items, **kwargs):
        self.max_id = 0
        self.organisms = {}
        self.childCount = childCount
        self.selector = selector
        super(DictPopulation, self).__init__(*items, **kwargs)

    def add(self, *args):
        for arg in args:
            if isinstance(arg, Organism):
                self.organisms[self.max_id] = arg
                self.max_id += 1
            else:
                self.add(arg)

    def best(self):
        return max(self.organisms.values())

    def worst(self):
        return min(self.organisms.values())

class MultiObjectiveDictPopulation(DictPopulation):
    def __init__(self, pisa_prefix, pisa_period, *items, **kwargs):
        self.pisa_prefix = pisa_prefix
        self.pisa_period = pisa_period
        self.pisa_files = {}
        for key, value in pisa.files.items():
            self.pisa_files[key] = "%s%s" % (pisa_prefix, value)

        # Write 0 to the state file.
        pisa.write_file(self.pisa_files['state'], pisa.STATE_0)

        # Read common parameters.
        self.pisa_parameters = pisa.read_configuration_file(self.pisa_files['configuration'])
        print "Loaded parameters: %s\n" % self.pisa_parameters

        # Generate the initial population.
        super(MultiObjectiveDictPopulation, self).__init__(*items, **kwargs)

        # Write initial population into init pop file
        pisa.write_file(self.pisa_files['initial_population'], self.organisms, self.pisa_parameters['dim'])

        # Write 1 to the state file
        pisa.write_file(self.pisa_files['state'], pisa.STATE_1)

    def __del__(self):
        if hasattr(self, 'state') and self.state != pisa.STATE_4:
            # Write 6 to state file
            pisa.write_file(self.pisa_files['state'], pisa.STATE_6)
 
    def gen(self, nfittest=None, nchildren=None):
        """Executes a generation of the population."""
        # If state is 4, return False. If state is 2, process selector output.
        # Otherwise, read state file every n seconds where n is the poll time.
        while True:
            self.state = pisa.read_state_file(self.pisa_files['state'])
            if self.state == pisa.STATE_4:
                print "Selector has terminated\n"
                return False
            elif self.state == pisa.STATE_2:
                break
            else:
                # Sleep for n seconds, then continue.
                print "Waiting for selector\n"
                time.sleep(poll_period)
                continue

        # Load sample from sample file.
        print "Read sample file\n"
        sample = pisa.read_data_file(self.pisa_files['sample'])
        
        # Load archive from archive file.
        archive = pisa.read_data_file(self.pisa_files['archive'])

        # Clean up local population based on archive contents.
        ids = population.keys()
        for id in ids:
            if id not in archive:
                del(population[id])

        # Pair up and mate parents from sample with mutation.
        offspring = {}
        for i in xrange(self.pisa_parameters['lambda']):
            # Choose the first parent.
            parent_index_1 = parent_index_2 = choice(sample)
        
            # Choose the second parent not equal to first parent.
            while parent_index_1 == parent_index_2:
                parent_index_2 = choice(sample)
        
            # Reproduce and mutate.
            children = self.organisms[parent_index_1] + self.organisms[parent_index_2]
            child = choice(children)
            child = child.mutate()

            # Calculate fitness and add child.
            offspring[self.max_id] = child.fitness()
            self.add(child)

        # Write offspring to offspring file
        pisa.write_file(self.pisa_files['offspring'], offspring, self.pisa_parameters['dim'])

        # Write 3 to the state file
        pisa.write_file(self.pisa_files['state'], pisa.STATE_3)
