import copy
import datetime
import ginDQNParameters
from bayesOpt import TrainingBayesianOptimizer

TRAIN_EPISODES = 5000
MAX_ITER = 25
INITIAL_ITERS = 6
CHANCE_PLAYERONE_BR90=0.1
#################################################################
#   optimizes the parameter sets used by the learningGin module #
#               Sets the  parameters for Bayesian Optimization  #
#################################################################
class DQNBayesianOptimizer(TrainingBayesianOptimizer):
    STRATEGIES = ('nn-convf', 'nn-convb', 'nn-linear')
    def __init__(self, params, optim_params):
        super().__init__(params, optim_params)

    def create_name_scenario(self, inputs):
        name_scenario = 'bo'

        for p in ('player1','player2'):
            p_str="p" + p[-1]
            name_scenario += '_' + p_str
            name_scenario += '_' + f"{self.params[p]['strategy']}"
            if 'nn' in self.params[p]:
                pparams = self.params[p]['nn']
                lr_str='{:.6f}'.format(float(pparams['learning_rate']))[2:]
                ls_str = ""
                for ls in pparams['layer_sizes']:
                    if not len(ls_str)==0:
                        ls_str += "_"
                    ls_str += f"{ls}"

                name_scenario += '_' + ls_str
                name_scenario += '_lr' + lr_str
                name_scenario += '_eps' + f"{pparams['epsilon_decay_linear']:.6f}"
                name_scenario += '_relu' + f"{int(pparams['no_relu'])}"

        return name_scenario                    

    def copy_inputs_to_params(self, inputs:(list),target_params:(dict)):
        pass
            
    def customize_optim_params(self,inputs):
        player_inputs, nonplayer_inputs = self.reshape_inputs(inputs)
        for np_key in nonplayer_inputs:
            self.params[np_key] = nonplayer_inputs[np_key]

        for i in (1,2):
            pi = player_inputs[i-1]
            player_key = 'player' + str(i)
            if 'strategy' in pi:
                self.params[player_key]['strategy'] = pi['strategy']
            if not 'nn' in self.params[player_key]:
                if 'nn-common' in self.params:
                    self.params[player_key]['nn'] = copy.deepcopy(self.params['nn-common'])
                else:
                    self.params[player_key]['nn'] = {}
            target = self.params[player_key]['nn']
            for nn_param in ('no_relu', 'learning_rate', 'epsilon_decay_linear'):
                if nn_param in pi:
                    target[nn_param] = pi[nn_param]

            layer_sizes = []
            for ls_param in ('first','second','third','fourth'):
                ls = int(pi[ls_param+'_layer_size'])
                if ls > 0:
                    layer_sizes.append(ls)
            target['layer_sizes'] = layer_sizes

    def reshape_inputs(self, inputs):
        player_inputs = [{},{}]
        nonplayer_inputs = {}
        for i in range(len(inputs)):
            name = self.optim_params[i]['name']
            if name[-1] in ('1','2'):
                key = name[:-1]
                target = player_inputs[int(name[-1])-1]
                if key == 'strategy':
                    target[key] = DQNBayesianOptimizer.STRATEGIES[int(inputs[i])]
                else:
                    target[key] = inputs[i]
            else:
                nonplayer_inputs[name] = inputs[i]

        return player_inputs, nonplayer_inputs
#################################################################
##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(f"bayesDqn.py: Bayesian optimization starting at {datetime.datetime.now()}") 

    # obtain basic static params
    params = ginDQNParameters.define_parameters()
    
    # set up logging, 
    params['episodes'] = TRAIN_EPISODES
    params['log_path'] = 'logs/bayesDqn_log.' + params['timestamp']+'.txt'

    # list of indexes for strategies (bayesian params seemingly cannot be strings?)
    strategies = []
    for i in range(len(DQNBayesianOptimizer.STRATEGIES)):
        strategies.append(i)

    # initialize bayesian parameter list
    optim_params_template = [
        {'name': "strategy", 'type': "discrete", 
                'domain': strategies},       # index to DQNBayesianOptimizer.STRATEGIES
        {'name': "learning_rate", 'type': "continuous", 'domain': (0.0001, 0.01)},
        {'name': 'epsilon_decay_linear', 'type': "continuous", 'domain': (float(8/params['episodes']),
                                                                         float(128/params['episodes'])), "fmt": "2.5f"},
        {'name': "first_layer_size", 'type': "discrete", 'domain': (100,150,200,300)},
        {'name': "second_layer_size", 'type': "discrete", 'domain': (200,300,400,800)},
        {'name': "third_layer_size", 'type': "discrete", 'domain': (0,40,80,160,220,340)},
        {'name': "fourth_layer_size", 'type': "discrete", 'domain': (10,20,30,50)},
        {'name': "no_relu", 'type': "discrete", 'domain': (0, 1)},
        # {'name': "nn-linear_state_size", 'type': "discrete", 'domain': (53, 312)},
        ]

    # Define optimizer
    # bayesOpt = BayesianOptimizer(params)
    optim_params = []
    for player in ('1','2'):
        for op in optim_params_template:
            target_param = copy.deepcopy(op)
            target_param['name'] += player 
            optim_params.append(target_param)
    bayesOpt = DQNBayesianOptimizer(params, optim_params)
    bayesOpt.optimize_RL(max_iter=MAX_ITER, initial_iters=INITIAL_ITERS)

    print(f"bayesDqn.py: Bayesian optimization run took {datetime.datetime.now()-start_time}") 
