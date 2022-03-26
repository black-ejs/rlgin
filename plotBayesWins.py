from typing import Union
from collections.abc import Iterable
import sys
import math
import copy
import distutils.util

import numpy as np
import matplotlib.axes as axes
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

import regplot

MA_SIZE = 50
FIGURE_WIDTH = 9
FIGURE_HEIGHT = 4
rl_param_names = ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]

statsList = []
cumulative_averages = []
figures = []
lastOpened = ""
xbnext = [] 
xbprev = []

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
def minmax(array_x):
    max_x = sys.float_info.min
    min_x = sys.float_info.max
    for x in array_x:
        max_x = max(x,max_x)
        min_x = min(x, min_x)   
    return max_x, min_x          

## #############################################
def calc_slope(fit_results, array_x):
    #print(f"{title}: pvalues {fit_results.pvalues}")
    #print(f"{title}: tvalues {fit_results.tvalues}")
    vals = fit_results.fittedvalues
    deltay = vals[-1] - vals[0]
    max_x, min_x = minmax(array_x)
    deltax = max_x-min_x
    if deltax > 0:
        slope = deltay/deltax
    else:
        slope = math.nan
    # print(f"{title}: slope of fittedvalues {slope:1.6f}")
    return slope

## #############################################
def do_splines(which, array_y, array_x, 
                splines:(int)=1, order:(int)=1, 
                ax:(axes.Axes)=None, linecolor="#F49F05"):

    my_array_x = copy.copy(array_x)
    my_array_x.sort()
    spline_length = int(len(my_array_x)/splines)
    results = []
    slopes = []

    for spline in range(splines):
        spline_start = spline*spline_length
        if spline == splines-1:
            spline_end = len(my_array_x)
        else:
            spline_end = spline_start+spline_length
        spline_array_x = my_array_x[spline_start:spline_end]
        spline_array_y = array_y[spline_start:spline_end]
        if which == 'rank':
            fit_results = (
                regplot.polyfit(
                    x=np.array([spline_array_x])[0],
                    y=np.array([spline_array_y])[0],
                    dropna=True,
                    order=order
                ))
        else:                
            fit_results = (
                regplot.regplot(
                    x=np.array([spline_array_x])[0],
                    y=np.array([spline_array_y])[0],
                    color="#36688D",
                    scatter=False,
                    # label='Data',
                    order=order,
                    fit_reg=True,
                    line_kws={"color": linecolor},
                    ax=ax
                ))
        results.append(fit_results)
        slopes.append(calc_slope(fit_results, spline_array_x))

    return slopes

## #############################################

def install_navigation(fig_label):
    button_height=0.075
    rrr = plt.get_figlabels()
    if not fig_label in plt.get_figlabels():
        print(f'wtf: fig_label={fig_label}')
    fig = plt.figure(fig_label)
    axx = fig.subplots_adjust(bottom=0.2, top=0.99, right=0.99)
    axprev = plt.axes([0.77, 0.01, 0.1, button_height])
    axnext = plt.axes([0.89, 0.01, 0.1, button_height])
    bnext = widgets.Button(axnext, 'Next')
    bnext.on_clicked(onclickn)
    bprev = widgets.Button(axprev, 'Previous')
    bprev.on_clicked(onclickp)
    xbprev.append(bprev)
    xbnext.append(bnext)

### #############################################
def do_poly_regression(array_y, array_x,
                        splines:(Union[int,Iterable])=1, order:(int)=1):
    
    if isinstance(splines,Iterable):
        slopes = []
        for spl in splines:
            spline_slopes = do_splines("rank",array_y, array_x, splines=spl, order=order)
            slopes.extend(spline_slopes)                                
    else:
        slopes = do_splines("rank",array_y, array_x, splines=splines, order=order)
    return slopes

