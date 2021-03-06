'''
root/problem/problem_definition.py

Overview:
overview of what will/should be in this file and how it interacts with the rest of the code

Rules:
mention any assumptions made in the code or rules about code structure should go here
'''

### packages
import numpy as np
from abc import ABC, abstractmethod
from typing import List

### sys relative to root dir
import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

### absolute imports wrt root
from codes.factory import FactoryDefinition
#from codes.universe import UniverseDefinition # can't import because will create import loop
from codes.utilities.custom_logging import ezLogging
from codes.genetic_material import IndividualMaterial#, BlockMaterial
from codes.individual_definitions.individual_definition import IndividualDefinition
from codes.individual_definitions.individual_evaluate import IndividualEvaluate_Abstract
from codes.individual_definitions.individual_mutate import IndividualMutate_Abstract
from codes.individual_definitions.individual_mate import IndividualMate_Abstract
from codes.block_definitions.block_definition import BlockDefinition
from codes.block_definitions.block_evaluate import BlockEvaluate_Abstract
from codes.block_definitions.block_mutate import BlockMutate_Abstract
from codes.block_definitions.block_mate import BlockMate_Abstract
from codes.block_definitions.block_shapemeta import BlockShapeMeta_Abstract
from codes.block_definitions.block_operators import BlockOperators_Abstract
from codes.block_definitions.block_arguments import BlockArguments_Abstract



class ProblemDefinition_Abstract(ABC):
    '''
     * data: training + validation
     * objective ftn(s)
     * define convergence
     * individual definition
     * which universe
    '''
    # Note to user: all abstract methods are not defined 
    # by default, please implement according to preferences
    def __init__(self,
                 population_size: int,
                 number_universe: int,
                 factory_def: FactoryDefinition,
                 mpi: bool=False,
                 genome_seeds: List=[]):
        '''
        genome_seeds:
        * each element in outer list is an inividual to be seeded
        * each element in the inner list is the seed for that positional block of the individual
        * an inner element of 'None' will get a randomly built block
        * an element could be a pkl file instead of another list if we are loading in a whole pickled IndividualMaterial
        
        self.construct_dataset()

        the build out each block and build individual_def
        block_def = self.construct_block()
        self.construct_individual([block_def])
        '''
        self.pop_size = population_size
        self.number_universe = number_universe
        self.Factory = factory_def
        self.mpi = mpi
        self.genome_seeds = genome_seeds


    @abstractmethod
    def construct_dataset(self):
        '''
        training data + labels
        validating data + labels
        '''
        pass


    @abstractmethod
    def objective_functions(self, indiv: IndividualMaterial):
        '''
        save fitness for each individual to IndividualMaterial.fitness.values as tuple
        
        try:
            acc_score = accuracy_score(actual, predict)
            avg_f1_score = f1_score(actual, predict, average='macro')
            return 1 - acc_score, 1 - avg_f1_score
        except ValueError:
            print('Malformed predictions passed in. Setting worst fitness')
            return 1, 1  # 0 acc_score and avg f1_score b/c we want this indiv ignored
        '''
        pass


    @abstractmethod
    def check_convergence(self, universe):
        '''
        whether some threshold for fitness or some max generation count

        set universe.converged to boolean T/F ...True will end the universe run
        '''
        pass


    def postprocess_generation(self, universe):
        '''
        NOTE that this is not an abstractmethod because the user may choose not to do anything here

        at this point in universe, the population has been fully evaluated.
        currently it is at the end of the loop so population selection has already occured.
        that may change
        '''
        ezLogging.info("Post Processing Generation Run - pass")
        pass


    def postprocess_universe(self, universe):
        '''
        NOTE that this is not an abstractmethod because the user may choose not to do anything here

        the idea here is that the universe.run() is about to exit but before it does,
        we can export or plot things wrt the final population
        '''
        ezLogging.info("Post Processing Universe Run - pass")
        pass


    def get_best_indiv(self, universe, ith_obj):
        '''
        return the index (ith indiv in population) who has the lowest score based
        on the ith objective
        '''
        best_score = np.inf
        best_index = None
        for ith_indiv, indiv in enumerate(universe.population.population):
            if indiv.fitness.values[ith_obj] < best_score:
                best_score = indiv.fitness.values[ith_obj]
                best_index = ith_indiv
        return best_index, best_score


    # Note to user: these last two methods are already defined
    def construct_block_def(self,
                            nickname: str,
                            shape_def: BlockShapeMeta_Abstract,
                            operator_def: BlockOperators_Abstract,
                            argument_def: BlockArguments_Abstract,
                            evaluate_def: BlockEvaluate_Abstract,
                            mutate_def: BlockMutate_Abstract,
                            mate_def: BlockMate_Abstract):
        return BlockDefinition(nickname,
                               shape_def,
                               operator_def,
                               argument_def,
                               evaluate_def,
                               mutate_def,
                               mate_def)


    def construct_individual_def(self,
                                 block_defs: List[BlockDefinition],
                                 mutate_def: IndividualMutate_Abstract,
                                 mate_def: IndividualMate_Abstract,
                                 evaluate_def: IndividualEvaluate_Abstract):
        self.indiv_def = IndividualDefinition(block_defs,
                                              evaluate_def,
                                              mutate_def,
                                              mate_def)