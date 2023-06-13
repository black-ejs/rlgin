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
def print_stats(stats, file=None):
    """
    force winMap to be last for parsing
    """
    if file == None:
        file = sys.stdout
    for key, value in stats.items():
        if not key == 'params':
            print(f"{key}: {value}", file=file)

## #############################################
def run(params:dict,weights:list):
    """
    Use the DQN to play gin, via a ginDQNStrategy            
    """
    stats = {}
    stats['run_timestamp'] = datetime.datetime.now()
    stats['params'] = params

    startTime = time.time()
    print(f"--- PROBE START at {startTime} ---")
    print(params)

    run_conv_heatmap(weights,params['heatmap_file'])

    endTime = time.time()
    total_duration = endTime - startTime
    
    stats['start_time']=startTime
    stats['end_time']=endTime
    stats['total_duration']=total_duration
    print(f"--- PROBE END at {time.time()} ---")

    return stats

## #############################################
def run_conv_heatmap(weights:list,output_file:str):
    heatmap_script = ""
    for weightsfile in weights:
        player2 = learningPlayer.learningPlayer(params['player2'])
        nn_params = params['player2']['nn']     
        nn_params['weights_path'] = weightsfile
        player2.get_strategy()

        conv2Dlayer = player2.ginDQN.layers[0]
        conv_weights = conv2Dlayer.weight.clone().detach()
        conv_bias = conv2Dlayer.bias.clone().detach()
        num_kernels = conv_bias.shape[0]
        conv_biased_weights = None
        for kernel_ndx in range(num_kernels):
            b0 = conv_bias[kernel_ndx].item()
            u0 = torch.sub(conv_weights[kernel_ndx],b0)
            if type(None) == type(conv_biased_weights):
                conv_biased_weights = u0.clone().detach()
            else:
                conv_biased_weights = torch.cat((conv_biased_weights,u0))
        conv_biased_weights = conv_biased_weights.reshape((num_kernels,1,4,4))
        print(f"******************************")
        print(f"{weightsfile}")
        print(f"---- Conv2D weights")
        print(f"{conv_weights}")
        print(f"---- Conv2D bias")
        print(f"{conv_bias} - {conv_bias[0].item()} - {conv_bias[1].item()}")
        print(f"---- Conv2D biased weights")
        print(f"{conv_biased_weights}")

        if '_' in weightsfile:
            model_id = weightsfile[weightsfile.find("_")+1:weightsfile.find("-")-5]
        else:
            chunks = weightsfile.split("/")
            generation = chunks[-1].split(".")[-1]
            model_tag = chunks[-3]
            model_id = model_tag + " g" + generation
        print(f"weightsfile={weightsfile}  model_id={model_id}")
        heatmap_script += create_conv_heatmap_script(conv_weights,
                                             model_id,"G")
        
        heatmap_script += create_conv_heatmap_script(conv_biased_weights,
                                                 model_id+" biased","R")
    
    create_conv_heatmap(heatmap_script,output_file)

## #############################################
def run_probe_with_logging(params:dict,weights_path_2:str):
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

        output_file = params['heatmap_file']
        if not output_file == None:
            if os.path.isfile(output_file):
                os.unlink(output_file)

        run_probe(params, weights_path_2)

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not old_stderr == None:
            sys.stderr = old_stderr
        if not log == None:
            log.close()

## #############################################
def run_probe(params:dict,weights_path_2:str):
    weights=[]
    if os.path.isfile(weights_path_2):
        weights.append(weights_path_2)
    elif os.path.isdir(weights_path_2):
        entries = os.scandir(weights_path_2)
        for e in entries:
            if e.is_file():
                weights.append(e.path)
    else:
        weights = weights_path_2.split()
        # see refactor below
        for w_p_2 in weights:
            run_probe(params, w_p_2)
        return  True

    # should refactor to always recurse the list here
    return run_probe_list(params,weights) 

## #############################################
def run_probe_list(params:dict,weights:list):
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
    
    return True

## #############################################
def create_conv_heatmap(heatmap_script, output_file=None):
    
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

## #############################################
def create_conv_heatmap_script(conv_weights:torch.Tensor, title:str, color:str="G"):

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

## #############################################
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
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    ###parser.add_argument("--params_module", nargs='?', type=str, default="logs/pad_params") # default="logs/pad_params")
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="weights/pad_params_weights.h5.post_training")
    ###parser.add_argument("--params_module", nargs='?', type=str, default="params/ginDQNParameters_BLGw17_16") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3  ../BLG/train/analysis/BLGw17.16/weights/weights.h5.4") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights ../BLG/train/analysis/BLGf7.3/weights") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3 ../BLG/train/analysis/BLGf7.3/weights") 
    parser.add_argument("--params_module", nargs='?', type=str, default="params/ginDQNParameters_TPN") 
    parser.add_argument("--weights_path_2", nargs='?', type=str, default="../TPN/scratch/analysis/TPN1/weights/scratchGin_TPN1.1.27.2023-06-12_20-23-22.h5") 
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

    run_probe_with_logging(params, args.weights_path_2)