# #############################################
def plot_regression(array_y, array_x, title:(str), 
                    splines:(Union[int,Iterable])=1, 
                    order:(int)=1, 
                    ax:(axes.Axes)=None, figure_id:(str)=None,
                    xlabel:(str)=None, ylabel:(str)=None,
                    average_array:(Iterable)=None):
    
    if figure_id == None:
        figure_id = title

    # cid = figure.canvas.mpl_connect('button_press_event', onclick)
    
    figure = plt.figure(figure_id, figsize=(FIGURE_WIDTH,FIGURE_HEIGHT))
    ax = figure.gca()

    # scatter
    regplot.regplot(
        x=np.array([array_x])[0],
        y=np.array([array_y])[0],
        color="#36688D",
        #x_jitter=.1,
        scatter_kws={"color": "#36688D"},
        label='Data',
        order=order,
        fit_reg=False,
        line_kws={"color": "#F49F05"},
        ax=ax
    )

    if isinstance(splines,Iterable):
        linecolors = ["orange","blue","green","violet","yellow"]
        color_ndx=0
        slopes = []
        for spl in splines:
            linecolor = linecolors[color_ndx]
            spline_slopes = do_splines('plot', array_y, array_x, splines=spl, order=order, ax=ax,
                                linecolor=linecolor)
            slopes.extend(spline_slopes)                                
            color_ndx = (color_ndx + 1)%len(linecolors)
    else:
        slopes = do_splines('plot', array_y, array_x, splines=splines, order=order, ax=ax)

    # Plot the average line
    if average_array == None:
        y_mean = [np.mean(array_y)]*len(array_x)
    else:
        while len(average_array) < len(array_x):
            average_array.append(average_array[-1])
        while len(average_array) > len(array_x):
            average_array.pop()
        # y_mean = np.array([average_array])[0]
        y_mean = average_array
    ax.plot(array_x,y_mean, label='Mean', linestyle='--', color="#0F0F00")
    ## ax.legend(loc='lower right')

    if xlabel == None:
        xlabel = "{} (last spline slope={:1.7f})".format(title,slopes[-1])
    if ylabel == None:
        ylabel = "wins last {} hands".format(MA_SIZE)
    ax.set(xlabel=xlabel, ylabel=ylabel)

    plt.draw()

    return slopes

## ##############################
def plot_all_rl_params():
    for param_name in rl_param_names:
        plot_rl_param(param_name)

def plot_rl_param(param_name):
    array_score = []
    array_param = []
    for st in statsList:
        if param_name in st and 'moving_average_spline_slopes' in st:
            slopes = st['moving_average_spline_slopes']
            array_param.append(st[param_name])
            ## array_score.append(st['wins2'])
            array_score.append(slopes[-1])
    
    if len(array_param)>0:
        plot_regression(array_score, array_param, param_name, splines=1,
                ylabel="slope - moving average of wins, last {} hands".format(MA_SIZE))

## ##############################
def plot_all_cumulative_wins():
    for st in statsList:
        plot_cumulative_wins(st)

def rank_all_cumulative_wins():
    for st in statsList:
        plot_cumulative_wins(st, rank_only=True)

def plot_cumulative_wins(st, rank_only:(bool)=False):
    hands = st['hands']
    array_ordinals = []
    array_cumu_wins = []
    for hand in hands:
        array_ordinals.append(int(hand['hand_index']))
        array_cumu_wins.append(int(hand['wins']))

    if rank_only:
        slopes = do_poly_regression(array_cumu_wins,
                        array_ordinals, 
                        splines=3)
    else:                        
        slopes = plot_regression(array_cumu_wins, 
                        array_ordinals, 'cumu - ' + st['name_scenario'], 
                        splines=3,
                        ylabel="cumulative wins   total=" + str(st['wins2']),
                        average_array=cumulative_averages)
    st['cumulative_wins_slopes'] = slopes
    st['cumulative_wins_last_spline_slope'] = slopes[-1]
    st['cumulative_wins_ratio'] = slopes[-1]/slopes[0]

## ##############################
def rank_all_moving_averages():
    for st in statsList:
        _rank_or_plot_ma('rank', st) 
    
def plot_all_moving_averages():
    for st in statsList:
        plot_moving_average(st) 

def rank_moving_average(st):
    return _rank_or_plot_ma('rank', st) 

def plot_moving_average(st):
    return _rank_or_plot_ma('plot', st) 

def _rank_or_plot_ma(which, st):
    array_ma = []
    array_count = []
    ma = st['ma_array']
    for ma_val in ma:
        array_ma.append(ma_val)
        array_count.append(len(array_ma))
        
    if len(array_count)>0:
        if which == 'plot':
            slopes = plot_regression(array_ma, array_count, 
                            st['name_scenario'], splines=[1,3],
                            ylabel="wins last {} hands".format(MA_SIZE))
        else:
            slopes = do_poly_regression(array_ma, array_count, splines=[1,3])
        array_count = []
        array_ma = []
        st['moving_average_overall_slope'] = slopes[0]
        st['moving_average_spline_slopes'] = slopes[1:]
        st['moving_average_last_spline_slope'] = slopes[-1]

## ##############################
## ##############################
def onclickp(event):
    onclick(event, 'p')
def onclickn(event):
    onclick(event, 'n')
