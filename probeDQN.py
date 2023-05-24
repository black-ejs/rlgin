import copy
import datetime
import random
import sys
import time
import argparse
import os
from pathlib import Path

import torch 
import numpy as np

import ginDQNParameters
NO_WIN_NAME = 'nobody'

import learningPlayer

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
        player2 = learningPlayer.learningPlayer(params['player2'])
        nn_params = params['player2']['nn']     
        nn_params['weights_path'] = weightsfile
        player2.get_strategy()

        conv2Dlayer = player2.ginDQN.layers[0]
        conv_weights = conv2Dlayer.weight
        conv_bias = conv2Dlayer.bias
        b0 = conv_bias[0].item()
        b1 = conv_bias[1].item()
        u0 = torch.sub(conv_weights[0],b0)
        u1 = torch.sub(conv_weights[1],b1)
        conv_biased_weights = torch.cat((u0,u1))
        conv_biased_weights = conv_biased_weights.reshape((2,1,4,4))
        print(f"******************************")
        print(f"{weightsfile}")
        print(f"---- Conv2D weights")
        print(f"{conv_weights}")
        print(f"---- Conv2D bias")
        print(f"{conv_bias} - {conv_bias[0].item()} - {conv_bias[1].item()}")
        print(f"---- Conv2D biased weights")
        print(f"{conv_biased_weights}")

        model_id = weightsfile[weightsfile.find("_")+1:weightsfile.find("-")-5]
        heatmap_script += create_heatmap_script(conv_weights,
                                             model_id,"G")
        
        heatmap_script += create_heatmap_script(conv_biased_weights,
                                                 model_id+" biased","R")
        
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
        with torch.no_grad():
            stats = run(probe_params, weights) 
        print_stats(stats)

## #############################################
def create_heatmap(heatmap_script, output_file=None):
    
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    template_filename = "probeDQN.html"

    with open(source_dir / template_filename,"r") as t:
        template = t.readlines()

    if not output_file == None:
        if os.path.isfile(output_file):
            os.unlink(output_file)

    for line in template:
        if "INSERT show_grid() CALLS HERE" in line:
            p2f(heatmap_script,output_file) 
        else:
            p2f(line, output_file)

def create_heatmap_script(conv_weights:torch.Tensor, title:str, color:str="G"):

    my_weights = conv_weights.detach().numpy()

    heatmap_script = ""
    #var_name = "heat_" + str(title.__hash__()).replace("-","_")
    var_name = "heat_" + str(random.randint(0,100000000)).replace("-","_")
    for i in range(2):
        map_title = f"{title} ({i+1})"
        t=my_weights[i][0]
        array_str = np.array2string(t, separator=', ')
        heatmap_script += f"{var_name} = {array_str};\n"
        heatmap_script += f"show_grid({var_name},\"{map_title}\",\"{color}\");\n"

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
    parser.add_argument("--params_module", nargs='?', type=str, default="logs/pad_params")
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    parser.add_argument("--weights_path_2", nargs='?', type=str, default="weights/pad_params_weights.h5.post_training")
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
    params['heatmap_file'] = os.path.expanduser(args.heatmap_file)

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

