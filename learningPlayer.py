import copy 

import torch 
import torch.optim as optim

import playGin

import DQN
import ginDQN
from ginDQNLinear import ginDQNLinear
from ginDQNLinearB import ginDQNLinearB
from ginDQNConvFHandOut import ginDQNConvFHandOut
from ginDQNHandOutStrategy import ginDQNHandOutStrategy, ginHandOutBenchmarkStrategy
from playGin import BrainiacGinStrategy

class learningPlayer:
    def __init__(self, params):
        self.params = params
        self.name = params['name']
        self.strategy = params['strategy']
        self.ginDQN = None
        self.pretrain_weights = None

    def is_nn_player(self):
        return "nn-" in self.strategy
    
    def get_strategy(self):
        if self.is_nn_player():
            return self.get_nn_strategy()
        else:
            return playGin.get_strategy(self.strategy)

    def get_nn_strategy(self):
        dqn_params = self.params['nn']
        if self.ginDQN == None:
            self.ginDQN = self.initializeDQN(dqn_params)
        if isinstance(self.ginDQN, ginDQNConvFHandOut):
            nn_strategy = ginDQNHandOutStrategy(dqn_params, self.ginDQN)
            nn_strategy.benchmark_scorer = ginHandOutBenchmarkStrategy()
        else:
            nn_strategy = ginDQN.ginDQNStrategy(dqn_params, self.ginDQN)
            nn_strategy.benchmark_scorer = BrainiacGinStrategy()
        return nn_strategy

    def initializeDQN(self,params):
        params['output_size'] = 1    

        if self.strategy == "nn-linear":
            ginDQN = ginDQNLinear(params)
        elif self.strategy == "nn-linearb":
            ginDQN = ginDQNLinearB(params)
        elif self.strategy == "nn-cfhp":
            ginDQN = ginDQNConvFHandOut(params)

        print(f"sending DQN ({self.strategy}/{type(ginDQN).__name__}) to DEVICE ('{DQN.DEVICE}') for player {self.name}")
        ginDQN = ginDQN.to(DQN.DEVICE)

        if params['train']:
            ginDQN.optimizer = optim.Adam(ginDQN.parameters(), 
                                weight_decay=0, lr=params['learning_rate'])

        if ginDQN.load_weights_success:
            print(f"weights loaded from {ginDQN.weights_path} for player '{self.name}' with strategy '{self.strategy}'")
            if params['train']:
                self.pretrain_weights = copy.deepcopy(ginDQN.state_dict())
        elif params['load_weights']:
            print(f"***** WARING: weights not loaded from {params['weights_path']} for player '{self.name}' with strategy '{self.strategy}', what happened?")            

        return ginDQN

    def replay_new(self):
        if self.is_nn_player():
            self.ginDQN.replay_new(self.ginDQN.memory, self.params['nn']['batch_size'])

    def save_weights(self, weights_file:str=None):
        if weights_file==None:
            weights_file =  self.params['nn']['weights_path']
        if self.is_nn_player():
            weights_to_save = self.ginDQN.state_dict()
            torch.save(weights_to_save,weights_file)
            print(f"weights saved to {weights_file}")
            return weights_to_save

