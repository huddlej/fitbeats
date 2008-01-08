"""Variator mockup used to test PISA functionality."""
import random
import time
import pisa

try:
    #################################################################
    # evolve_beats.py
    #
    # Configuration steps, command line arguments, basic file i/o.
    # Passes prefix and period.
    #################################################################
    
    MAX_GENERATIONS = 10
    pisa_prefix = "PISA_"
    poll_period = 1

    #################################################################
    # population __init__()
    #
    # PISA file names and common parameters.  Uses PISA files to
    # configure state and initial population.
    #################################################################
    for key, value in pisa.files.items():
        pisa.files[key] = "%s%s" % (pisa_prefix, value)

    # Write 0 to the state file
    pisa.write_file(pisa.files['state'], 0)

    # Read common parameters
    parameters = pisa.read_configuration_file(pisa.files['configuration'])
    print "Loaded parameters: %s\n" % parameters

    # Generate initial population
    population = {}
    for i in xrange(parameters['alpha']):
        population[i] = [float(random.randint(0, 100))]
        # Evaluate individual
    next_id = parameters['alpha']
    print "Generated population: %s\n" % population

    # Write initial population into init pop file
    pisa.write_file(pisa.files['initial_population'], population, parameters['dim'])

    # Write 1 to the state file
    pisa.write_file(pisa.files['state'], 1)

    #################################################################
    # evolve_beats
    #
    # Handles looping of generations.  Everything within loop can be
    # handled by the population.
    #################################################################

    # For each remaining generation
    print "Start\n"
    generation = 0
    while generation < MAX_GENERATIONS:
        #############################################################
        # population gen()
        #
        # Checks state file, returns False if selector terminates.
        #############################################################
        
        # If state is 4, break. If state is 2, process selector output.
        # Otherwise, read state file every n seconds where n is the poll time
        state = pisa.read_state_file(pisa.files['state'])
        if state == 4:
            print "Selector has terminated\n"
            break
        elif state != 2:
            # Sleep for n seconds, then continue.
            print "Waiting for selector\n"
            time.sleep(poll_period)
            continue

        #############################################################
        # The load sample and archive sections could be in the
        # selector but how does the selector know where the mating
        # happens or where to look for the data files? How does it
        # know what it's looking at or what to do with it?
        #############################################################

        # Load sample from sample file
        print "Read sample file\n"
        sample = pisa.read_data_file(pisa.files['sample'])
        
        # Load archive from archive file
        archive = pisa.read_data_file(pisa.files['archive'])

        # Clean up local population based on archive contents
        ids = population.keys()
        for id in ids:
            if id not in archive:
                del(population[id])

        # Pair up and mate parents from sample with mutation
        offspring = {}
        for i in xrange(parameters['lambda']):
            offspring[next_id] = [random.randint(0, 100)]
            next_id += 1

        # Calculate fitness values for the offspring
        # Write offspring to offspring file
        pisa.write_file(pisa.files['offspring'], offspring, parameters['dim'])
        population.update(offspring)

        # Write 3 to the state file
        pisa.write_file(pisa.files['state'], 3)

        # This marks the end of the gen() method.
        generation += 1 

    #################################################################
    # The final write to the state file will need to be handled
    # in a separate population method like close(), or finish().
    # Alternately, the population's __del__ method can be used.
    #################################################################
    if state != 4:
        # Write 6 to state file
        pisa.write_file(pisa.files['state'], 6)

    print "Final sample:"
    for id in sample:
        print "%i: %s" % (id, population[id])
except pisa.CorruptedDataException, e:
    print "Error: %s" % e
