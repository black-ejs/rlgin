import learningGin
import time
import datetime
import ginDQNParameters
from GPyOpt.methods import BayesianOptimization
from bayesOpt import TrainingBayesianOptimizer

#################################################################
#   optimizes the parameter sets used by the learningGin module #
#               Sets the  parameters for Bayesian Optimization  #
#################################################################
class DQNBayesianOptimizer(TrainingBayesianOptimizer):
    def __init__(self, params, optim_params):
        super().__init__(params, optim_params)

    def create_name_scenario(self, inputs):
        lr_string='{:.8f}'.format(float(inputs[0]))[2:]
        layer_sizes = self.params['layer_sizes']
        name_scenario = 'gin_lr{}_struct{}_{}_{}_eps{:2.3f}'.format(
                                lr_string,
                                int(inputs[1]),
                                int(inputs[2]),
                                int(inputs[3]),
                                float(inputs[4]))
        return name_scenario                    

    def customize_optim_params(self,inputs):
        layer_sizes = []
        layer_sizes.append(int(inputs[1]))
        layer_sizes.append(int(inputs[2]))
        layer_sizes.append(int(inputs[3]))
        self.params['layer_sizes'] = layer_sizes

#################################################################
##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(f"bayesDqn.py: Bayesian optimization stsrting at {datetime.datetime.now()}") 

    params = ginDQNParameters.define_parameters()
    params['log_path'] = 'logs/bayesDqn_log.' + params['timestamp'] +'.txt'
    optim_params = [
        {"name": "learning_rate", "type": "continuous", "domain": (0.001, 0.01)},
        {"name": "first_layer_size", "type": "discrete", "domain": (100,150,200,300)},
        {"name": "second_layer_size", "type": "discrete", "domain": (200,300,400,800)},
        {"name": "third_layer_size", "type": "discrete", "domain": (10,20,30,50)},
        {"name":'epsilon_decay_linear', "type": "discrete", "domain": (float(8/params['episodes']),
                                                                        float(16/params['episodes']),
                                                                        float(32/params['episodes']),
                                                                        float(64/params['episodes']),
                                                                        float(128/params['episodes'])), "fmt": "2.4f"}
        ]

    # Define optimizer
    # bayesOpt = BayesianOptimizer(params)
    bayesOpt = DQNBayesianOptimizer(params, optim_params)
    bayesOpt.optimize_RL()

    print(f"bayesDqn.py: Bayesian optimization run took {datetime.datetime.now()-start_time}") 
