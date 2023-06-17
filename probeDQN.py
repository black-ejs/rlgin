import copy
import datetime
import random
import sys
import time
import argparse
import os
from pathlib import Path

import torch 
import torch.nn as nn
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
    print(f"--- probeDQN: PROBE START at {startTime} ---")
    print(params)

    print(f"   --- probeDQN: conv layer probe ---")
    run_conv_heatmap(weights,params['heatmap_file'])

    print(f"   --- probeDQN: linear layers probe ---")
    run_linear_heatmap(weights,params['heatmap_file']+"_l_")

    if len(weights) > 1:
        print(f"   --- probeDQN: by-layer comparisons ---")
        for w_ndx in range(len(weights)-1):
            w1=weights[w_ndx]
            for w2 in weights[w_ndx+1:]:
                if not w1==w2:
                    compare_weights(w1,w2) 

    endTime = time.time()
    total_duration = endTime - startTime
    
    stats['start_time']=startTime
    stats['end_time']=endTime
    stats['total_duration']=total_duration
    print(f"--- probeDQN: PROBE END at {time.time()} ---")

    return stats

## #############################################
def compare_weights(weights1,weights2):
    model_ids=[]
    models = []
    print(f"** ** ** ** ** ** ** ** ** ** ** ** ** ** **")
    for weightsfile in (weights1,weights2):
        player2 = learningPlayer.learningPlayer(params['player2'])
        nn_params = params['player2']['nn']     
        nn_params['weights_path'] = weightsfile
        player2.get_strategy()
        models.append(player2.ginDQN)
        model_ids.append(extract_model_id(weightsfile))
    
    layer_weights = []
    for model in models:
        my_weights=[]
        for layer_ndx in range(0,len(model.layers)):
            my_weights.append(model.layers[layer_ndx].weight)
        layer_weights.append(my_weights)

    print(f"            ** ** ** ** ** ** **")
    for layer_ndx in range(len(layer_weights[0])):
        diffs = torch.eq(layer_weights[0][layer_ndx], layer_weights[1][layer_ndx])
        print(f"{model_ids[0]} vs {model_ids[1]}: layer {layer_ndx}")
        if torch.all(diffs):
            print("this layer is identical in both models")
        else:
            print(f" --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---")
            print("this layer is different in the two models")
            print(diffs)

## #############################################
def run_linear_heatmap(weights:list,output_file:str):
    heatmap_script = ""
    for weightsfile in weights:
        model_id = extract_model_id(weightsfile)
        print(f"******************************")
        print(f"weightsfile={weightsfile}  model_id={model_id}")
        
        player2 = learningPlayer.learningPlayer(params['player2'])
        nn_params = params['player2']['nn']     
        nn_params['weights_path'] = weightsfile
        player2.get_strategy()

        for layer_ndx in range(1,len(player2.ginDQN.layers)):
            llayer = player2.ginDQN.layers[layer_ndx]
            lin_weights = llayer.weight
            lin_bias = llayer.bias
            print(f"---- Linear Layer {layer_ndx} weights")
            print(f"{lin_weights}")
            print(f"---- Linear Layer {layer_ndx} bias")
            print(f"{lin_bias}")
            #print(f"---- Linear Layer {layer_ndx} biased weights")
            #print(f"{conv_biased_weights}")

## #############################################
def extract_model_id(weightsfile:str) ->str:
    if '_' in weightsfile:
        model_id = weightsfile[weightsfile.find("_")+1:weightsfile.find("-")-5]
    else:
        chunks = weightsfile.split("/")
        generation = chunks[-1].split(".")[-1]
        model_tag = chunks[-3]
        model_id = model_tag + " g" + generation
    return model_id

## #############################################
def run_conv_heatmap(weights:list,output_file:str):
    heatmap_script = ""
    for weightsfile in weights:
        model_id = extract_model_id(weightsfile)
        print(f"******************************")
        print(f"weightsfile={weightsfile}  model_id={model_id}")

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
        print(f"---- Conv2D weights")
        print(f"{conv_weights}")
        print(f"---- Conv2D bias")
        print(f"{conv_bias} - {conv_bias[0].item()} - {conv_bias[1].item()}")
        print(f"---- Conv2D biased weights")
        print(f"{conv_biased_weights}")

        heatmap_script += create_conv_heatmap_script(conv_weights,
                                             model_id,"G")
        
        heatmap_script += create_conv_heatmap_script(conv_biased_weights,
                                                 model_id+" biased","R")
    
    create_conv_heatmap(heatmap_script,output_file)

## #############################################
def expand_weights_path_2(weights_path_2:str):
    weights=[]
    expanded_weights_path_2 = os.path.expanduser(weights_path_2)
    if os.path.isfile(expanded_weights_path_2):
        weights.append(expanded_weights_path_2)
    elif os.path.isdir(expanded_weights_path_2):
        entries = os.scandir(expanded_weights_path_2)
        for e in entries:
            if e.is_file():
                weights.append(e.path)
    else:
        ww = weights_path_2.split()
        for w in ww:
            if not os.path.exists(w):
                raise Exception(f"weights_path_2 specified does not exist: {w}")
            weights.extend(expand_weights_path_2(w))
    
    return weights

## #############################################
def run_probe(params:dict,weights_path_2:str):
    weights=expand_weights_path_2(weights_path_2)
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
    for i in range(conv_weights.shape[0]):
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
    parser.add_argument("--logfile", nargs='?', type=str, default="logs/probe")
    parser.add_argument("--heatmap_file", nargs='?', type=str, default="~/gg.html")

    ###parser.add_argument("--params_module", nargs='?', type=str, default="logs/pad_params") # default="logs/pad_params")
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="weights/pad_params_weights.h5.post_training")

    ###parser.add_argument("--params_module", nargs='?', type=str, default="params/ginDQNParameters_BLGw17_16") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3  ../BLG/train/analysis/BLGw17.16/weights/weights.h5.4") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights ../BLG/train/analysis/BLGf7.3/weights") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGw17.16/weights/weights.h5.3 ../BLG/train/analysis/BLGf7.3/weights") 

    ###parser.add_argument("--params_module", nargs='?', type=str, default="params/ginDQNParameters_TPN") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../TPN/scratch/analysis/TPN1/weights/scratchGin_TPN1.1.22.2023-06-13_22-30-01.h5") 
    #parser.add_argument("--weights_path_2", nargs='?', type=str, default="../TPN/scratch/analysis/TPN1/weights/scratchGin_TPN1.1.22.2023-06-13_22-30-01.h5 ../TPN/scratch/analysis/TPN1/weights/scratchGin_TPN1.1.78.2023-06-15_04-23-36.h5") 

    parser.add_argument("--params_module", nargs='?', type=str, default="params/ginDQNParameters_BLGw17_7") 
    parser.add_argument("--weights_path_2", nargs='?', type=str, default="../BLG/train/analysis/BLGwi17.7/weights") 

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

    # step on what is supplied in the paramss, that was intended for training logs
    params['log_path'] = args.logfile
    if params['log_path'] == None:
        params.pop('log_path')

    run_probe_with_logging(params, args.weights_path_2)
