"""
mutator.py

Base Mutator class for all mutation operators and extensions of this base class
for the following organism-level mutations:

 * Classic - randomly mutate each bit in an individual with a given probability
 * Reverse - reverse the order of the beats in each instrument or in one random
             instrument
 * RotateRight -  rotate to the right by a random or specified amount
 * Invert - silence to noise, noise to silence
 * TimbreExchange - randomly swap two instrument parts
"""

from random import choice, randint
from collections import deque
import operator

class Mutator(object):
    """
    Base Mutator class
    
    All mutation operators will extend this class
    """
    
    """
    @var string
    @private
    """
    mutationImpact = None
    
    def __init__(self, organism=None, **kw):
        """
        @param organism organism the organism to be mutated which may or may not
                                 be a copy; mutators do not need to worry about
                                 that.
        """
        self.organism = organism
        self.args = kw

    def __str__(self):
        """
        Override this method
        
        @return string the string representation of the mutator's parameters
        """
        raise Exception("The __str__ method must be overridden") 
        
    def mutate(self):
        """
        Override this method
        
        @return organism organism the organism to be mutated
        """
        raise Exception("The mutate method must be overridden") 
        
class ClassicMutator(Mutator):
    """
    Perform simple, classic mutation on a randomly selected gene
    or on each gene individually.
    """

    mutationImpact = "SMALL"

    def __repr__(self):
        return "ClassicMutator"
    
    def __str__(self):
        """
        @return string the string representation of the mutator's parameters
        """
        s = "impact: %s" % (self.mutationImpact)
        return s
    
    def mutate(self):
        if self.organism.mutateOneOnly:
            # Unconditionally mutate just one gene.
            
            # Choose random row and column.
            rowIndex = randint(0, self.organism.instrument_length - 1)
            columnIndex = randint(0, self.organism.length - 1)
            gene = self.organism.genes[rowIndex][columnIndex].toscalar()
            gene.mutate()
        else:
            # Conditionally mutate all genes.
            for row in self.organism.genes:
                for gene in row:
                    gene.maybeMutate()
                
        return self.organism

class InvertMutator(Mutator):
    """
    Invert the values of an organism's genes by swapping silence for noise and 
    noise for silence.
    """
    
    def __init__(self, organism, **kw):
        """
        @param organism organism
        @param boolean singleMutation whether a single individual should be
                                      mutated instead of all individuals
        @param mixed minValue minimum value assignable to genes in the organism
        @param mixed maxValue maximum value assignable to genes in the organism
        """
        self.organism = organism

        if kw.has_key('singleMutation'):
            self.singleMutation = kw['singleMutation']
        else:
            self.singleMutation = False
            
        if kw.has_key('minValue'):
            self.minValue = kw['minValue']
        else:
            self.minValue = 0

        if kw.has_key('maxValue'):
            self.maxValue = kw['maxValue']
        else:
            self.maxValue = 1
        
        if self.singleMutation:
            self.mutationImpact = "MEDIUM"
        else:
            self.mutationImpact = "LARGE"

    def __repr__(self):
        return "InvertMutator"

    def __str__(self):
        """
        @return string the string representation of the mutator's parameters
        """
        s = "singleMutation: %s|minValue: %i|maxValue: %i|impact: %s" % (
            self.singleMutation, self.minValue, self.maxValue, 
            self.mutationImpact
            )
        return s
    
    def mutate(self):
        # Set the range of genes to invert.
        if self.singleMutation:
            # Select a random instrument to invert.
            instruments = [randint(0, self.organism.instrument_length - 1)]
        else:
            # Use all instruments
            instruments = xrange(self.organism.instrument_length)
        
        for instrument in instruments:
            row = self.organism.genes[instrument].tolist()
            for gene in row:
                if gene.value > self.minValue:
                    gene.value = self.minValue
                else:
                    gene.value = self.maxValue
            self.organism.genes[instrument] = row

        return self.organism
        