def onclick(event,direction):
    # print(f"onclick: direction={direction} event={vars(event)}")
    figure_id = get_figure_id(event)
    #print(f'click: figure_id={figure_id}')
    if figure_id == None:
        return

    for i in range(len(figures)):
        fig_label = figures[i]
        if fig_label == figure_id:
            plt.close(figure_id)
            if direction == 'n':
                fig_label = figures[(i+1)%len(figures)]
            else:
                if i>0:
                    fig_label = figures[i-1]
                else:
                    fig_label = figures[-1]
            if '_struct' in fig_label:
                scenario_string = fig_label[fig_label.find("gin_"):]
                if 'cumu' in fig_label:
                    plot_cumulative_wins(find_stats(scenario_string))
                else:
                    plot_moving_average(find_stats(scenario_string))
            else:
                plot_rl_param(fig_label)

            install_navigation(fig_label)
            global lastOpened
            lastOpened = fig_label

## ##############################
def find_stats(scenario_string):
    for st in statsList:
        if scenario_string in st['name_scenario']:
            return st
    return "dang!"

## ##############################
def get_figure_id(event):
    return lastOpened
    if event.dblclick:
        click_type = 'double'
    else:
        click_type = 'single'
    print(f'{click_type} click: button={event.button}, x={event.x}, y={event.y}, xdata={event.xdata}, ydata={event.ydata}')
    if not hasattr(event,'canvas'):
        print('no canvas attribute')
    elif event.canvas == None:
        print('canvas == None')
    elif not hasattr(event.canvas,'figure'):
        print('no figure attribute on canvas')
    elif event.canvas.figure == None:
        print('canvas.figure == None')
    elif not hasattr(event.canvas.figure,'get_label'):
        print('cannot call get_label() on canvas.figure')

    return  event.canvas.figure.get_label()

## ##############################
## ##############################
## ##############################
## ##############################

def extract_prop(key, line, stats):
    if key in line:
        stats[key] = get_prop(key, line)

def get_prop(key, line):
    cpos = line.find(key)+len(key)+3
    val = line[cpos:]
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
    return val

## ##############################
def parseLogs(filepath:(str), include_partials:(bool)=False): 
    stats = {}
    hands = []
    wins = 0
    ma_window = []
    ma_size = MA_SIZE
    for i in range(ma_size):
        ma_window.append(0)
    ma_count = 0
    ma_name = "Tempo"
    ma_array = []

    with open(filepath, 'r') as f:
        lines=f.readlines()
    for line in lines:
        if "INPUT" in line and len(stats)>0:
            if 'wins2' in stats or include_partials:
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

    if 'wins2' in stats or include_partials:
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
            for hand in st['hands']:
                ndx = int(hand['hand_index'])
                cumu = int(hand['wins'])
                if ndx>=len(cumulative_averages):
                    cumulative_averages.append(cumu)
                else:
                    cumulative_averages[ndx] += cumu
    mean_losses = tot1/count_scenarios
    mean_wins = tot2/count_scenarios 
    for i in range(len(cumulative_averages)):
        cumulative_averages[i]/=count_scenarios             
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
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_logfile',
                    default='logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    parser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='path to the logfile to be plotted')
    args = parser.parse_args()

    parseLogs(args.path_to_logfile, distutils.util.strtobool(args.include_partials))
    #print_statsList()

    print("* * * * * * * * * * * * * * * * * * * ")
    print_score_stats(create_score_stats())
    print("* * * * * * * * * * * * * * * * * * * ")

    rank_all_cumulative_wins()
    rank_all_moving_averages()

    statsList.sort(key=lambda x: x['moving_average_last_spline_slope'])
    print("     -------- name_scenario ----------     \tma_last_slope  ma_overall_slope  cum_last_slope  cum_ratio")
    for st in statsList:
        star = ""
        if not 'wins2' in st:
            star = "*"  # should only happen if "include_partials==True"
        print(f"{star}{st['name_scenario']}:"
                f"\t{st['moving_average_last_spline_slope']: 1.7f}  "
                f"\t{st['moving_average_overall_slope']: 1.7f}"
                f"\t{st['cumulative_wins_last_spline_slope']:1.7f}"
                f"\t{st['cumulative_wins_ratio']:1.7f}"
                )
    print(f"{len(statsList)} scenarios")    

    try:

        #plot_all_rl_params()
        #plot_all_cumulative_wins()
        #plot_all_moving_averages()

        for param_name in rl_param_names:
            figures.append(param_name)

        for st in statsList:
            figures.append(st['name_scenario'])
            figures.append('cumu - ' + st['name_scenario'])

        lastOpened='l1'
        plot_rl_param(lastOpened)
        install_navigation(lastOpened)

        #p=0
        while True:
            plt.pause(0.1)
            if len(plt.get_figlabels())==0:
                break
            #if True: # p==0:
            #    p+=1
            #    mgr = plt.get_current_fig_manager()
            #    print(f'{p} current_fig_manager={mgr}')
            #    print(f'{p}                vals={vars(mgr)}')
            #    print(f'{p}        vals(canvas)={vars(mgr.canvas)}')
                
    finally:
        pass


            

