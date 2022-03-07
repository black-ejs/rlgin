import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import math
import plotBayes

count_stats = 0
statsList = []

def extract_prop(key, line, stats):
    if key in line:
        stats[key] = get_prop(key, line)

def get_prop(key, line):
    cpos = line.find(key)+len(key)+3
    val = line[cpos:]
    # print (f"valA={val}")
    if val[0] == '"':
        delim='"'
        val = val[1:]
    elif val[0] == "'":
        delim="'"
        val = val[1:]
    elif val[0] == "[":
        delim="]"
        val = val[1:]
    else:
        delim=","
    val = val[:val.find(delim)]
    # print (f"valB={val}")
    return val

def print_stats(stats):
    for key in stats.keys():
        print(f"{key}={stats[key]}")

def save_stats(stats):
    statsList.append(stats)
    plotBayes.count_stats+=1
    # print_stats(stats)

def print_statsList():
    for stats in statsList:
        print_stats(stats)

## #############################################
def plot_seaborn(array_score, array_param, param_name, train):
    sns.set(color_codes=True, font_scale=1.5)
    sns.set_style("white")
    plt.figure(figsize=(13,7))
    fit_reg = False if train== False else True        
    ax = sns.regplot(
        x=np.array([array_param])[0],
        y=np.array([array_score])[0],
        color="#36688D",
        #x_jitter=.1,
        scatter_kws={"color": "#36688D"},
        label='Data',
        fit_reg = fit_reg,
        line_kws={"color": "#F49F05"}
    )
    # Plot the average line
    y_mean = [np.mean(array_score)]*len(array_param)
    ax.plot(array_param,y_mean, label='Mean', linestyle='--')
    ax.legend(loc='upper right')
    ax.set(xlabel=param_name, ylabel='score')
    plt.show()

## ##############################
def plot_statsList():
    for param_name in ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]:
        array_score = []
        array_param = []
        for st in statsList:
            if param_name in st and 'wins2' in st:
                array_param.append(st[param_name])
                array_score.append(st['wins2'])
        
        if len(array_param)>0:
            plot_seaborn(array_score, array_param, param_name, True)

## ##############################
def parseLogs(filepath):
    stats = {}
    count_stats = 0

    with open(filepath, 'r') as f:
        lines=f.readlines()
    for line in lines:
        if "INPUT" in line and len(stats)>0:
            save_stats(stats)
            stats = {}
        if "winMap:" in line:
            cpos = line.find(",")
            stats['wins1'] = int(line[cpos-3:cpos])
            cpos +=1
            cpos = line[cpos:].find(",")+cpos
            stats['wins2'] = int(line[cpos-3:cpos])
        extract_prop("name_scenario", line,stats)
        if "learning_rate" in line:
            lr = get_prop("learning_rate", line)
            stats["learning_rate"] = float(lr)
        if "epsilon_decay_linear" in line:
            eps = get_prop("epsilon_decay_linear", line)
            stats["epsilon_decay_linear"] = float(eps)
        if "layer_sizes" in line:
            ls = get_prop("layer_sizes", line)
            # print(f"ls={ls}")
            layers = ls.split(",")
            stats["l1"] = int(layers[0])
            stats["l2"] = int(layers[1])
            stats["l3"] = int(layers[2])

    save_stats(stats)

## ##############################
def create_score_stats():
    score_stats={}
    count = 0
    tot1 = 0
    tot2 = 0
    for st in statsList:
        if 'wins2' in st:
            count+=1
            tot1+= st['wins1']
            tot2+= st['wins2']
    mean_losses = tot1/count
    mean_wins = tot2/count      
    score_stats['mean_losses']=mean_losses
    score_stats['mean_wins']=mean_wins
    for st in statsList:
        if 'wins2' in st:
            count+=1
            tot1 += (st['wins1']-mean_losses)**2
            tot2 += (st['wins2']-mean_wins)**2
    score_stats['std_losses']=math.sqrt(tot1/count)
    score_stats['std_wins']=math.sqrt(tot2/count)
    
    return score_stats

## ##############################
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_logfile',
                    default='logs/megalog', 
                    nargs='?', help='path to the logfile to be plotted')
    args = parser.parse_args()

    parseLogs(args.path_to_logfile)
    #print_statsList()

    print(create_score_stats())

    plot_statsList()
            