class ReverseMutator(Mutator):
    """
    Reverse the order of beats in one or more instrument rows.
    """
 
    def __init__(self, organism, **kw):
        """
        @param PatternOrganism organism
        @param boolean singleMutation whether a single individual should be
                                      mutated instead of all individuals
        """
        self.organism = organism
        
        if kw.has_key('singleMutation'):
            self.singleMutation = kw['singleMutation']
        else:
            self.singleMutation = False
        
        if self.singleMutation:
            self.mutationImpact = "MEDIUM"
        else:
            self.mutationImpact = "LARGE"

    def __repr__(self):
        return "ReverseMutator"

    def __str__(self):
        """
        @return string the string representation of the mutator's parameters
        """
        s = "singleMutation: %s|impact: %s" % (self.singleMutation, 
                                               self.mutationImpact)
        return s

    def mutate(self):        
        if self.singleMutation:
            instruments = [randint(0, self.organism.instrument_length - 1)]
        else:
            instruments = xrange(self.organism.instrument_length)

        for instrument in instruments:
            row = self.organism.genes[instrument].tolist()
            row.reverse()
            self.organism.genes[instrument] = row
        
        return self.organism
        
class RotateMutator(Mutator):
    """
    Rotate one or more instrument rows to the right by a specified or random 
    amount.
    """

    def __init__(self, organism=None, **kw):
        """
        @param organism organism the organism to be mutate which may or may not
                                 be a copy.  Mutators do not need to worry about
        @param int rotateAmount the amount by which the individual should be 
                                rotated
        @param boolean singleMutation whether a single row should be mutated 
                                      instead of all rows
        """
        self.organism = organism
        
        if kw.has_key('singleMutation'):
            self.singleMutation = kw['singleMutation']
        else:
            self.singleMutation = False
        
        if kw.has_key('rotateAmount') and kw['rotateAmount'] > 0:
            self.rotateAmount = -1 * (kw['rotateAmount'] % 
                                      organism.length)
        else:
            self.rotateAmount = -1 * randint(1, organism.length - 1)
        
        """
        Determine how much impact is made based on the percentage of 
        the individual being rotated and whether all instruments are being
        rotated or not.
        
        1. If all rows being rotated and rotation is more than a third of the
        individual it's a large impact.
        2. If all rows are being rotated and rotation is less than a third but 
        more than one value, it's a medium impact.
        3. If all rows are being rotated by one value, it's a small impact.
        4. If one row is being rotated more than a third, it's a medium impact.
        5. If one row is being rotated less than a third, it's a small impact.
        """
        rotFraction = float(self.rotateAmount) / organism.length
        if (not self.singleMutation and rotFraction > 0.33):
            self.mutationImpact = "LARGE"
        elif ((not self.singleMutation and rotFraction <= 0.33 
               and self.rotateAmount > 1) 
              or (self.singleMutation and rotFraction > 0.33)): 
            self.mutationImpact = "MEDIUM"
        else:
            self.mutationImpact = "SMALL"

    def __repr__(self):
        return "RotateMutator"

    def __str__(self):
        """
        @return string the string representation of the mutator's parameters
        """
        s = "singleMutation: %s|rotate amount: %i|impact: %s" % (
            self.singleMutation, self.rotateAmount, self.mutationImpact
            )
        return s

    def mutate(self):
        if self.singleMutation:
            instruments = [randint(0, self.organism.instrument_length - 1)]
        else:
            instruments = xrange(self.organism.instrument_length)

        for instrument in instruments:
            row = self.organism.genes[instrument]
            row = row[self.rotateAmount:] + row[:self.rotateAmount]
            self.organism.genes[instrument] = row

        return self.organism

class TimbreExchangeMutator(Mutator):
    """
    Exchange instrument parts between two randomly selected instruments.
    """ 
    mutationImpact = "SMALL"
    
    def __repr__(self):
        return "TimbreExchangeMutator"

    def __str__(self):
        """
        @return string the string representation of the mutator's parameters
        """
        s = "impact: %s" % self.mutationImpact
        return s

    def mutate(self):
        """
        Select two instrument rows to exchange parts between.
        """
        # Select random instrument 1 to exchange
        instrument1 = instrument2 = randint(0, self.organism.instrument_length - 1)
       
        # Select random instrument 2 to exchange
        while instrument1 == instrument2:
            instrument2 = randint(0, self.organism.instrument_length - 1)

        # Exchange instrument rows
        row1 = self.organism.genes[instrument1].tolist()
        row2 = self.organism.genes[instrument2].tolist()
        self.organism.genes[instrument1] = row2
        self.organism.genes[instrument2] = row1

        return self.organism
