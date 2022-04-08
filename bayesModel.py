import learningGin
import time
import datetime
import ginDQNParameters
from GPyOpt.methods import BayesianOptimization

#################################################################
#   optimizes the parameter sets used by the learningGin module #
#               Sets the  parameters for Bayesian Optimization  #
#################################################################

class BayesianOptimizer():
    def __init__(self, params):
        self.params = params

    def optimize_RL(self):
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
            name_scenario = "gin"
            for input in inputs:
                self.params[optim_params[i]['name']] = inputs[i]
                if 'fmt' in optim_params[i]:
                    input_str = ("{:" + optim_params[i]['fmt'] + "}").format(inputs[i])
                else:
                    input_str = str(inputs[i])
                name_scenario += f"_{optim_params[i]['name']}{input_str}"
                i +=1

            self.params['name_scenario'] = name_scenario
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
            score = stats.get('winMap')[self.params['player_two_name']]
            stats.put('score',score)

            # report the results
            self.print_stats(stats)

            return score

        optim_params = [
            {"name": "win_reward", "type": "continuous", "domain": (0.99, 0.75), "fmt": "0.3f"},
            {"name": "loss_reward", "type": "continuous", "domain": (-0.009, -0.20), "fmt": "0.3f"},
            {"name": "no_win_reward", "type": "continuous", "domain": (-0.001, -0.01), "fmt": "0.3f"}
            ]

        bayes_optimizer = BayesianOptimization(f=optimize,
                                               domain=optim_params,
                                               initial_design_numdata=6,
                                               acquisition_type="EI",
                                               exact_feval=True,
                                               # verbosity=True,
                                               maximize=True)

        bayes_optimizer.run_optimization(max_iter=20)
        for i in range(len(optim_params)):
            print(f"Optimized {optim_params[i]['name']}: ", bayes_optimizer.x_opt[i])
        return self.params
    
    def print_stats(self,stats):
        learningGin.print_stats(stats)
        with open(self.params['log_path'], 'a') as f: 
            print(f"\n********* {str(self.params['name_scenario'])}",file=f) 
            learningGin.print_stats(stats, f)
            print(f"=====> optimization run {self.params['name_scenario']} took {stats.get('duration'):10.2f} seconds\n",file=f)
            f.close()

##################
#      Main      #
##################
if __name__ == '__main__':
    print(f"bayesModel.py: Bayesian model optimization starting at {datetime.datetime.now()}") 
    # Define optimizer
    params = ginDQNParameters.define_parameters()
    params['log_path'] = 'logs/bayesian_log.' + params['timestamp'] +'.txt'
    params['episodes'] = 5
    bayesOpt = BayesianOptimizer(params)
    startTime = time.time()
    bayesOpt.optimize_RL()
    print(f"bayesModel.py: Bayesian optimization run took {time.time()-startTime} seconds") 
