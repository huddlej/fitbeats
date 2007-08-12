#!/usr/bin/env python
"""
evolve_beats.py

Evolves a pattern of beats based on a collection of user-defined fitness
trajectories.  The genetic algorithm is based on the pygene library.

@author John Huddleston
"""
import os
import sys
import pickle
os.environ['DJANGO_SETTINGS_MODULE'] = "fitbeat_project.settings"

from random import choice, random
from optparse import OptionParser
from pattern import PatternGene, PatternOrganism, PatternPopulation
from fitbeat_project.fitbeats.models import *
from selector import RouletteSelector, TournamentSelector, NewRouletteSelector
from crossover import OnePointCrossover
        
def main():
    usage = "usage: %prog [-p] [[options] pattern_id]"
    parser = OptionParser(usage)
    parser.add_option("-m", "--mutators",
                      dest="mutator_arg", type="string", default="0",
                      help="a comma delimited string of mutators to use by id")
    parser.add_option("-s", "--stats",
                      dest="statfile", type="string", default="stats.txt",
                      help="a filename for the statistical output")
    parser.add_option("-o", "--output",
                      dest="songfile", type="string", default=None,
                      help="a filename for the song output")
    parser.add_option("-l",
                      dest="limit_mutation", action="store_true", default=False,
                      help="limit mutation based on fitness value and mutator impact")
    parser.add_option("-q",
                      dest="quiet", action="store_true", default=False,
                      help="suppress debug output")
    parser.add_option("-p",
                      dest="list_patterns", action="store_true", default=False,
                      help="list available patterns and their ids")
    
    (options, args) = parser.parse_args()
    
    if options.list_patterns:
        patterns = Pattern.objects.all()
        print "Id | Dimensions | Name"
        print "----------------------"
        for p in patterns:
            try:
                print "%i | (%i x %i) | %s" % (p.id, 
                                               p.length, 
                                               p.instrument_length, 
                                               p)
            except:
                pass
        sys.exit()
    elif len(args) != 1:
        parser.error("""You must supply a pattern id as an argument or use the
                        -p flag to list the available patterns.""")
    else:
        try:
            pattern_id = int(args[0])
        except ValueError:
            parser.error("You must supply an integer value for the pattern id.")
    
    # Set option variables    
    limit_mutation = options.limit_mutation
    quiet = options.quiet
    statfile = options.statfile
    songfile = options.songfile
    mutator_arg = options.mutator_arg
    mutator_arg = map(int, mutator_arg.split(","))
    
    try:
        pattern = Pattern.objects.get(pk=pattern_id)
    except Pattern.DoesNotExist:
        print "Error: could not load pattern %s" % pattern_id
        sys.exit(1)
    
    length = pattern.length
    instrument_length = pattern.instrument_length

    selector = eval(pattern.selector.get_short_name())
    crossover = eval(pattern.crossover.get_short_name())
    mutators = ["%sMutator" % m.name for m in pattern.mutators.all()]
    
    trajectory_set = pattern.fitnesstrajectory_set.all()
    for trajectory in trajectory_set:
        trajectory.calculate_trajectory()
        
    parameters = pattern.parameters.all()
    parameter_dict = {}
    for parameter in parameters:
        parameter_dict[parameter.name] = parameter.value
    parameters = parameter_dict
    
    """
    # Available mutators to select from during mutation phase
    mutators = [
        (ClassicMutator, {}), 
        (InvertMutator, {}), 
        (InvertMutator, {'singleMutation': True}),
        (ReverseMutator, {}),
        (ReverseMutator, {'singleMutation': True}),
        (RotateMutator, {}),
        (RotateMutator, {'rotateAmount': 0, 'singleMutation': True}),
        (RotateMutator, {'rotateAmount': 1, 'singleMutation': True}),
        (TimbreExchangeMutator, {}),
        ]
    
    selectedMutators = []
    for m in mutator_arg:
        if m >= 0:
            selectedMutators.append(mutators[m])
    """
    # Prepare gene
    PatternGene.mutProb = parameters['gene_mutation_probability']
    
    # Prepare organism
    PatternOrganism.mutProb = parameters['organism_mutation_probability']
    PatternOrganism.crossoverRate = parameters['organism_crossover_rate']
    PatternOrganism.instrument_length = instrument_length
    PatternOrganism.length = length
    PatternOrganism.crossover = crossover()
    PatternOrganism.mutators = mutators
    PatternOrganism.limit_mutation = limit_mutation
    PatternOrganism.trajectory_set = trajectory_set
    PatternOrganism.gene = PatternGene
    
    # Prepare population
    PatternPopulation.selector=selector()
    ph = PatternPopulation(init=int(parameters['population_initial_size']),
                           species=PatternOrganism)
    ph.childCount = int(parameters['population_new_children'])
    max_generations = int(parameters['population_max_generations'])
    
    if not quiet:
        print "Pattern Length: %i, Instruments: %i" % (length, instrument_length)
        print "Generations: %i" % max_generations
        print "Selector: %s" % pattern.selector.name
        print "Crossover: %s" % pattern.crossover.name
        print "Mutators:\n\t%s" % "\n\t".join(mutators)
        print "Fitness Trajectories:"
        print trajectory_set
        #print "Parameters:"
        #print parameters
    
    stats = {}

    lastBest = 1000
    lastBestCount = 0
    i = 0
    while i < max_generations:
        try:
            b = ph.best()
            
            if not quiet:
                print "generation %i:\n%s best=%f, average=%f, diversity=%f)" % (i, 
                                                                                 repr(b),
                                                                                 b.fitness(),
                                                                                 ph.fitness(),
                                                                                 ph.diversity())
            
            stats[i] = {'generation': i, 
                        'bestfitness': b.fitness(), 
                        'popfitness': ph.fitness(),}
            
            if b.fitness() <= 0:
                break
                
            if lastBest > b.fitness():
                lastBest = b.fitness()
                lastBestCount = 1
            else:
                lastBestCount += 1
                
            #if lastBestCount > 10:
            #    break
            ph.gen()

            i += 1
        except KeyboardInterrupt:
            break

    if not quiet:
        print "Stopped:\n%f" % lastBest
        #print "Average diversity: %f" % ph.diversity()
    
    # Store new statistics data
    #fileHandle = open(statfile, 'w')
    #pickle.dump(stats, fileHandle)
    #fileHandle.close()

    if songfile:
        testxml = open(songfile, "w")
        b.xmlDump(testxml)
        testxml.close()

        if not quiet:
            print "Wrote %s" % songfile
    else:
        if not quiet:
            print "No file written."
        
if __name__ == '__main__':
    main()
