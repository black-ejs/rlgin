import sys
import regplot
import matplotlib.axes as axes
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np
import math
import copy

MA_SIZE = 50
FIGURE_WIDTH = 11
FIGURE_HEIGHT = 6
NAV_LABEL = 'plot_controls'
statsList = []
rl_param_names = ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]
figures = []
lastOpened = ""

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
    deltay = vals[len(vals)-1] - vals[0]
    max_x, min_x = minmax(array_x)
    deltax = max_x-min_x
    if deltax > 0:
        slope = deltay/deltax
    else:
        slope = math.nan
    # print(f"{title}: slope of fittedvalues {slope:1.6f}")
    return slope

## #############################################
def do_splines(which, array_y, array_x, splines:(int)=1, order:(int)=1, ax:(axes.Axes)=None):

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
                    #x_jitter=.1,
                    scatter=False,
                    label='Data',
                    order=order,
                    fit_reg=True,
                    line_kws={"color": "#F49F05"},
                    ax=ax
                ))
        results.append(fit_results)
        slopes.append(calc_slope(fit_results, spline_array_x))

    return slopes

xbnext = [] 
xbprev = []
## #############################################
def install_navbar():
    figure = plt.figure(NAV_LABEL, figsize=(2,0.2))
    ax1 = figure.add_subplot(1,2,1)
    bprev = widgets.Button(ax1, 'prev', color='yellow', hovercolor='red')
    bprev.on_clicked(onclickl)
    ax2 = figure.add_subplot(1,2,2)
    bnext = widgets.Button(ax2, 'next', color='green', hovercolor='red')
    bnext.on_clicked(onclickr)

    xbprev.append(bprev)
    xbnext.append(bnext)
    cid = figure.canvas.mpl_connect('button_press_event', xxonclick)

### #############################################
def do_poly_regression(array_y, array_x, splines:(int)=1, order:(int)=1):
    return do_splines("rank",array_y, array_x, splines=splines, order=order)

# #############################################
def plot_regression(array_y, array_x, title, splines:(int)=1, order:(int)=1, ax:(axes.Axes)=None, figure_id:(str)=None):
    # sns.set(color_codes=True, font_scale=1.5)
    # sns.set_style("darkgrid")
    
    ##doShow = False
    ##if ax == None:
    ##    figure = plt.figure(figsize=(13,7))
    ##    ax = figure.add_axes([0,0,100,100])    
    ##    doShow = True

    if figure_id == None:
        figure_id = title

    """
    if figure_id in figures:
        figure = figure[figure_id]
    else:
        figure = plt.figure(figure_id,figsize=(FIGURE_WIDTH,FIGURE_HEIGHT))
        figures.append(figure_id)
        cid = figure.canvas.mpl_connect('button_press_event', onclick)
    """
    figure = plt.figure(figure_id, figsize=(FIGURE_WIDTH,FIGURE_HEIGHT))

    ax = plt.gca()

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

    slopes = do_splines('plot', array_y, array_x, splines=splines, order=order, ax=ax)
    slope = slopes[len(slopes)-1]

    # Plot the average line
    y_mean = [np.mean(array_y)]*len(array_x)
    ax.plot(array_x,y_mean, label='Mean', linestyle='--')
    ## ax.legend(loc='lower right')

    xlabel = "{} (last spline slope={:1.7f})".format(title,slope)
    ylabel = "wins last {} hands".format(MA_SIZE)
    ax.set(xlabel=xlabel, ylabel=ylabel)

    ######if doShow:
    plt.draw()
    # plt.show()

    return slopes

## ##############################
def plot_all_rl_params():
    for param_name in rl_param_names:
        plot_rl_param(param_name)

def plot_rl_param(param_name):
    array_score = []
    array_param = []
    for st in statsList:
        if param_name in st and 'moving_average_slopes' in st:
            slopes = st['moving_average_slopes']
            array_param.append(st[param_name])
            ## array_score.append(st['wins2'])
            array_score.append(slopes[len(slopes)-1])
    
    if len(array_param)>0:
        plot_regression(array_score, array_param, param_name, splines=1 )

