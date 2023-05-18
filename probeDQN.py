import copy
import datetime
import time
import sys
import os
import argparse
from pathlib import Path

import numpy as np
import torch 
import torch.optim as optim

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
def run(params:dict,weights:list):
    """
    Use the DQN to play gin, via a ginDQNStrategy            
    """
    stats = Stats()
    stats.put('run_timestamp', datetime.datetime.now())
    stats.put('params', params)

    startTime = time.time()
    print(f"--- PROBE START at {startTime} ---")
    print(params)

    heatmap_script = ""

    for weightsfile in weights:
        player2 = learningPlayer(params['player2'])
        nn_params = params['player2']['nn']     
        nn_params['weights_path'] = weightsfile
        player2.get_strategy()

        conv2Dlayer = player2.ginDQN.layers[0]
        conv_weights = conv2Dlayer.weight
        print(f"{weightsfile}")
        print(f"{conv_weights}")

        heatmap_script += create_heatmap_script(conv_weights,
                                             weightsfile)
        
    create_heatmap(heatmap_script, params['heatmap_file'])

    endTime = time.time()
    total_duration = endTime - startTime
    
    stats.put("start_time", startTime)
    stats.put("end_time", endTime)
    stats.put("total_duration", total_duration)
    print(f"--- PROBE END at {time.time()} ---")

    return stats

## #############################################
def run_probe(params:dict,weights:list):
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
        stats = run(probe_params, weights) 
        print_stats(stats)

## #############################################
def create_heatmap(heatmap_script, output_file=None):
    
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    template_filename = "probeDQN.html"

    with open(source_dir / template_filename,"r") as t:
        template = t.readlines()

    for line in template:
        if "INSERT show_grid() CALLS HERE" in line:
            p2f(heatmap_script,output_file) 
        else:
            p2f(line, output_file)

def create_heatmap_script(conv_weights:torch.Tensor, title:str):

    my_weights = conv_weights.detach().numpy()

    heatmap_script = ""
    var_name = "heat_" + str(title.__hash__()).replace("-","_")
    for i in range(2):
        map_title = f"{title} ({i+1})"
        t=my_weights[i][0]
        array_str = np.array2string(t, separator=', ')
        heatmap_script += f"{var_name} = {array_str};\n"
        heatmap_script += f"show_grid({var_name},\"{map_title}\");\n"
    return heatmap_script

def p2f(data,output_file:str=None):
    if not output_file == None:
        with open(output_file,"a") as o:
            o.write(data)
    else:
        sys.stdout.write(data)

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
    parser.add_argument("--weights_path_2", nargs='?', type=str, default="weights/BLG1")
    parser.add_argument("--heatmap_file", nargs='?', type=str, default="~/gg.html")
    args = parser.parse_args()
    print("probeDQN.py: args ", args)

    if args.weights_path_2 == None:
        print("no weights to load, exiting")
        exit(-1)

    if (args.params_module == None):
        print("using default parameters")
        params = ginDQNParameters.define_parameters()
    else:
        params = import_parameters(args.params_module)

    params['display'] = True
    params['heatmap_file'] = args.heatmap_file

    if not (args.logfile == None):
        params['log_path'] = args.logfile        

    weights=[]
    if os.path.isfile(args.weights_path_2):
        weights.append(args.weights_path_2)
    elif os.path.isdir(args.weights_path_2):
        entries = os.scandir(args.weights_path_2)
        for e in entries:
            if e.is_file():
                weights.append(e.path)
    else:
        weights = args.weights_path_2.split()

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

        run_probe(params, weights)

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not old_stderr == None:
            sys.stderr = old_stderr
        if not log == None:
            log.close()

