# RUN_UNIVERSE parallely


import numpy as np
from copy import deepcopy
import time
from individual import Individual
import problem
import selections
import gc
import os
import mpi4py as MPI


def evaluator_queue():
    pass

def run_parallel(population,
                 GENERATION_LIMIT,
                 num_mutants,
                 num_offspring,
                 input_data,
                 labels,
                 block=None
                 ):
    converged = False
    generation = 0
    while (not converged) & (generation <= GENERATION_LIMIT):
        scores = []
        SCORE_MIN = problem.score_min
        generation += 1
        run_universe()

        for individual in population:
            scores.append(individual.fitness.values[0])

        if np.min(scores) < SCORE_MIN:
            converged = True

        if (generation % 10) == 0 or converged:
            sample_best = population[np.random.choice(a=np.where(np.min(scores) == scores)[0], size=1)[0]]
            try:
                print(sample_best.genome_outputs[0])
            except:
                import pdb
                pdb.set_trace()

    return population


def evaluate_population(population):
    print("population after mutation", len(population))
    print("    EVALUATING")
    for individual in population:
        if individual.need_evaluate():
            """
            look up concurrent.futures and queue...
            maybe make the queue thing a permanent part of universe in evaluating every individual
            then make solving each node customizable...gt computer nodes, locally on different processes,
            or on cloud compute service, add to queue to evaluate individual
            evaluate uses multithreading to send individuals to evaluate blocks
            """

            individual.evaluate(problem.x_train, problem.y_train, (problem.x_val,
                                                                   problem.y_val))
            individual.fitness.values = problem.scoreFunction(actual=problem.y_val,
                                                              predict=individual.genome_outputs)
            print('Muatated population individual has fitness: {}'
                  .format(individual.fitness.values))

    """
     print("after mutation")
     for ind in population:
         print(ind.skeleton[1]["block_object"].active_nodes)

     filter population down based off fitness
     new population done: rank individuals in population and trim down
    """

    population, _ = selections.selNSGA2(population, k=pop_size, nd='standard')
    print("population after selection ", len(population))
    gc.collect()

    """
    print("after selection")
    for ind in population:
    print(ind.skeleton[1]["block_object"].active_nodes)
    """
    return population


def run_universe(sub_pop, num_mutants, num_offspring, input_data, labels, block=None):
    print("    MUTATING")

    for i in range(len(sub_pop)):
        individual = sub_pop[i]
        for _ in range(num_mutants):
            mutant = deepcopy(individual)
            print("deepcopied")
            mutant.mutate(block)
            if mutant.need_evaluate:
                sub_pop.append(mutant)
            else:
                pass
    return sub_pop


def create_universe(input_data, labels, population_size=9, universe_seed=9, num_mutants=4, num_offpsring=2):
    np.random.seed(universe_seed)

    population = []
    for i in range(population_size):
        individual = Individual(skeleton=problem.skeleton_genome)
        individual.evaluate(problem.x_train, problem.y_train, (problem.x_val,
                                                               problem.y_val))

        try:
            individual.fitness.values = problem.scoreFunction(actual=problem.y_val,
                                                              predict=individual.genome_outputs)
            print('Initialized individual has fitness: {}' \
                  .format(individual.fitness.values))

        except:
            import pdb;pdb.set_trace()

        population.append(individual)
        del individual

    generation = -1
    converged = False
    GENERATION_LIMIT = problem.generation_limit # 199
    SCORE_MIN = problem.score_min # 1e-1
    start_time = time.time()
    newpath = r'outputs_cifar/'

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    file_generation = 'outputs_cifar/generation_number.npy'

    while (not converged) & (generation<=GENERATION_LIMIT):
        generation += 1
        population = run_universe(population,
                                  num_mutants,
                                  num_offpsring,
                                  input_data,
                                  labels)

        scores = []

        for individual in population:
            scores.append(individual.fitness.values[0])


        print("-------------RAN UNIVERSE FOR GENERATION: {}-----------".format(generation + 1))
        print(generation, np.min(scores))


        if np.min(scores) < SCORE_MIN:
            converged = True
        else:
            pass
        if (generation%10 == 0) or (converged):
            sample_best = population[np.random.choice(a=np.where(np.min(scores)==scores)[0], size=1)[0]]
            try:
                print(sample_best.genome_outputs[0])

            except:
                import pdb
                pdb.set_trace()

        file_pop = 'outputs_cifar/gen%i_pop.npy' % generation

        np.save(file_pop, population)
        np.save(file_generation, generation)

    print("ending universe", time.time()-start_time)
