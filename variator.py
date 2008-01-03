"""Variator mockup used to test PISA functionality."""
import random
import sys
import time
import pisa

try:
    poll_period = 1
    MAX_GENERATIONS = 10
    pisa_files = {"configuration": "cfg", 
                  "initial_population": "ini",
                  "archive": "arc",
                  "sample": "sel", 
                  "offspring": "var",
                  "state": "sta"}
    pisa_prefix = "PISA_"
    for key, value in pisa_files.items():
        pisa_files[key] = "%s%s" % (pisa_prefix, value)

    # Write 0 to the state file
    pisa.write_file(pisa_files['state'], 0)

    # Read common parameters
    parameters = pisa.read_configuration_file(pisa_files['configuration'])
    print "Loaded parameters: %s\n" % parameters

    # Generate initial population
    population = {}
    for i in xrange(parameters['alpha']):
        population[i] = [float(random.randint(0, 100))]
    print "Generated population: %s\n" % population

    # Write initial population into init pop file
    pisa.write_file(pisa_files['initial_population'], population, parameters['dim'])

    # Write 1 to the state file
    pisa.write_file(pisa_files['state'], 1)

    # For each remaining generation
    print "Start\n"
    generation = 0
    while generation < MAX_GENERATIONS:
        # If state is 4, break. If state is 2, process selector output.
        # Otherwise, read state file every n seconds where n is the poll time
        state = pisa.read_state_file(pisa_files['state'])
        if state == 4:
            print "Selector has terminated\n"
            break
        elif state != 2:
            # Sleep for n seconds, then continue.
            print "Waiting for selector\n"
            time.sleep(poll_period)
            continue

        # Load sample from sample file
        print "Read sample file\n"
        sample = pisa.read_data_file(pisa_files['sample'])
        
        # Load archive from archive file
        archive = pisa.read_data_file(pisa_files['archive'])

        # Clean up local population based on archive contents
        ids = population.keys()
        for id in ids:
            if id not in archive:
                del(population[id])

        # Pair up and mate parents from sample with mutation
        next_id = max(population.keys()) + 1
        offspring = {}
        for i in xrange(parameters['lambda']):
            offspring[next_id] = [random.randint(0, 100)]
            next_id += 1

        # Calculate fitness values for the offspring
        # Write offspring to offspring file
        pisa.write_file(pisa_files['offspring'], offspring, parameters['dim'])
        population.update(offspring)

        # Write 3 to the state file
        pisa.write_file(pisa_files['state'], 3)
        generation += 1

    if state != 4:
        # Write 6 to state file
        pisa.write_file(pisa_files['state'], 6)

    print "Final sample:"
    for id in sample:
        print "%i: %s" % (id, population[id])
except pisa.CorruptedDataException, e:
    print "Error: %s" % e
