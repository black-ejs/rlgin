import learningGin
import time
import copy
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

    def copy_inputs_to_params(self, inputs:(list),target_params:(dict)):
        pass
            
    def customize_optim_params(self,inputs):
        player_inputs = [{},{}]
        for i in range(len(inputs)):
            name = self.optim_params[i]
            if ['name'][-1] == '1':
                player_inputs[0][name[:-2]] = inputs[i]
            elif ['name'][-1] == '2':
                player_inputs[1][name[:-2]] = inputs[i]
            else:
                self.params[name] = inputs[i]

        for i in (1,2):
            pi = player_inputs[i]
            player_key = 'player' + int(i)
            if not 'nn' in self.params[player_key]:
                if 'nn-common' in self.params:
                    self.params[player_key]['nn'] = copy.deepcopy(self.params['nn-common'])
                else:
                    self.params[player_key]['nn'] = {}
            target = self.params[player_key]['nn']
            for nn_param in ('strategy', 'no_relu', 'learning_rate', 'epsilon_decay_linear'):
                if nn_param in pi:
                    target[nn_param] = pi[nn_param]

            layer_sizes = []
            for ls_param in ('first','second','third','fourth'):
                ls = int(pi[ls_param+'_layer_size'])
                if ls > 0:
                    layer_sizes.append(ls)
            target['layer_sizes'] = layer_sizes

#################################################################
##################
#      Main      #
##################
if __name__ == '__main__':
    TRAIN_EPISODES = 2000
    TEST_EPISODES = 500
    MAX_ITER = 100

    start_time = datetime.datetime.now()
    print(f"bayesDqn.py: Bayesian optimization starting at {datetime.datetime.now()}") 

    params = ginDQNParameters.define_parameters()
    params['epsiodes'] = TRAIN_EPISODES
    params['test_epsiodes'] = TEST_EPISODES
    params['log_path'] = 'logs/bayesDqn_log.' + params['timestamp']+'.txt'
    optim_params_template = [
        {'name': "strategy", 'type': "discrete", 'domain': ('nn-convf', 'nn-convf', 'nn-linear')},
        {'name': "learning_rate", 'type': "continuous", 'domain': (0.0001, 0.01)},
        {'name': 'epsilon_decay_linear', 'type': "continuous", 'domain': (float(8/params['episodes']),
                                                                         float(128/params['episodes'])), "fmt": "2.5f"},
        {'name': "first_layer_size", 'type': "discrete", 'domain': (100,150,200,300)},
        {'name': "second_layer_size", 'type': "discrete", 'domain': (200,300,400,800)},
        {'name': "third_layer_size", 'type': "discrete", 'domain': (0,40,80,160,220,340)},
        {'name': "fourth_layer_size", 'type': "discrete", 'domain': (10,20,30,50)},
        {'name': "no_relu", 'type': "discrete", 'domain': (False, True)},
        # {'name': "nn-linear_state_size", 'type': "discrete", 'domain': (53, 312)},
        ]

    # Define optimizer
    # bayesOpt = BayesianOptimizer(params)
    optim_params = {}
    for player in ('1','2'):
        for op in optim_params_template:
            optim_params[op['name']+player] = op
    bayesOpt = DQNBayesianOptimizer(params, optim_params)
    bayesOpt.optimize_RL(max_iter=MAX_ITER)

    print(f"bayesDqn.py: Bayesian optimization run took {datetime.datetime.now()-start_time}") 
