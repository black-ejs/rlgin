from collections.abc import Iterable
import sys
import math
import time
import re
import distutils.util

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from learningGin import NO_WIN_NAME

import regressionPlotter
import benchmarks
import gin

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
            array_cumu_wins.append(int(hand['wins'][0]))

        if rank_only:
            slopes = TrainingPlotter.do_poly_regression(array_cumu_wins,
                            array_ordinals, 
                            splines=3)
        else:       
            benchmark_player, benchmark_opponent = TrainingPlotter.get_benchmark_players(st)
            benchmark_arrays=benchmarks.get_cumulative_wins(benchmark_player,benchmark_opponent,len(hands))
            slopes = TrainingPlotter.plot_regression(array_cumu_wins, 
                            array_ordinals, 'cumu - ' + st['name_scenario'], 
                            splines=[1,3], #=3,
                            ylabel="cumulative wins   total=" + str(st['wins2']),
                            average_array=cumulative_averages,
                            benchmark_arrays=benchmark_arrays)
        st['cumulative_wins_slopes'] = slopes
        st['cumulative_wins_last_spline_slope'] = slopes[-1]
        st['cumulative_wins_ratio'] = slopes[-1]/slopes[1] # [0]

    ## ##############################
    def rank_all_moving_averages(statsList):
        for st in statsList:
            TrainingPlotter._rank_or_plot_ma('rank', st) 
        
    def rank_moving_average(st):
        return TrainingPlotter._rank_or_plot_ma('rank', st) 

    def plot_moving_average(st):
        return TrainingPlotter._rank_or_plot_ma('plot', st) 

    def _rank_or_plot_ma(which, st):
        nn_players = st['nn_players']
        if len(nn_players) == 0:
            return

        for nnp in nn_players.values():
            nnp_name = nnp['name']
            array_ma = []
            array_count = []
            ma = nnp['ma_array']
            for ma_val in ma:
                array_ma.append(ma_val)
                array_count.append(len(array_ma))
            
            if len(array_count)>0:
                if which == 'plot':
                    benchmark_player, benchmark_opponent = TrainingPlotter.get_benchmark_players(st)
                    benchmark_ma=benchmarks.get_moving_average(benchmark_player,benchmark_opponent,MA_SIZE)
                    benchmark_array=[]
                    for i in range(len(array_count)):
                        benchmark_array.append(benchmark_ma)
                    slopes = TrainingPlotter.plot_regression(array_ma, array_count, 
                                    st['name_scenario'], splines=[1,3],
                                    ylabel="wins last {} hands".format(MA_SIZE),
                                    benchmark_arrays=(benchmark_array,array_count))
                else:
                    slopes = TrainingPlotter.do_poly_regression(array_ma, array_count, splines=[1,3])
                array_count = []
                array_ma = []
                nnp['moving_average_overall_slope'] = slopes[0]
                nnp['moving_average_spline_slopes'] = slopes[1:]
                nnp['moving_average_last_spline_slope'] = slopes[-1]

    def get_benchmark_players(st:(dict)):
        benchmark_player = 'r'  #random
        if 'brandiac_random_percent' in st['params']:               
            benchmark_opponent = 'br' + str(st['params']['brandiac_random_percent'])
        else:
            benchmark_opponent = 'b'
        return (benchmark_player, benchmark_opponent)


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
        self.last_button = 0

    def install_navigation(self, fig_label):
        # prev_fig = plt.gcf()
        self.last_button = 0

        ppp = plt.get_figlabels()
        if not fig_label in plt.get_figlabels():
            print(f'wtf: fig_label={fig_label}')
        fig = plt.figure(fig_label)
        axx = fig.subplots_adjust(bottom=0.2, top=0.99, right=0.99,left=0.12)

        self.bnext = self.add_button('Next', self.onclickn)
        self.bprev = self.add_button('Previous', self.onclickp)
        self.bparams = self.add_button("params", self.onclickparams)

        # plt.figure(prev_fig)


    ## #######################################
    BUTTON_Y=0.01
    BUTTON_HEIGHT=0.075
    BUTTON_WIDTH=0.1
    BUTTON_X_SPACE=0.02
    BUTTON_X_INC=BUTTON_WIDTH+BUTTON_X_SPACE
    def add_button(self, label:(str)="?", onclick=None):
        # prev_fig = plt.gcf()
        ax = plt.axes([
                    1-((self.last_button+1)*TrainingPlotManager.BUTTON_X_INC), 
                    TrainingPlotManager.BUTTON_Y, 
                    TrainingPlotManager.BUTTON_WIDTH, 
                    TrainingPlotManager.BUTTON_WIDTH])
        button = widgets.Button(ax, label)
        if not onclick==None:
            button.on_clicked(onclick)
        self.last_button += 1
        # plt.figure(prev_fig)
        return button

    ## ##############################
    PARAMS_FIG_ID = "parameters"
    PARAMS_FIG_W = 7
    PARAMS_FIG_H = 5.7
    def onclickparams(self, event):
        if not self.params_window_is_open():
            figure_id = self.get_figure_id(event)
            if figure_id == None:
                return
            st = self.find_stats(figure_id)
            if not st == None:
                self.show_params(st)

    ## ##############################
    def show_params(self,st):
        if not 'params' in st:
            print(f"no params available for scenario {st['name_scenario']}")
            return
        fig = plt.figure(TrainingPlotManager.PARAMS_FIG_ID, 
                    figsize=(TrainingPlotManager.PARAMS_FIG_W,TrainingPlotManager.PARAMS_FIG_H))
        
        params = st['params']
        s = ""
        for key in params.keys():
            s += f"{key}: {params[key]}\n"
        s += f"   ---   ---   ---\n"
        for key in st.keys():
            if key in ['hands', 'params', "ma_array"] or key in params:
                continue
            s += f"{key}: {st[key]}\n"

        fig.text(0.01, 0.01, s,
                backgroundcolor='#FFFFAA',
                fontsize=8)

        plt.show()            
        self.jdjdj = 943049
        return

    ## ##############################
    def params_window_is_open(self):
        return TrainingPlotManager.PARAMS_FIG_ID in plt.get_figlabels()

    ## ##############################
    def onclickp(self, event):
        self.onclick(event, 'p')
    def onclickn(self, event):
        self.onclick(event, 'n')
    def onclick(self, event, direction):
        # print(f"onclick: direction={direction} event={vars(event)}")
        figure_id = self.get_figure_id(event)
        # print(f'click: figure_id={figure_id}')
        if figure_id == None:
            return

        for i in range(len(self.figures)):
            fig_label = self.figures[i]
            if fig_label == figure_id:
                # print(f'click: i={i}, direction={direction}, fig_label={fig_label}')  #########
                self.deactivateFigure(figure_id)
                if direction == 'n':
                    fig_label = self.figures[(i+1)%len(self.figures)]
                else:
                    if i>0:
                        fig_label = self.figures[i-1]
                    else:
                        fig_label = self.figures[-1]
                self.activateFigure(fig_label)
                break

    ## ##############################
    def deactivateFigure(self, fig_label:(str)):
        # print(f"deactivating figure {fig_label}")
        plt.close(fig_label)
        if self.params_window_is_open():
            plt.close(TrainingPlotManager.PARAMS_FIG_ID)
        
    ## ##############################
    def activateFigure(self, fig_label:(str)):
        # print(f"trainingAnalyszer: activating figure {fig_label}")
        if 'cumu' in fig_label:
            TrainingPlotter.plot_cumulative_wins(self.find_stats(fig_label[7:]), self.cumulative_averages)
        else:
            TrainingPlotter.plot_moving_average(self.find_stats(fig_label))

        self.lastOpened = fig_label
        self.install_navigation(fig_label)
        # self.install_view_support()

    ## ##############################
    def find_stats(self,scenario_string):
        chop = scenario_string.find(" - ")
        if not chop == -1:
            scenario_string = scenario_string[chop+3:]
        for st in self.statsList:
            # if scenario_string in st['name_scenario']:
            if scenario_string == st['name_scenario']:
                return st
        print(f"dang, cannot find these stats: {scenario_string}")
        return None

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
    def __init__(self):

        self.scenario_players = {}
        self.nn_players = {}
        self.statsList = []
        self.cumulative_averages = []
        self.score_stats = {}

    def get_default_name_scenario(self):
        return self.filepath + '.learning_' + str(self.session_count)

    def save_training_session(self):
        self.stats['hands'] = self.hands
        self.stats['scenario_players'] = self.scenario_players
        self.stats['nn_players'] = self.nn_players
        ma_arrays = {}
        for p in self.nn_players.values():
            if len(p['ma_array']) == 0:
                # we never made it to the window
                # dummy something up to avoid problems
                for hand in self.hands:
                    p['ma_array'].append(1)
            ma_arrays[p['name']] = p['ma_array']
        self.stats['ma_arrays'] = ma_arrays
        if len(self.stats['name_scenario']) == 0: # some kind of error in the input
            self.stats['name_scenario'] = "unknown"
        i=1
        root = self.stats['name_scenario']
        dupe = True
        while dupe:
            dupe = False
            for st in self.statsList:
                if self.stats['name_scenario'] == st['name_scenario']:
                    self.stats['name_scenario'] = root + f"_{i}"
                    i+=1
                    dupe=True
                    break

        self.extract_generation()

        self.statsList.append(self.stats)
        self.session_count += 1

    def init_training_session(self):
        #self.scenario_players = {}
        #self.nn_players = {}
        self.hands = []

        self.stats = {}
        self.stats['name_scenario'] = self.get_default_name_scenario()
        self.ma_count = 0
        # self.stats['generation'] = 0

    ## ##############################
    def extract_generation(self):
        generation_match = re.search("[.][0-9]*[.]", self.stats['name_scenario'])
        if generation_match:
            self.stats['generation'] = int(
                self.stats['name_scenario'][generation_match.start()+1:generation_match.end()-1]
                )
        else:
            generation_match = re.search("[.][0-9]*[.]", self.stats['params']['log_path'])
            if generation_match:
                self.stats['generation'] = int(
                    self.stats['params']['log_path'][generation_match.start()+1:generation_match.end()-1]
                    )
        if ('generation' in self.stats) and (self.stats['generation'] > 999):  # old, pre-convention name
            print(f"generation={self.stats['generation']}   name_scenario={self.stats['name_scenario']}    log_path={self.stats['params']['log_path']}")
            self.stats.pop('generation')

    ## ##############################
    def extract_param(self, key, params):
        if key in params:
            self.stats[key] = params[key]

    ## ##############################
    def is_session_start(line):
        return (("INPUT" in line) or ("learningGin execution at" in line) or ("Testing." in line))

    ## ##############################
    def parse_player_params(self, params):
        player_params = []
        for pid in (1,2):
            key = 'player' + str(pid)
            if key in params:
                pparams = params[key]
                pparams['pid'] = pid
                pparams['params_key'] = key
                player_params.append(pparams)

        if len(self.scenario_players) == 0:
            for pparams in player_params:
                if pparams['name'] in self.scenario_players:
                    print(f" ** WARNING: duplicate player name '{pparams['name']}'")
                else:
                    self.scenario_players[pparams['name']] = pparams
                self.scenario_players[pparams['name']]['wins'] = 0

        if len(self.nn_players) == 0:
            for pparams in self.scenario_players.values():
                if 'nn' in pparams:
                    dqn_params = pparams['nn']
                    for ppk in pparams.keys():
                        if ppk != 'nn':
                            dqn_params[ppk] = pparams[ppk]
                    if "layer_sizes" in dqn_params:
                        ls = dqn_params["layer_sizes"]
                        for lndx in range(len(ls)):
                            key = 'l' + str(lndx+1)
                            dqn_params[key] = int(ls[lndx])
                    dqn_params['total_reward'] = 0
                    dqn_params['ma_array'] = []
                    dqn_params['ma_window'] = []
                    for i in range(MA_SIZE):
                        dqn_params['ma_window'].append(0)   
                    self.nn_players[pparams['name']] = dqn_params

    ## ##############################
    def parse_params(self, line:(str)):
        params = eval(line[line.find('{'):])

        self.parse_player_params(params)

        self.extract_param('name_scenario', params)
        self.extract_param('timestamp', params)
        self.stats['params'] = params

    ## ##############################
    def parse_win_line(self, line):
            ## end of hand
            toks = line.split()
            hand_index = int(toks[1])
            winner = toks[3]
            tok_pad = 0
            if not winner == NO_WIN_NAME:
                self.scenario_players[winner]['wins'] += 1
                tok_pad = gin.HAND_SIZE+1  # Hand: + cards
            if (len(toks)>9+tok_pad):
                ginscore1_owner = toks[9+tok_pad]
                ginscore1 = toks[10+tok_pad]
            else:
                ginscore1 = 0
            if (len(toks)>11+tok_pad):
                ginscore2_owner = toks[11+tok_pad]
                ginscore2 = toks[12+tok_pad]
            else:
                ginscore2 = 0
            total_reward1_owner = ""
            if (len(toks)>14+tok_pad):
                total_reward1_owner = toks[14+tok_pad]
                total_reward1   = toks[15+tok_pad]
            total_reward2_owner = ""
            if (len(toks)>16+tok_pad):
                total_reward2_owner = toks[16+tok_pad]
                total_reward2   = toks[17+tok_pad]
            tot_rew = []
            if len(total_reward1_owner)>0:
                tot_rew.append((total_reward1_owner,total_reward1))
            if len(total_reward2_owner)>0:
                tot_rew.append((total_reward2_owner,total_reward2))
            if not winner == NO_WIN_NAME:
                self.scenario_players[winner]['wins'] += 1
            hand_summary = {'hand_index': hand_index, 
                            'winner': winner, 
                            'ginscores': (ginscore1, ginscore2),
                            'total_reward': tot_rew,
                            'wins': (self.scenario_players[ginscore1_owner]['wins'],
                                     self.scenario_players[ginscore2_owner]['wins'])
                            }
            self.hands.append(hand_summary) 
                            
            ## moving average wins
            self.ma_count += 1
            for p in self.nn_players.values():
                if p['name'] == winner:
                    w = 1
                else:   
                    w = 0
                p['ma_window'][self.ma_count%MA_SIZE] = w
            if self.ma_count>MA_SIZE:
                p['ma_array'].append(sum(p['ma_window']))                            

    ## ##############################
    def processLine(self, line:(str), include_partials:(bool)=False):
        
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
            ## end of hand
            self.parse_win_line(line)
        if "total_reward: " == line[:14]:
            self.stats['total_reward'] = float(line[14:])
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
                for p in self.nn_players.values():
                    p['wins_per_1000_hands'] = self.scenario_players[p['name']]['wins']*1000/len(self.hands)
                self.stats['wins_per_1000_hands_1'] = self.stats['wins1']*1000/len(self.hands)
                self.stats['wins_per_1000_hands_2'] = self.stats['wins2']*1000/len(self.hands)
            else:
                self.stats['wins_per_1000_hands_1'] = -1
                self.stats['wins_per_1000_hands_2'] = -1

    ## ##############################
    def parseLogs(self, filepath:(str), include_partials:(bool)=False): 

        start_time = time.time()
        self.filepath = filepath
        self.session_count = 0
        self.init_training_session()

        with open(filepath, 'r') as f:
            count_lines = 0
            for line in f:
                self.processLine(line)
                count_lines += 1
                if count_lines%10000 == 0:
                    sys.stdout.write(f"\rparsed {count_lines} lines in {time.time()-start_time:3.3f}s")
            sys.stdout.write("\n")
        
        # last (or only) stats
        if 'wins2' in self.stats or include_partials:
            self.save_training_session()

        self.score_stats = self.create_score_stats()

    ## ##############################
    def create_score_stats(self):
        score_stats={}
        count_scenarios = 0
        count_hands = 0
        tot1 = 0
        tot2 = 0
        totwpk1 = 0
        totwpk2 = 0
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
                totwpk1 += st['wins_per_1000_hands_1']
                totwpk2 += st['wins_per_1000_hands_2']
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

                self.capture_cumulative_averages(st)

        score_stats['count_scenarios']=count_scenarios
        if count_scenarios == 0:
            return score_stats
        mean_wins_1 = tot1/count_scenarios
        mean_wins_2 = tot2/count_scenarios 
        for i in range(len(self.cumulative_averages)):
            cumu_nn = self.cumulative_averages[i]
            for j in range(len(cumu_nn)):
                cumu_nn[j] /= count_scenarios             
        score_stats['mean_wins_per_1000_hands_1']=totwpk1/count_scenarios
        score_stats['mean_wins_per_1000_hands_2']=totwpk2/count_scenarios
        score_stats['mean_wins_1']=mean_wins_1
        score_stats['mean_wins_2']=mean_wins_2
        score_stats['max_wins_1']=max1
        score_stats['max_wins_2']=max2
        score_stats['min_wins_1']=min1
        score_stats['min_wins_2']=min2
        score_stats['max_ratio']=maxr
        score_stats['min_ratio']=minr
        score_stats['count_hands']=count_hands
        for st in self.statsList:
            if 'wins2' in st:
                tot1 += (st['wins1']-mean_wins_1)**2
                tot2 += (st['wins2']-mean_wins_2)**2
        score_stats['std_wins_1']=math.sqrt(tot1/count_scenarios)
        score_stats['cv_wins_1']=math.sqrt(tot1/count_scenarios)/mean_wins_1
        score_stats['std_wins_2']=math.sqrt(tot2/count_scenarios)
        score_stats['cv_wins_2']=math.sqrt(tot2/count_scenarios)/mean_wins_2
        for ca in self.cumulative_averages:
            for i in range(len(ca)):
                cumu_nn = ca[i]
                key = 'cumulative_average_slope_' + str(i+1)
                score_stats[key]=(
                        self.cumulative_averages[-1][i] - self.cumulative_averages[0][i]
                                        )/len(self.cumulative_averages)
        return score_stats

    def capture_cumulative_averages(self,st):
        player1_name = st['params']['player1']['name']
        player2_name = st['params']['player2']['name']
        for hand in st['hands']:
            cumu_nn_dict = {}
            for nnp in self.nn_players:
                cumu_nn_dict[nnp] = 0
            ndx = int(hand['hand_index'])
            if hand['winner'] in cumu_nn_dict:
                cumu_nn_dict[hand['winner']]+=1
            
            cumu_nn = []
            if len(cumu_nn_dict) > 1:
                cumu_nn = [cumu_nn_dict[player1_name],cumu_nn_dict[player2_name]]
            else: 
                cumu_nn = cumu_nn_dict.values()

            if len(cumu_nn) > 0:    
                target = ndx - 1                
                if target>=len(self.cumulative_averages):
                    self.cumulative_averages.append(cumu_nn.copy())
                else:
                    # self.cumulative_averages[ndx] += cumu_nn
                    for i in range(len(self.cumulative_averages[target])):
                        self.cumulative_averages[target][i] += cumu_nn[i]
                    

    def format_stats(stats):
        rez=""
        for key in stats.keys():
            if not key == "hands":
                rez+= f"{key}={stats[key]}\n"
        return rez

    def format_score_stats(score_stats):
        rez=""
        for key in score_stats.keys():
            rez += f"{key}={score_stats[key]}\n"
        return rez

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

    def get_scenario_sort_key(self):
        # return 'moving_average_last_spline_slope'
        return 'timestamp'
        # return 'generation'

    def display_scenarios(self,statsList):
        maxlen = -100000
        for st in statsList:
            maxlen = max(maxlen,len(st['name_scenario']))
        name_title = " name_scenario "
        while len(name_title) < maxlen-2:
            name_title = "-" + name_title + "-"
        print(f"{name_title}\ttotal_reward\tma_last_slope  ma_full_slope\tcum_last_slope\tcum_ratio\twpk\tgen")
        for st in statsList:
            star = ""
            if not 'wins2' in st:
                star = "*"  # should only happen if "include_partials==True"
            if 'generation' in st:
                gen=st['generation']
            else:
                gen='-'
            print(f"{star}{st['name_scenario']}:"
            """
                    f"\t{st['total_reward']: 2.4f}  "
                    f"\t{st['moving_average_last_spline_slope']: 1.7f}  "
                    f"\t{st['moving_average_overall_slope']: 1.7f}"
                    f"\t{st['cumulative_wins_last_spline_slope']:1.7f}"
                    f"\t{st['cumulative_wins_ratio']:1.3f}"
                    f"\t{st['wins_per_1000_hands']:2.3f}"
                    f"\t{gen}"
                    """
                    )
        print(f"{len(statsList)} scenarios sorted by {self.get_scenario_sort_key()}")    

    ## ##############################
    def analyze(self, path_to_logfile, include_partials:(bool)=False):
        logParser = self.create_LogParser()
        logParser.parseLogs(path_to_logfile, include_partials)

        print("* * * * * * * * * * * * * * * * * * * ")
        print(TrainingLogParser.format_score_stats(logParser.score_stats))
        if logParser.score_stats['count_scenarios'] == 0:
            print(f"No scenarios to analyze, found {len(logParser.statsList)} stats")
            print("* * * * * * * * * * * * * * * * * * * ")
            return
        print("* * * * * * * * * * * * * * * * * * * ")

        TrainingPlotter.rank_all_cumulative_wins(logParser.statsList)
        TrainingPlotter.rank_all_moving_averages(logParser.statsList)

        sortkey = self.get_scenario_sort_key()
        logParser.statsList.sort(key=lambda x: x[sortkey])
        self.display_scenarios(logParser.statsList)

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
                    default='logs/dueling.scratch.log',  #'logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results even without bayesian end-tags')
    args = argparser.parse_args()

    print(f"analyzing {args.path_to_logfile}")
    TrainingAnalyzer().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

