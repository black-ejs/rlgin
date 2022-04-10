import learningGin
import time
import datetime
import ginDQNParameters
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
        self.params = params
        self.optim_params = optim_params

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

    ##########################################################
    def optimize_RL(self, max_iter:(int)=20):
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
            i=0
            for input in inputs:
                self.params[self.optim_params[i]['name']] = inputs[i]
                i+=1
            self.customize_optim_params(inputs)

            # metadata for scenario
            self.params['name_scenario'] = self.create_name_scenario(inputs)
            self.params['weights_path'] = 'weights/weights_' + self.params['name_scenario'] + '.h5'
            self.params['load_weights'] = False
            self.params['train'] = True
            print(self.params)

            # run one scenario
            startTime = time.time()
            stats = learningGin.run(self.params)
            duration = time.time() - startTime
            stats.put('duration',duration)

            # the more we win, the better it came out
            # we are player two
            # score = stats.get('winMap')[self.params['player_two_name']]
            score = stats.get('total_reward')
            stats.put('score',score)

            # report the results
            self.print_stats(stats)

            return score

        bayes_optimizer = BayesianOptimization(f=optimize,
                                               domain=self.optim_params,
                                               initial_design_numdata=6,
                                               acquisition_type="EI",
                                               exact_feval=True,
                                               # verbosity=True,
                                               maximize=True)

        bayes_optimizer.run_optimization(max_iter=max_iter)
        for i in range(len(self.optim_params)):
            print(f"Optimized {self.optim_params[i]['name']}: ", bayes_optimizer.x_opt[i])
        return self.params
    
    def print_stats(self,stats):
        learningGin.print_stats(stats)
        with open(self.params['log_path'], 'a') as f: 
            print(f"\n********* {str(self.params['name_scenario'])}",file=f) 
            learningGin.print_stats(stats, f)
            print(f"=====> optimization run {self.params['name_scenario']} took {stats.get('duration'):10.2f} seconds\n",file=f)
            f.close()


