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
            self.params["learning_rate"] = inputs[0]
            lr_string = '{:.8f}'.format(self.params["learning_rate"])[2:]
            layer_sizes = []
            layer_sizes.append(int(inputs[1]))
            layer_sizes.append(int(inputs[2]))
            layer_sizes.append(int(inputs[3]))
            self.params['layer_sizes'] = layer_sizes
            self.params["epsilon_decay_linear"] = float(inputs[4])

            self.params['name_scenario'] = 'gin_lr{}_struct{}_{}_{}_eps{}'.format(lr_string,
                                                                               layer_sizes[0],
                                                                               layer_sizes[1],
                                                                               layer_sizes[2],
                                                                               self.params['epsilon_decay_linear'])

            self.params['weights_path'] = 'weights/weights_' + self.params['name_scenario'] + '.h5'
            self.params['load_weights'] = False
            self.params['train'] = True
            print(self.params)

            # run one hand
            startTime = time.time()
            stats = learningGin.run(self.params)
            duration = time.time() - startTime
            stats.stats['duration'] = duration

            # the more we win, the better it came out
            # we are player two
            score = stats.stats['winMap'][self.params['player_two_name']] 
            stats.stats['score'] = score

            # report the results
            learningGin.print_stats(stats)
            with open(self.params['log_path'], 'a') as f: 
                print(f"\n********* {str(self.params['name_scenario'])}",file=f) 
                learningGin.print_stats(stats, f)
                print(f"=====> optimization run {self.params['name_scenario']} took {duration:10.2f} seconds\n",file=f)
                f.close()

            return score

        optim_params = [
            {"name": "learning_rate", "type": "continuous", "domain": (0.001, 0.05)},
            {"name": "first_layer_size", "type": "discrete", "domain": (20,50,100,200)},
            {"name": "second_layer_size", "type": "discrete", "domain": (20,50,100,200)},
            {"name": "third_layer_size", "type": "discrete", "domain": (20,50,100,200)},
            {"name":'epsilon_decay_linear', "type": "discrete", "domain": (float(2/self.params['episodes']),
                                                                           float(4/self.params['episodes']),
                                                                           float(8/self.params['episodes']),
                                                                           float(16/self.params['episodes']),
                                                                           float(32/self.params['episodes']))}
            ]

        bayes_optimizer = BayesianOptimization(f=optimize,
                                               domain=optim_params,
                                               initial_design_numdata=6,
                                               acquisition_type="EI",
                                               exact_feval=True,
                                               maximize=True)

        bayes_optimizer.run_optimization(max_iter=20)
        print('Optimized learning rate: ', bayes_optimizer.x_opt[0])
        print('Optimized first layer: ', bayes_optimizer.x_opt[1])
        print('Optimized second layer: ', bayes_optimizer.x_opt[2])
        print('Optimized third layer: ', bayes_optimizer.x_opt[3])
        print('Optimized epsilon linear decay: ', bayes_optimizer.x_opt[4])
        return self.params


##################
#      Main      #
##################
if __name__ == '__main__':
    print(f"bayesOpt.py: Bayesian optimization stsrting at {datetime.datetime.now()}") 
    # Define optimizer
    params = ginDQNParameters.define_parameters()
    params['log_path'] = 'logs/bayesian_log.' + params['timestamp'] +'.txt'
    bayesOpt = BayesianOptimizer(params)
    startTime = time.time()
    bayesOpt.optimize_RL()
    print(f"bayesOpt.py: Bayesian optimization run took {time.time()-startTime} seconds") 
