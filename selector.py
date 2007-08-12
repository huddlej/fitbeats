"""
Selector classes implementing various selection algorithms
"""
import sys
from random import choice, randint, shuffle, random

class Selector(object):
    """
    Abstract base selection object contains standard methods 
    """

    def select(self, organisms=None, n=None):
        """
        @param list organisms a list of organisms from which individuals are 
        selected
        @param int n number of individuals in the population to select
        @param list candidates the selected candidates for reproduction
        """
        raise Exception("select method is not implemented.")

class TournamentSelector(Selector):
    """
    """
    
    def select(self, organisms, n):
        tournament_size = 5
        candidates = []
        for i in xrange(n):
            # Choose x random organisms
            tournament_candidates = [choice(organisms) for i in xrange(tournament_size)]
            best_candidate = tournament_candidates[0]

            # Compare candidates to find the best of the group.
            for candidate in tournament_candidates[1:]:                   
                if candidate.fitness() < best_candidate.fitness():
                    best_candidate = candidate

            candidates.append(best_candidate)

        return candidates
    
class RouletteSelector(Selector):
    """
    Based on the algorithm presented by Holland (1975) and Goldberg (1989b)
    """
    
    def select(self, organisms, n):
        # Evaluate the fitness of each organism
        organism_count = len(organisms)
        shuffle(organisms)
        fitnesses = [organism.fitness() for organism in organisms]
        f_total = sum(fitnesses)
        
        # Invert fitness so smallest fitnesses have the most weight.
        f_inv = [f_total / f for f in fitnesses]
        f_inv_total = sum(f_inv)

        # Calculate selection probability of inverted fitnesses.
        p = [f_inv_i / f_inv_total for f_inv_i in f_inv]
        
        # Calculate the cumulative selection probability.
        p_total = 0
        q = []
        for p_i in p:
            p_total += p_i
            q.append(p_total)

        
        # Select candidates for reproduction
        organism_range = xrange(1, organism_count)
        candidates = []
        for c in xrange(n):
            # Select r in (0, 1]
            r = 0
            while r == 0:
                r = random()

            if r < q[0]:
                i = 0
            else:
                for i in organism_range:
                    if q[i - 1] < r <= q[i]:
                        break

            candidates.append(organisms[i])

        print "Return candidates", len(candidates)
        return candidates

class NewRouletteSelector(Selector):
    """
    Based on the algorithm presented by Holland (1975) and Goldberg (1989b)
    """
    
    def select(self, organisms, n):
        # Evaluate the fitness of each organism
        organism_count = len(organisms)
        #shuffle(organisms)
        fitnesses = [organism.fitness() for organism in organisms]
        f_total = sum(fitnesses)
        
        # Calculate selection probability of inverted fitnesses.
        p = [f / f_total for f in fitnesses]

        # Invert fitness so smallest fitnesses have the most weight.
        p.reverse()

        #print p
        #sys.exit()
        
        # Calculate the cumulative selection probability.
        p_total = 0
        q = []
        for p_i in p:
            p_total += p_i
            q.append(p_total)

        
        # Select candidates for reproduction
        organism_range = xrange(1, organism_count)
        candidates = []
        for c in xrange(n):
            # Select r in (0, 1]
            r = 0
            while r == 0:
                r = random()

            if r < q[0]:
                i = 0
            else:
                for i in organism_range:
                    if q[i - 1] < r <= q[i]:
                        break

            candidates.append(organisms[i])

        print "Return candidates", len(candidates)
        return candidates
