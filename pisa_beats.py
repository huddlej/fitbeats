#!/usr/bin/env python
"""
pisa_beats.py

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
from pattern import PatternGene, MultiObjectivePatternOrganism, MultiObjectiveDictPopulation
from fitbeat_project.fitbeats.models import *
from selector import RouletteSelector, TournamentSelector, NewRouletteSelector
from crossover import OnePointCrossover

def main(pattern_id=None):
    if pattern_id:
        return_best = True
    else:
        return_best = False
    
    usage = "usage: %prog [-p] [[options] pattern_id]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--prefix",
                      dest="pisa_prefix", type="string", default="PISA_",
                      help="the prefix to use for all PISA configuration files.")
    parser.add_option("-t", "--poll",
                      dest="pisa_period", type="float", default=1.0,
                      help="the amount of time the variator should wait between\
                            polling the PISA state file.")
    parser.add_option("-s", "--stats",
                      dest="statfile", type="string", default="stats.txt",
                      help="a filename for the statistical output")
    parser.add_option("-o", "--output",
                      dest="songfile", type="string", default=None,
                      help="a filename for the song output")
    parser.add_option("-d",
                      dest="database_dump", action="store_true", default=False,
                      help="dump best pattern to database")
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
    elif pattern_id is None and len(args) != 1:
        parser.error("""You must supply a pattern id as an argument or use the
                      -p flag to list the available patterns.""")
    else:
        try:
            pattern_id = pattern_id or int(args[0])
        except ValueError:
            parser.error("You must supply an integer value for the pattern id.")
    
    try:
        pattern = Pattern.objects.get(pk=pattern_id)
    except Pattern.DoesNotExist:
        print "Error: could not load pattern %s" % pattern_id
        sys.exit(1)
    
    selector = eval(pattern.selector.get_short_name())
    crossover = eval(pattern.crossover.get_short_name())
    mutators = ["%sMutator" % m.name for m in pattern.mutators.all()]
    
    trajectory_set = pattern.fitnesstrajectory_set.all()
    for trajectory in trajectory_set:
        trajectory.calculate_trajectory()

    parameters = dict([(parameter.name, parameter.value) for parameter in pattern.parameters.all()])
    
    # Prepare gene
    PatternGene.mutProb = parameters['gene_mutation_probability']
    
    # Prepare organism
    MultiObjectivePatternOrganism.mutProb = parameters['organism_mutation_probability']
    MultiObjectivePatternOrganism.crossoverRate = parameters['organism_crossover_rate']
    MultiObjectivePatternOrganism.instrument_length = pattern.instrument_length
    MultiObjectivePatternOrganism.instruments = pattern.instruments.all()
    MultiObjectivePatternOrganism.length = pattern.length
    MultiObjectivePatternOrganism.crossover = crossover()
    MultiObjectivePatternOrganism.mutators = mutators
    MultiObjectivePatternOrganism.limit_mutation = options.limit_mutation
    MultiObjectivePatternOrganism.trajectory_set = trajectory_set
    MultiObjectivePatternOrganism.gene = PatternGene
    
    # Prepare population
    childCount = int(parameters['population_new_children'])
    selector=selector()
    initial_population_size = int(parameters['population_initial_size'])
    ph = MultiObjectiveDictPopulation(options.pisa_prefix, options.pisa_period, childCount, 
                                      selector, init=initial_population_size,
                                      species=MultiObjectivePatternOrganism)
    max_generations = int(parameters['population_max_generations'])
    
    if not options.quiet:
        print "Pattern Length: %i" % pattern.length
        print "Instruments:"
        for i in pattern.instruments.all():
            print "\t%s" % i
        print "Generations: %i" % max_generations
        print "Selector: %s" % pattern.selector.name
        print "Crossover: %s" % pattern.crossover.name
        print "Mutators:\n\t%s" % "\n\t".join(mutators)
        print "Fitness Trajectories:"
        for t in trajectory_set:
            print "\t%s" % t
        print "Parameters:"
        for key, value in parameters.iteritems():
            print "\t%s: %s" % (key, value)
    
    stats = {}
    webstats = None
    lastBest = None
    lastBestCount = 0
    i = 0
    stopfile = "/home/huddlej/fitbeats/stopfile.txt"

    while i < max_generations:
        # Check for file-based exit command.
        if options.database_dump:
            try:
                fhandle = open(stopfile, "r")
                stop = pickle.load(fhandle)
                if stop:
                    break
            except:
                pass
    
        try:
            b = ph.best()
            #diversity = ph.diversity()
            
            if not options.quiet:
                print "generation %i:\n%s best=%s)" % (i, 
                                                       repr(b),
                                                       b.fitness())
            
            stats[i] = {'generation': i, 
                        'bestfitness': b.fitness(),
                        'best_pattern': b,
                        'is_done': False}
            webstats = stats[i]            
            # Store for web, TODO: make this better
            fhandle = open(options.statfile, "w")
            pickle.dump(webstats, fhandle)
            fhandle.close()
            
            if b.fitness() <= 0:
                break
                
            if lastBest is None or lastBest > b.fitness():
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

    if options.database_dump:
        p = PatternInstance(pattern=pattern,
                            fitness=b.fitness(),
                            value=b.xmlDumps())
        p.save()
    
    if webstats:
        webstats['is_done'] = True
        fhandle = open(options.statfile, "w")
        pickle.dump(webstats, fhandle)
        fhandle.close()
            
    if not options.quiet:
        print "Stopped:\n%s" % lastBest
        #print "Average diversity: %f" % ph.diversity()
    
    # Store new statistics data
    #fileHandle = open(options.statfile, 'w')
    #pickle.dump(stats, fileHandle)
    #fileHandle.close()

    if options.songfile:
        testxml = open(options.songfile, "w")
        b.xmlDump(testxml)
        testxml.close()

        if not options.quiet:
            print "Wrote %s" % options.songfile
    else:
        if not options.quiet:
            print "No file written."
        
if __name__ == '__main__':
    main()
