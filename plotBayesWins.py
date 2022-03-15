import regplot
import matplotlib.pyplot as plt
import numpy as np
import math

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
        if not key == "hands":
            print(f"{key}={stats[key]}")

def print_score_stats(score_stats):
    for key in score_stats.keys():
        print(f"{key}={score_stats[key]}")

def save_training_session(stats, hands, ma_array):
    stats['hands'] = hands
    stats['ma_array'] = ma_array
    statsList.append(stats)

def print_statsList():
    for stats in statsList:
        print_stats(stats)

## #############################################
def do_poly_regression(array_y, array_x, title, order:(int)=1):
    fit_results = regplot.polyfit(
        x=np.array([array_x])[0],
        y=np.array([array_y])[0],
        dropna=True,
        order=order
    )
    return report_regression(fit_results, array_x, title)

## #############################################
def report_regression(fit_results, array_x, title):
    #print(f"{title}: pvalues {fit_results.pvalues}")
    #print(f"{title}: tvalues {fit_results.tvalues}")
    vals = fit_results.fittedvalues
    deltay = vals[len(vals)-1] - vals[0]
    deltax = array_x[len(array_x)-1] - array_x[0]
    slope = deltay/deltax;
    print(f"{title}: slope of fittedvalues {slope:1.6f}")
    return slope

## #############################################
def plot_regression(array_y, array_x, title, order:(int)=1):
    # sns.set(color_codes=True, font_scale=1.5)
    # sns.set_style("darkgrid")
    plt.figure(figsize=(13,7))
    ax = plt.gca()      
    fit_results = regplot.regplot(
        x=np.array([array_x])[0],
        y=np.array([array_y])[0],
        color="#36688D",
        #x_jitter=.1,
        scatter_kws={"color": "#36688D"},
        label='Data',
        order=order,
        fit_reg=True,
        line_kws={"color": "#F49F05"},
        ax=ax
    )
    # Plot the average line
    y_mean = [np.mean(array_y)]*len(array_x)
    ax.plot(array_x,y_mean, label='Mean', linestyle='--')
    ax.legend(loc='lower right')

    slope = report_regression(fit_results, array_x, title)
    ylabel = "wins (slope={:1.7f})".format(slope)
    ax.set(xlabel=title, ylabel=ylabel)
    plt.show()
    return slope

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
            plot_regression(array_score, array_param, param_name)

## ##############################
def plot_wins_trend():
    for st in statsList:
        hands = st['hands']
        array_ordinals = []
        array_cumu_wins = []
        for hand in hands:
            array_ordinals.append(int(hand['hand_index']))
            array_cumu_wins.append(int(hand['wins']))

        plot_regression(array_cumu_wins, array_ordinals, st['name_scenario'])

## ##############################
def rank_moving_average():
    return _rank_or_plot_ma('rank')
    
def plot_moving_average():
    return _rank_or_plot_ma('plot')

def _rank_or_plot_ma(which):
    array_score = []
    array_param = []
    max_slope = -10000000
    min_slope = 10000000
    for st in statsList:
        ma = st['ma_array']
        for ma_val in ma:
            array_param.append(len(array_score))
            array_score.append(ma_val)
        if len(array_param)>0:
            if which == 'plot':
                slope = plot_regression(array_score, array_param, st['name_scenario'])
            else:
                slope = do_poly_regression(array_score, array_param, st['name_scenario'])
            array_param = []
            array_score = []
            if slope > max_slope:
                max_slope = slope
            if slope < min_slope:
                min_slope = slope
            st['moving_avarage_slope'] = slope
    return max_slope

## ##############################
def parseLogs(filepath):
    stats = {}
    hands = []
    wins = 0
    ma_window = []
    ma_size = 100
    for i in range(ma_size):
        ma_window.append(0)
    ma_count = 0
    ma_name = "Tempo"
    ma_array = []

    with open(filepath, 'r') as f:
        lines=f.readlines()
    for line in lines:
        if "INPUT" in line and len(stats)>0:
            save_training_session(stats, hands, ma_array)
            for i in range(ma_size):
                ma_window.append(0)    
            ma_array = []
            ma_count = 0
            stats = {}
            hands = []
            wins = 0
        if "Winner: " in line:
            ## cumulative wins
            toks = line.split()
            hand_index = toks[1]
            winner = toks[3]
            if winner == "Tempo":
                wins = wins + 1
            hands.append({'hand_index': hand_index, 
                            'winner': winner, 
                            'wins': wins})
            ## moving average wins
            ma_count += 1
            name=line.split()[3]
            if ma_name in name:
                w = 1
            else:   
                w = 0
            ma_window[ma_count%ma_size] = w
            if ma_count>ma_size:
                # ma_array.append(float(sum(ma_window))/float(len(ma_window)))                            
                ma_array.append(sum(ma_window))                            
        if "winMap: " in line:
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

    save_training_session(stats, hands, ma_array)

## ##############################
def create_score_stats():
    score_stats={}
    count_scenarios = 0
    count_hands = 0
    tot1 = 0
    tot2 = 0
    min1 = 100000
    min2 = 100000
    max1 = -1
    max2 = -1
    minr = 100000
    maxr = -1
    for st in statsList:
        if 'wins2' in st:
            count_scenarios+=1
            count_hands += len(st['hands'])
            w1 = st['wins1']
            w2 = st['wins2']
            tot1+= w1
            tot2+= w2
            if w1>max1:
                max1=w1
            if w2>max2:
                max2=w2
            if w1<min1:
                min1=w1
            if w2<min2:
                min2=w2
            ratio = w1/w2
            if ratio>maxr:
                maxr=ratio
            if ratio<minr:
                minr=ratio
    mean_losses = tot1/count_scenarios
    mean_wins = tot2/count_scenarios      
    score_stats['mean_losses']=mean_losses
    score_stats['mean_wins']=mean_wins
    score_stats['max_losses']=max1
    score_stats['max_wins']=max2
    score_stats['min_losses']=min1
    score_stats['min_wins']=min2
    score_stats['max_ratio']=maxr
    score_stats['min_ratio']=minr
    score_stats['count_hands']=count_hands
    score_stats['count_scenarios']=count_scenarios
    for st in statsList:
        if 'wins2' in st:
            tot1 += (st['wins1']-mean_losses)**2
            tot2 += (st['wins2']-mean_wins)**2
    score_stats['std_losses']=math.sqrt(tot1/count_scenarios)
    score_stats['std_wins']=math.sqrt(tot2/count_scenarios)
    
    return score_stats

## ##############################
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_logfile',
                    default='logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    args = parser.parse_args()

    parseLogs(args.path_to_logfile)
    #print_statsList()

    print("* * * * * * * * * * * * * * * * * * * ")
    print_score_stats(create_score_stats())
    print("* * * * * * * * * * * * * * * * * * * ")

    # plot_statsList()
    # plot_wins_trend()
    rank_moving_average()
    plot_moving_average()

            

