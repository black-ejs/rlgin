import copy
import datetime
import random
import ginDQNParameters
from bayesOpt import TrainingBayesianOptimizer

TRAIN_EPISODES = 5000
MAX_ITER = 50   
INITIAL_ITERS = 40
#################################################################
#   optimizes the parameter sets used by the learningGin module #
#               Sets the  parameters for Bayesian Optimization  #
#################################################################
class LinearbBayesianOptimizer(TrainingBayesianOptimizer):
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
                
                gamma_str='{:.6f}'.format(float(pparams['gamma']))[2:]
                name_scenario += '_' + gamma_str

        print(f"name_scenario is {name_scenario  }")
        return name_scenario                    

    def copy_inputs_to_params(self, inputs:(list),target_params:(dict)):
        pass
            
    def customize_optim_params(self,inputs):  
        timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        self.params['timestamp'] = timestamp
        self.params['timestamp'] = timestamp

        player_inputs, nonplayer_inputs = self.reshape_inputs(inputs)
        for np_key in nonplayer_inputs:
            self.params[np_key] = nonplayer_inputs[np_key]

        for i in (1,2):
            pi = player_inputs[i-1]
            player_key = 'player' + str(i)
            if 'strategy' in pi:
                self.params[player_key]['strategy'] = pi['strategy']
                if pi['strategy'][:3] == "nn-": 
                    if not 'nn' in self.params[player_key]:
                        if 'nn-common' in self.params:
                            self.params[player_key]['nn'] = copy.deepcopy(self.params['nn-common'])
                        else:
                            self.params[player_key]['nn'] = {}
                    target = self.params[player_key]['nn']

                    if 'use_cheat_rewards' in self.params and self.params['use_cheat_rewards']:
                        target['gamma'] = 0.1
                    else:
                        target['gamma'] = self.getta_gamma(pi['gamma'])

                    target['weights_path'] = "weights/weights." + pi['strategy'] + "." + timestamp + ".h5"

    def reshape_inputs(self, inputs):
        player_inputs = [{},{}]
        nonplayer_inputs = {}
        for i in range(len(inputs)):
            name = self.optim_params[i]['name']
            if name[-1] in ('1','2'):
                key = name[:-1]
                target = player_inputs[int(name[-1])-1]
                if key == 'strategy':
                    target[key] = "nn-linearb"
                else:
                    target[key] = inputs[i]
            else:
                nonplayer_inputs[name] = inputs[i]

        return player_inputs, nonplayer_inputs

    def getta_gamma(self, input_gamma):
        
        my_scale = float(input_gamma)
        # g = 1 - (random.random() * (10**-my_scale))
        # g = 0.90 + my_scale
        #g = round(g,5)
        g = round(my_scale,5)
        return g

#################################################################
##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(f"Linearb optimization starting at {datetime.datetime.now()}") 

    # obtain basic static params
    params = ginDQNParameters.define_parameters()
    
    # set up logging, 
    params['episodes'] = TRAIN_EPISODES
    params['log_path'] = 'logs/bayesDqn_log.' + params['timestamp']+'.txt'

    # initialize bayesian parameter list
    optim_params_template = [
        {'name': "strategy", 'type': "discrete", 'domain': (0.0, 0.1)},
        {'name': "gamma", 'type': "continuous", 'domain': (0.85,0.98)},
        ]

    # Define optimizer
    # bayesOpt = BayesianOptimizer(params)
    optim_params = []
    for player in ('2'):
        for op in optim_params_template:
            target_param = copy.deepcopy(op)
            target_param['name'] += player 
            optim_params.append(target_param)
    bayesOpt = LinearbBayesianOptimizer(params, optim_params)
    bayesOpt.optimize_RL(max_iter=MAX_ITER, initial_iters=INITIAL_ITERS)

    print(f"Linearb optimization run took {datetime.datetime.now()-start_time}") 
