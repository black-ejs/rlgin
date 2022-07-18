import sys
import time
import copy
import learningGin
from GPyOpt.methods import BayesianOptimization

#################################################################
#   optimizes the parameter sets used by the learningGin module #
#               Sets the  parameters for Bayesian Optimization  #
#################################################################

################################################
################################################
################################################
################################################
################################################
class TrainingBayesianOptimizer():
    def __init__(self, params, optim_params):
        self.params = copy.deepcopy(params)
        self.optim_params = optim_params
        self.scenario_count = 0

    def customize_optim_params(self, inputs):
        pass

    def create_name_scenario(self, inputs):
        name_scenario="gin"
        i=0
        for input in inputs:
            if 'fmt' in self.optim_params[i]:
                scenario_str = ("{:" + self.optim_params[i]['fmt'] + "}").format(inputs[i])
            else:
                scenario_str = str(inputs[i])
            name_scenario += f"_{self.optim_params[i]['name']}{scenario_str}"
            i+=1
        return name_scenario

    def copy_inputs_to_params(self, inputs:(list),target_params:(dict)):
        i=0
        for input in inputs:
            target_params[self.optim_params[i]['name']] = inputs[i]
            i+=1

    ##########################################################
    def optimize_RL(self, max_iter:(int)=20, initial_iters:(int)=6):
        """
        optimizes the parameter sets used by the learningGin module
        """
        def optimize(inputs):
            """
            This is the "inner loop" that runs a learning session
            with the provided set of learning parameters 
            """
            print("INPUT", inputs)
            inputs = inputs[0]

            # Variables to optimize
            self.copy_inputs_to_params(inputs,self.params)
            self.customize_optim_params(inputs)

            # metadata for scenario
            self.params['name_scenario'] = self.create_name_scenario(inputs)
            self.params['weights_path'] = 'weights/weights_' + self.params['name_scenario'] + '.h5'
            self.params['load_weights'] = False
            self.params['train'] = True
            print(f"bayesian_parameters: {self.params}")

            # run one scenario
            startTime = time.time()
            stats = learningGin.run(copy.deepcopy(self.params))
            self.scenario_count += 1
            duration = time.time() - startTime
            stats.put('duration',duration)
            stats.put('bayesian_scenario_counter',self.scenario_count)

            # the more we win, the better it came out
            # we are player two
            # score = stats.get('winMap')[self.params['player_two_name']]
            totrew  = stats.get('total_reward')
            if len(totrew) > 0:
                score = stats.get('total_reward')[0][1] # player1's total_reward
            else:
                score = 0 # both players non-nn
            stats.put('score',score)

            # report the results
            self.print_stats(stats)

            return score

        bayes_optimizer = BayesianOptimization(f=optimize,
                                               domain=self.optim_params,
                                               # model_type="RF",
                                               initial_design_numdata=initial_iters,
                                               acquisition_type="EI",
                                               exact_feval=True,
                                               # verbosity=True,
                                               maximize=True)

        bayes_optimizer.run_optimization(max_iter=max_iter)
        for i in range(len(self.optim_params)):
            print(f"Optimized {self.optim_params[i]['name']}: ", bayes_optimizer.x_opt[i])
        return self.params
    
    def print_stats(self,stats):
        with open(self.params['log_path'], 'a') as f: 
            self._print_stats(stats,f)
            f.close()
        self._print_stats(stats, sys.stdout)
        
    def _print_stats(self,stats,f):
        print(f"\n=====> optimization run {str(self.params['name_scenario'])}",file=f) 
        learningGin.print_stats(stats, f)
        print(f"=====> optimization run \'{self.params['name_scenario']}\' took {stats.get('duration'):10.2f} seconds\n",file=f)
        


