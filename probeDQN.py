import copy
import datetime
import time
import sys
import os
import argparse

import torch.optim as optim
import torch 

import DQN 
from playGin import BrainiacGinStrategy
import playGin 
import ginDQN
import ginDQNParameters
from ginDQNConvoBitPlanes import ginDQNConvoBitPlanes
from ginDQNConvoFloatPlane import ginDQNConvoFloatPlane
from ginDQNLinear import ginDQNLinear
from ginDQNLinearB import ginDQNLinearB
import ginDQNConvFHandOut
NO_WIN_NAME = 'nobody'

## #############################################
## #############################################
class Stats:
    def __init__(self):
        self.stats = {}    

    def put(self, key, value):
        self.stats[key]=value

    def get(self, key): 
        if key in self.stats:
            return self.stats[key]
        return "unknown statistic"

## #############################################
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
        if self.strategy == "nn-cfh":
            nn_strategy = ginDQNConvFHandOut.ginDQNHandOutStrategy(dqn_params, self.ginDQN)
            nn_strategy.benchmark_scorer = ginDQNConvFHandOut.ginHandOutBenchmarkStrategy ()
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
        elif self.strategy == "nn-convf":
            ginDQN = ginDQNConvoFloatPlane(params)
        elif self.strategy == "nn-convb":
            ginDQN = ginDQNConvoBitPlanes(params)    
        elif self.strategy == "nn-cfh":
            ginDQN = ginDQNConvFHandOut.ginDQNConvFHandOut(params)

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

## #############################################
def print_stats(stats, file=None):
    """
    force winMap to be last for parsing
    """
    if file == None:
        file = sys.stdout
    for key, value in stats.stats.items():
        if not key == 'params':
            print(f"{key}: {value}", file=file)

## #############################################
def run(params):
    """
    Use the DQN to play gin, via a ginDQNStrategy            
    """
    stats = Stats()
    stats.put('run_timestamp', datetime.datetime.now())
    stats.put('params', params)

    startTime = time.time()
    print(f"--- PROBE START at {startTime} ---")
    print(params)

    player1 = learningPlayer(params['player1'])
    player2 = learningPlayer(params['player2'])
    players = [player1, player2]
    nn_players = []
    for p in players:
        if p.is_nn_player():
            nn_players.append(p)
            p.get_strategy()

    for p in nn_players:
        conv2Dlayer = p.ginDQN.layers[0]
        conv_weights = conv2Dlayer.weight
        print(f"{conv_weights}")

    endTime = time.time()
    total_duration = endTime - startTime
    
    stats.put("start_time", startTime)
    stats.put("end_time", endTime)
    stats.put("total_duration", total_duration)
    print(f"--- PROBE END at {time.time()} ---")

    return stats

## #############################################
def run_probe(params):
    probe_params = copy.deepcopy(params)
    do_probe = False
    for p in ('player1', 'player2'):
        if 'nn' in probe_params[p]:
            nnp = probe_params[p]['nn']
            nnp['pretest']=False
            nnp['test']=False
            nnp['train']=True
            nnp['load_weights']=True
            do_probe = True

    if do_probe:
        probe_params['episodes']=0
        print("Probing...")
        stats = run(probe_params) 
        print_stats(stats)

## #############################################

## #############################################
## #############################################
## #############################################
import importlib
def import_parameters(parameters_file:str) -> dict:
    package_name = ""
    parameters_file=os.path.expanduser(parameters_file)
    module_name=parameters_file.replace("/",".")
    if package_name == "":
        print(f"importing params from: {module_name}")
    else:
        print(f"importing params from: {module_name} in package {package_name}")
    p=importlib.import_module(module_name)
    params = p.define_parameters()
    return params

## #############################################
if __name__ == '__main__':

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--params_module", nargs='?', type=str, default="logs/ginDQNParameters_probe")
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    parser.add_argument("--weights_path_2", nargs='?', type=str, default="weights/BLGlrc2.12_weights.h5.1")
    args = parser.parse_args()
    print("learningGin: args ", args)

    if (args.params_module == None):
        print("using default parameters")
        params = ginDQNParameters.define_parameters()
    else:
        params = import_parameters(args.params_module)

    params['display'] = True

    if not (args.logfile == None):
        params['log_path'] = args.logfile        
    for player_index in ("1","2"):
        player_key="player" + player_index
        for key_root in ["weights_path"]:
            params_key=key_root
            args_key=f"{key_root}_{player_index}"
            argvars = vars(args)
            if (args_key in argvars) and (not (argvars[args_key] == None)):
                param_val = argvars[args_key]
                if isinstance(param_val,str):
                    param_val=os.path.expanduser(param_val)
                if 'nn' in params[player_key]:
                    params[player_key]['nn'][params_key]  = param_val
                else:
                    print(f"*** WARNING, --{args_key} specified but {player_key} is not a neural net ")

    old_stdout = None
    old_stderr = None
    log = None
    try:
            
        if 'log_path' in params:
            log_path = params['log_path']
            log_path = os.path.expanduser(log_path)
            if len(log_path)>0:
                log = open(log_path, "w")
                if log.writable:
                    old_stdout = sys.stdout
                    sys.stdout = log
                    old_stderr = sys.stderr
                    sys.stderr = log


        run_probe(params)

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not old_stderr == None:
            sys.stderr = old_stderr
        if not log == None:
            log.close()

