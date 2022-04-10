from collections.abc import Iterable
import math
import distutils.util

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

import regressionPlotter

MA_SIZE = 50

## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################

## #############################################
class TrainingPlotter(regressionPlotter.RegressionPlotter):

    ## ##############################
    def rank_all_cumulative_wins(statsList):
        for st in statsList:
            TrainingPlotter.plot_cumulative_wins(st, rank_only=True)

    def plot_cumulative_wins(st, cumulative_averages:(Iterable)=None,
                            rank_only:(bool)=False):
        hands = st['hands']
        array_ordinals = []
        array_cumu_wins = []
        for hand in hands:
            array_ordinals.append(int(hand['hand_index']))
            array_cumu_wins.append(int(hand['wins']))

        if rank_only:
            slopes = TrainingPlotter.do_poly_regression(array_cumu_wins,
                            array_ordinals, 
                            splines=3)
        else:                        
            slopes = TrainingPlotter.plot_regression(array_cumu_wins, 
                            array_ordinals, 'cumu - ' + st['name_scenario'], 
                            splines=3,
                            ylabel="cumulative wins   total=" + str(st['wins2']),
                            average_array=cumulative_averages)
        st['cumulative_wins_slopes'] = slopes
        st['cumulative_wins_last_spline_slope'] = slopes[-1]
        st['cumulative_wins_ratio'] = slopes[-1]/slopes[0]

    ## ##############################
    def rank_all_moving_averages(statsList):
        for st in statsList:
            TrainingPlotter._rank_or_plot_ma('rank', st) 
        
    def rank_moving_average(st):
        return TrainingPlotter._rank_or_plot_ma('rank', st) 

    def plot_moving_average(st):
        return TrainingPlotter._rank_or_plot_ma('plot', st) 

    def _rank_or_plot_ma(which, st):
        array_ma = []
        array_count = []
        ma = st['ma_array']
        for ma_val in ma:
            array_ma.append(ma_val)
            array_count.append(len(array_ma))
            
        if len(array_count)>0:
            if which == 'plot':
                slopes = TrainingPlotter.plot_regression(array_ma, array_count, 
                                st['name_scenario'], splines=[1,3],
                                ylabel="wins last {} hands".format(MA_SIZE))
            else:
                slopes = TrainingPlotter.do_poly_regression(array_ma, array_count, splines=[1,3])
            array_count = []
            array_ma = []
            st['moving_average_overall_slope'] = slopes[0]
            st['moving_average_spline_slopes'] = slopes[1:]
            st['moving_average_last_spline_slope'] = slopes[-1]

## ##############################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################

class TrainingPlotManager:
    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        self.statsList = statsList
        self.figures = []
        for st in statsList:
             self.figures.append(st['name_scenario'])
             self.figures.append('cumu - ' + st['name_scenario'])
        self.lastOpened = ""
        self.cumulative_averages = cumulative_averages

    def install_navigation(self, fig_label):
        button_height=0.075
        rrr = plt.get_figlabels()
        if not fig_label in plt.get_figlabels():
            print(f'wtf: fig_label={fig_label}')
        fig = plt.figure(fig_label)
        axx = fig.subplots_adjust(bottom=0.2, top=0.99, right=0.99)
        axprev = plt.axes([0.77, 0.01, 0.1, button_height])
        axnext = plt.axes([0.89, 0.01, 0.1, button_height])
        self.bnext = widgets.Button(axnext, 'Next')
        self.bnext.on_clicked(self.onclickn)
        self.bprev = widgets.Button(axprev, 'Previous')
        self.bprev.on_clicked(self.onclickp)

    ## ##############################
    def onclickp(self, event):
        self.onclick(event, 'p')
    def onclickn(self, event):
        self.onclick(event, 'n')
    def onclick(self, event, direction):
        # print(f"onclick: direction={direction} event={vars(event)}")
        figure_id = self.get_figure_id(event)
        #print(f'click: figure_id={figure_id}')
        if figure_id == None:
            return

        for i in range(len(self.figures)):
            fig_label = self.figures[i]
            if fig_label == figure_id:
                plt.close(figure_id)
                if direction == 'n':
                    fig_label = self.figures[(i+1)%len(self.figures)]
                else:
                    if i>0:
                        fig_label = self.figures[i-1]
                    else:
                        fig_label = self.figures[-1]
                self.activateFigure(fig_label)

    ## ##############################
    def activateFigure(self, fig_label:(str)):
        if 'cumu' in fig_label:
            TrainingPlotter.plot_cumulative_wins(self.find_stats(fig_label[7:]), self.cumulative_averages)
        else:
            TrainingPlotter.plot_moving_average(self.find_stats(fig_label))

        self.install_navigation(fig_label)
        self.lastOpened = fig_label

    ## ##############################
    def find_stats(self,scenario_string):
        for st in self.statsList:
            if scenario_string in st['name_scenario']:
                return st
        print(f"dang, cannot find these stats: {scenario_string}")
        return "dang!"

    ## ##############################
    def get_figure_id(self,event):
        return self.lastOpened
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

## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
class TrainingLogParser:
    DQN_PLAYER_NAME = "Tempo"
    statsList = []
    cumulative_averages = []
    score_stats = {}

    def save_training_session(self):
        self.stats['hands'] = self.hands
        if len(self.ma_array) == 0:
            # we never made it to the window
            # dummy something up to avoid problems
            for hand in self.hands:
                self.ma_array.append(1)
        self.stats['ma_array'] = self.ma_array
        self.statsList.append(self.stats)
        self.session_count += 1

    def init_training_session(self):
        self.stats = {}
        self.stats['name_scenario'] = self.filepath + '.validation_test.' + str(self.session_count)

        self.ma_array = []
        self.ma_count = 0
        self.ma_window = []
        for i in range(MA_SIZE):
            self.ma_window.append(0)   

        self.hands = []
        self.wins = 0

    def extract_param(self, key, params):
        if key in params:
            self.stats[key] = params[key]

    ## ##############################
    def is_session_start(line):
        return (("INPUT" in line) or ("Testing." in line) or ("Training." in line))

    ## ##############################
    def parse_params(self, line:(str)):
        params = eval(line[line.find('{'):])
        self.extract_param("name_scenario", params)
        self.extract_param("learning_rate", params)
        self.extract_param("epsilon_decay_linear", params)
        if "layer_sizes" in params:
            ls = params["layer_sizes"]
            self.stats["l1"] = int(ls[0])
            self.stats["l2"] = int(ls[1])
            self.stats["l3"] = int(ls[2])
        self.stats['params'] = params

    ## ##############################
    def processLine(self, line:(str), include_partials:(bool)=False):
        ma_name = TrainingLogParser.DQN_PLAYER_NAME

        if TrainingLogParser.is_session_start(line) and len(self.stats)>0:
            if 'wins2' in self.stats or include_partials:
                self.save_training_session()
            self.init_training_session()
        if "Training.." in line:
            self.stats['mode']='train'
            self.stats['name_scenario'] += '.' + self.stats['mode']
        if "Testing.." in line:
            self.stats['mode']='test'
            self.stats['name_scenario'] += '.' + self.stats['mode']
        if "{'episodes':" in line:
            self.parse_params(line)
        if "Winner: " in line:
            ## cumulative wins
            toks = line.split()
            hand_index = int(toks[1])
            winner = toks[3]
            if winner == TrainingLogParser.DQN_PLAYER_NAME:
                self.wins += 1
            self.hands.append({'hand_index': hand_index, 
                            'winner': winner, 
                            'wins': self.wins})
            ## moving average wins
            self.ma_count += 1
            name=line.split()[3]
            if ma_name in name:
                w = 1
            else:   
                w = 0
            self.ma_window[self.ma_count%MA_SIZE] = w
            if self.ma_count>MA_SIZE:
                # ma_array.append(float(sum(self.ma_window))/float(len(self.ma_window)))                            
                self.ma_array.append(sum(self.ma_window))                            
        if "winMap: " in line:
            cpos = line.find(",")
            x = cpos-1
            while not line[x] == ' ':
                x-=1        
            self.stats['wins1'] = int(line[x:cpos])
            cpos +=1
            cpos = line[cpos:].find(",")+cpos
            x = cpos-1
            while not line[x] == ' ':
                x-=1        
            self.stats['wins2'] = int(line[x:cpos])
            if len(self.hands)>0:
                self.stats['wins_per_1000_hands'] = self.stats['wins2']*1000/len(self.hands)
            else:
                self.stats['wins_per_1000_hands'] = -1

    ## ##############################
    def parseLogs(self, filepath:(str), include_partials:(bool)=False): 

        self.filepath = filepath
        self.session_count = 0
        self.init_training_session()

        with open(filepath, 'r') as f:
            lines=f.readlines()

        for line in lines:
            self.processLine(line)

        # last (or only) stats
        if 'wins2' in self.stats or include_partials:
            self.save_training_session()

        self.score_stats = self.create_score_stats

    ## ##############################
    def create_score_stats(self):
        score_stats={}
        count_scenarios = 0
        count_hands = 0
        tot1 = 0
        tot2 = 0
        totwpk = 0
        min1 = 100000
        min2 = 100000
        max1 = -1
        max2 = -1
        minr = 100000
        maxr = -1
        for st in self.statsList:
            if 'wins2' in st:
                count_scenarios+=1
                count_hands += len(st['hands'])
                w1 = st['wins1']
                w2 = st['wins2']
                tot1+= w1
                tot2+= w2
                totwpk += st['wins_per_1000_hands']
                max1=max(max1,w1)
                max2=max(max2,w2)
                min1=min(min1,w1)
                min2=min(min2,w2)
                if w2 > 0:
                    ratio = w1/w2
                else:
                    ratio = w1
                maxr = max(ratio, maxr)
                minr = min(ratio, minr)
                for hand in st['hands']:
                    ndx = int(hand['hand_index'])
                    cumu = int(hand['wins'])
                    if ndx>=len(self.cumulative_averages):
                        self.cumulative_averages.append(cumu)
                    else:
                        self.cumulative_averages[ndx] += cumu
        mean_losses = tot1/count_scenarios
        mean_wins = tot2/count_scenarios 
        for i in range(len(self.cumulative_averages)):
            self.cumulative_averages[i]/=count_scenarios             
        score_stats['mean_wins_per_1000_hands']=totwpk/count_scenarios
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
        for st in self.statsList:
            if 'wins2' in st:
                tot1 += (st['wins1']-mean_losses)**2
                tot2 += (st['wins2']-mean_wins)**2
        score_stats['std_losses']=math.sqrt(tot1/count_scenarios)
        score_stats['std_wins']=math.sqrt(tot2/count_scenarios)
        score_stats['cumulative_average_slope']=(
                        self.cumulative_averages[-1] - self.cumulative_averages[0]
                                        )/len(self.cumulative_averages)
                        
        return score_stats

    def print_stats(stats):
        for key in stats.keys():
            if not key == "hands":
                print(f"{key}={stats[key]}")

    def print_score_stats(score_stats):
        for key in score_stats.keys():
            print(f"{key}={score_stats[key]}")

    def print_statsList(statsList):
        for stats in statsList:
            TrainingLogParser.print_stats(stats)

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
class TrainingAnalyzer:
    def __init__(self):
        self.banana =1

    def get_first_figure(self,statsList):
        return statsList[0]['name_scenario']

    def create_PlotManager(self,statsList, cumulative_averages):
        return TrainingPlotManager(statsList, cumulative_averages)

    def create_LogParser(self):
        return TrainingLogParser()

    def analyze(self, path_to_logfile, include_partials:(bool)=False):
        logParser = self.create_LogParser()
        logParser.parseLogs(path_to_logfile, include_partials)

        print("* * * * * * * * * * * * * * * * * * * ")
        TrainingLogParser.print_score_stats(logParser.create_score_stats())
        print("* * * * * * * * * * * * * * * * * * * ")

        TrainingPlotter.rank_all_cumulative_wins(logParser.statsList)
        TrainingPlotter.rank_all_moving_averages(logParser.statsList)

        logParser.statsList.sort(key=lambda x: x['moving_average_last_spline_slope'])
        print("     -------- name_scenario ----------     \tma_last_slope  ma_full_slope\tcum_last_slope\tcum_ratio\twpk")
        for st in logParser.statsList:
            star = ""
            if not 'wins2' in st:
                star = "*"  # should only happen if "include_partials==True"
            print(f"{star}{st['name_scenario']}:"
                    f"\t{st['moving_average_last_spline_slope']: 1.7f}  "
                    f"\t{st['moving_average_overall_slope']: 1.7f}"
                    f"\t{st['cumulative_wins_last_spline_slope']:1.7f}"
                    f"\t{st['cumulative_wins_ratio']:1.7f}"
                    f"\t{st['wins_per_1000_hands']:1.7f}"
                    )
        print(f"{len(logParser.statsList)} scenarios")    

        try:

            plotManager = self.create_PlotManager(logParser.statsList, logParser.cumulative_averages)
            scenario = self.get_first_figure(logParser.statsList)
            plotManager.activateFigure(scenario)

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
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path_to_logfile',
                    default='logs/learning_lr00332519_struct100_800_20_eps0.0256.log.0',  #'logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results eve without bayesian end-tags')
    args = argparser.parse_args()

    TrainingAnalyzer().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