## ##############################
def plot_all_cumulative_wins():
    for st in statsList:
        plot_cumulative_wins(st)

def plot_cumulative_wins(st):
    hands = st['hands']
    array_ordinals = []
    array_cumu_wins = []
    for hand in hands:
        array_ordinals.append(int(hand['hand_index']))
        array_cumu_wins.append(int(hand['wins']))

    plot_regression(array_cumu_wins, array_ordinals, 'cumu - ' + st['name_scenario'], 
                    splines=3)

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
    array_score = []
    array_param = []
    ma = st['ma_array']
    for ma_val in ma:
        array_param.append(len(array_score))
        array_score.append(ma_val)
        
    if len(array_param)>0:
        if which == 'plot':
            slopes = plot_regression(array_score, array_param, 
                            st['name_scenario'], splines=3)
        else:
            slopes = do_poly_regression(array_score, array_param, splines=3)
        array_param = []
        array_score = []
        st['moving_average_slopes'] = slopes
        st['moving_average_last_spline_slope'] = slopes[len(slopes)-1]

## ##############################
## ##############################
def onclickl(event):
    onclick(event, 'l')
def onclickr(event):
    onclick(event, 'r')
def onclick(event,direction):
    figure_id = get_figure_id(event)
    print(f'click: figure_id={figure_id}')
    if figure_id == None:
        return

    """
    for i in range(len(rl_param_names)):
        param_name = rl_param_names[i]
        print(f"rl_param_names[{i}]={param_name}  figure_id={figure_id}")
        if param_name == figure_id:
            plt.close(figure_id)
            if direction == 'r':
                rl_param_name = rl_param_names[(i+1)%len(rl_param_names)]
            else:
                rl_param_name = rl_param_names[(i-1)%len(rl_param_names)]
            plot_rl_param(rl_param_name)
            global lastOpened
            print(f"lastOpened={lastOpened} (pre)")
            lastOpened = rl_param_name
            print(f"lastOpened={lastOpened} (post)")

            plt.show()
    """
    
    for i in range(len(figures)):
        fig_label = figures[i]
        print(f"figures[{i}]={fig_label}  figure_id={figure_id}")
        if fig_label == figure_id:
            plt.close(figure_id)
            if direction == 'r':
                fig_label = figures[(i+1)%len(figures)]
            else:
                fig_label = figures[(i-1)%len(figures)]
            if '_struct' in fig_label:
                scenario_string = fig_label[20:]
                if 'cumu' in fig_label:
                    plot_cumulative_wins(find_stats(scenario_string))
                else:
                    plot_moving_average(find_stats(scenario_string))
            else:
                plot_rl_param(fig_label)
            global lastOpened
            print(f"lastOpened={lastOpened} (pre)")
            lastOpened = fig_label
            print(f"lastOpened={lastOpened} (post)")

            plt.figure(NAV_LABEL)
            plt.show()

def xxonclick(event):
    figure_id = get_figure_id(event)
    print(f'xxxclick: figure_id={figure_id}')

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
def parseLogs(filepath): 
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
    args = parser.parse_args()

    parseLogs(args.path_to_logfile)
    #print_statsList()

    rank_all_moving_averages()

    print("* * * * * * * * * * * * * * * * * * * ")
    print_score_stats(create_score_stats())
    print("* * * * * * * * * * * * * * * * * * * ")

    statsList.sort(key=lambda x: x['moving_average_last_spline_slope'])
    for st in statsList:
        star = ""
        if not 'wins2' in st:
            star = "*"
        print(f"{st['name_scenario']}: moving_average_last_spline_slope={st['moving_average_last_spline_slope']:1.7f}{star}")

    try:
        #plot_all_rl_params()
        #plot_all_cumulative_wins()
        #plot_all_moving_averages()

        for param_name in rl_param_names:
            figures.append(param_name)

        for st in statsList:
            figures.append(st['name_scenario'])
            figures.append('cumu - ' + st['name_scenario'])

        install_navbar()
        lastOpened='l1'
        plot_rl_param('l1')

        plt.show()

    finally:
        pass


            

