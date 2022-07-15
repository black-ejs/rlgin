from collections.abc import Iterable
import copy
from re import I

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from matplotlib.gridspec import GridSpec

from learningGin import NO_WIN_NAME

import regressionPlotter
import benchmarks

MA_SIZE = 200

## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
class Plottable:
    def __init__(self,plot,st,nn_key:(str)):
        self.plot = plot
        self.st = st
        self.nn_key = nn_key
        self.nn_player = st['nn_players'][nn_key]
        self.pid = self.nn_player['pid']
        self.fig_label =   (f"{self.plot}"
                          + f"-bo{st['st_id']}" 
                          + f"-{self.nn_key}"
                          + f"-{self.nn_player['strategy']}"
                          + f"_{self.nn_player['mode']}"
                          + f"_{self.st['scenario_players'][self.nn_key]['wins']}w"
                            )

    def get(self, key:(str)):
        for dic in (self.nn_player, 
                    self.st['scenario_players'][self.nn_key],
                    self.st,
                    self.st['params']):
            if key in dic:
                return dic[key]
        return self.nn_player[key]  # force KeyError

    def has_key(self, key:(str)):
        for dic in (self.nn_player, 
                    self.st['scenario_players'][self.nn_key],
                    self.st):
            if key in dic:
                return True
        return False  

    def __lt__(self, other):
        mywins = self.st['scenario_players'][self.nn_key]['wins'] 
        otherwins = other.st['scenario_players'][other.nn_key]['wins']
        if mywins < otherwins:
            return False
        if mywins > otherwins:
            return True
        if self.st['st_id'] > other.st['st_id']:
            return False
        if self.st['st_id'] < other.st['st_id']:
            return True
        if self.nn_key > other.nn_key:
            return False
        if self.nn_key < other.nn_key:
            return True
        if self.nn_player['mode'] > other.nn_player['mode']: 
            return True # want "train" before "test"
        if self.nn_player['mode'] < other.nn_player['mode']: 
            return False # want "train" before "test"
        return self.plot < other.plot

## #############################################
class LearningPlotter(regressionPlotter.RegressionPlotter):

    def rank_all_cumulative_wins(statsList):
        for st in statsList:
            LearningPlotter.plot_cumulative_wins(st, rank_only=True)

    def plot_cumulative_wins(st, cumulative_averages:(Iterable)=None,
                            rank_only:(bool)=False,
                            plottable:(Plottable)=None):
        hands = st['hands']
        if not plottable==None:
            plot_key = plottable.nn_key
            plot_title = plottable.fig_label
        else:
            plot_key = list(st['nn_players'].keys())[0]
            plot_title = 'cumu - ' + st['name_scenario']
        for nnp in st['nn_players'].values():
            win_index = int(nnp['pid'])-1
            array_ordinals = []
            array_cumu_wins = []
            for hand in hands:
                array_ordinals.append(int(hand['hand_index']))
                array_cumu_wins.append(int(hand['wins'][win_index]))

            if rank_only or nnp['name']!=plot_key:
                slopes = LearningPlotter.do_poly_regression(array_cumu_wins,
                                array_ordinals, 
                                splines=3)
            else:       
                benchmark_player, benchmark_opponent = LearningPlotter.get_benchmark_players(st)
                benchmark_arrays=benchmarks.get_cumulative_wins(benchmark_player,benchmark_opponent,len(hands))
                slopes = LearningPlotter.plot_regression(array_cumu_wins, 
                                array_ordinals, plot_title, 
                                splines=[1,3], #=3,
                                ylabel=f"{nnp['name']}: cumulative wins (total={array_cumu_wins[-1]})",
                                average_array=cumulative_averages,
                                benchmark_arrays=benchmark_arrays)
            nnp['cumulative_wins_slopes'] = slopes
            nnp['cumulative_wins_last_spline_slope'] = slopes[-1]
            nnp['cumulative_wins_ratio'] = slopes[-1]/slopes[1] # [0]

    ## ##############################
    def rank_all_moving_averages(statsList):
        for st in statsList:
            LearningPlotter._rank_or_plot_ma('rank', st) 
        
    def rank_moving_average(st):
        return LearningPlotter._rank_or_plot_ma('rank', st) 

    def plot_moving_average(st, plottable=None):
        return LearningPlotter._rank_or_plot_ma('plot', st, plottable=plottable) 

    def _rank_or_plot_ma(which, st, plottable:(Plottable)=None):
        nn_players = st['nn_players']
        if len(nn_players) == 0:
            return

        if plottable==None:
            target_name = list(st['nn_players'].keys())[0]
            fig_label = st['name_scenario']
        else:
            target_name = plottable.nn_player['name']
            fig_label = plottable.fig_label

        for nnp in nn_players.values():
            nnp_name = nnp['name']
            array_ma = []
            array_count = []
            ma = nnp['ma_array']
            for ma_val in ma:
                array_ma.append(ma_val)
                array_count.append(len(array_ma))
            
            if len(array_count)>0:
                if which == 'plot' and nnp_name==target_name:
                    benchmark_player, benchmark_opponent = LearningPlotter.get_benchmark_players(st)
                    benchmark_ma=benchmarks.get_moving_average(benchmark_player,benchmark_opponent,MA_SIZE)
                    benchmark_array=[]
                    for i in range(len(array_count)):
                        benchmark_array.append(benchmark_ma)
                    slopes = LearningPlotter.plot_regression(array_ma, array_count, 
                                    fig_label, splines=[1,3],
                                    ylabel="wins last {} hands".format(MA_SIZE),
                                    benchmark_arrays=(benchmark_array,array_count))
                else:
                    slopes = LearningPlotter.do_poly_regression(array_ma, array_count, splines=[1,3])
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

class LearningPlotManager:
    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        self.statsList = statsList

        self.lastOpened = None
        self.cumulative_averages = cumulative_averages
        self.last_button = 0

        self.plottables = []
        for st in statsList:
            for nn_key in st['nn_players']:
                for plot in ("cumu", "ma"):
                    plottable = Plottable(plot, st, nn_key)
                    self.plottables.append(plottable)
        self.plottables.sort()
        self.plottables_window = None

    ## ##############################
    def onclickp(self, event):
        self.onclick_next_prev(event, 'p')
    def onclickn(self, event):
        self.onclick_next_prev(event, 'n')
    def onclick_next_prev(self, event, direction):

        #print(f"onclick: direction={direction} event={vars(event)}")
        plottable = self.get_plottable(event)
        figure_id = plottable.fig_label
        # print(f'click: figure_id={figure_id}')
        if figure_id == None:
            return

        for i in range(len(self.plottables)):
            p = self.plottables[i]
            if p.fig_label == figure_id:
                # print(f'click: i={i}, direction={direction}, fig_label={fig_label}')  #########
                self.deactivatePlottable(p)
                if direction == 'n':
                    target_plottable = self.plottables[(i+1)%len(self.plottables)]
                else:
                    if i>0:
                        target_plottable = self.plottables[i-1]
                    else:
                        target_plottable = self.plottables[-1]
                self.activatePlottable(target_plottable)
                break

    ## ##############################
    def onclickparams(self, event):
        if not self.params_window_is_open():
            plottable = self.get_plottable(event)
            if plottable == None:
                return
            self.show_params(plottable)
        self.update_plottables_window()

    ## ##############################
    def activatePlottable(self, plottable:(Plottable)):
        # print(f"trainingAnalyszer: activating figure {fig_label}")
        if 'cumu' == plottable.plot:
            LearningPlotter.plot_cumulative_wins(plottable.st, self.cumulative_averages, plottable=plottable)
        elif 'ma' == plottable.plot:
            LearningPlotter.plot_moving_average(plottable.st, plottable=plottable)

        if plottable.fig_label in plt.get_figlabels():
            self.lastOpened = plottable
            self.install_plottable_navigation(plottable)
            # self.install_view_support()
            if self.plottables_window_is_open():
                self.update_plottables_window()
            return plottable
        else:
            print(f"problem activating plottable with fig_label='{plottable.fig_label}'")

    ## ##############################
    def deactivatePlottable(self, plottable:(Plottable)):
        # print(f"deactivating figure {fig_label}")
        plt.close(plottable.fig_label)
        if self.params_window_is_open():
            plt.close(LearningPlotManager.PARAMS_FIG_ID)

    ## ##############################
    def get_plottable(self,event):
        return self.lastOpened

    ## ##############################
    PLOTTABLE_LIST_FIG_ID = "plottables"
    PLOTTABLE_LIST_FIG_W = 4
    PLOTTABLE_LIST_FIG_H = 7
    PLOTTABLE_LIST_ENTRIES = 20
    def show_plottables_window(self):
        
        if self.plottables_window_is_open():
            self.update_plottables_window()
            return
        elif not (self.plottables_window == None):
            plt.figure(self.plottables_window.label)
            return
        else:
            self.plottables_window = plt.figure(LearningPlotManager.PLOTTABLE_LIST_FIG_ID, 
                                    figsize=(LearningPlotManager.PLOTTABLE_LIST_FIG_W,
                                    LearningPlotManager.PLOTTABLE_LIST_FIG_H),
                                    constrained_layout=True)

        gs = GridSpec(10,10, figure=self.plottables_window)        

        # plottables list
        self.plottables_window_list_ax = self.plottables_window.add_subplot(gs[0:-1,0:9])
        self.plottables_window_list_ax.set_axis_off()
        self.plottables_window_list_ax.set_frame_on(True)

        # buttons
        self.plottables_window_nav_ax = self.plottables_window.add_subplot(gs[-1,0:])
        self.plottables_window_nav_ax.set_axis_off()
        self.plottables_window_nav_ax.set_frame_on(False)
        self.last_button = 0
        self.bnext = self.add_button('Next', self.onclickn, ax=self.plottables_window_nav_ax)
        self.bprev = self.add_button('Prev', self.onclickp, ax=self.plottables_window_nav_ax)

        # scrollbar
        if len(self.plottables) > LearningPlotManager.PLOTTABLE_LIST_ENTRIES:
            self.plottables_window_scroll_ax = self.plottables_window.add_subplot(gs[0:-1,-1:])
            self.scroller = widgets.Slider(self.plottables_window_scroll_ax,
                                            "",
                                            0,
                                            len(self.plottables)-LearningPlotManager.PLOTTABLE_LIST_ENTRIES,
                                            valinit=len(self.plottables),
                                            orientation="vertical",
                                            valstep=1.0)
            self.scroller.valtext.set_visible(False)                                        
            self.scroller.on_changed(self.on_scroll_change)

        # self.plottables_window.subplots_adjust(top=0.98, bottom=0.02, left=0.02, right=0.98, wspace=0.03, hspace=0.03)
        self.scroll_plottables_list(0)
        ## plt.show()            
        return

    ## ##############################
    def onclick_radio_bogus(self,event):
        # print(f"onclick_radio_bogus(): event={event}")
        if (not (event.xdata==None)):
            target = None
            i=0
            for t in self.radio_buttons.labels:
                contains_event, contains_info = t.contains(event)
                if contains_event:
                    target = i
                #print(f"self.radio_buttons.labels[{i}].get_position()={t.get_position()}")
                i+=1
            if not (target==None):
                # print(f"hit in target {target}, text is {self.radio_buttons.labels[target].get_text()}")
                self.onclick_radio(self.radio_buttons.labels[target].get_text())
                return

            contains_event, contains_info = self.bprev.ax.contains(event)
            if contains_event:
                self.onclickp(event)
                return

            contains_event, contains_info = self.bnext.ax.contains(event)
            if contains_event:
                self.onclickn(event)
                return

    ## ##############################
    def onclick_radio(self,event):
        # print(f"onclick_radio(): event={event}, self.radio_buttons.active={self.radio_buttons.active}")
        if self.radio_buttons.ignore(event):
            print(f"onclick_radio(): ignoring this event: {event}")
            return
        selected_button_text = event
        if selected_button_text == self.lastOpened.fig_label:
            return
        for p in self.plottables:
            if p.fig_label == selected_button_text:
                self.deactivatePlottable(self.lastOpened)
                self.activatePlottable(p)
                break
            
    ## ##############################
    def on_scroll_change(self,event):
        # print(f"on_scroll_change(): event={event}")
        pos=int(event)
        pos=self.scroller.valmax-pos;
        self.scroll_plottables_list(pos)

    ## ##############################
    def scroll_plottables_list(self,pos):
        if pos>len(self.plottables)-LearningPlotManager.PLOTTABLE_LIST_ENTRIES:
            pos = len(self.plottables)-LearningPlotManager.PLOTTABLE_LIST_ENTRIES
        pos=0 if pos<0 else pos

        fig_labels = []
        for p in self.plottables[pos:]:
            fig_labels.append(p.fig_label)
            if len(fig_labels)==LearningPlotManager.PLOTTABLE_LIST_ENTRIES:
                break

        self.plottables_window_list_ax.clear()
        self.radio_buttons = widgets.RadioButtons(self.plottables_window_list_ax,fig_labels)
        # self.radio_buttons.on_clicked(self.onclick_radio)
        self.bogus_connect = self.radio_buttons.connect_event('button_press_event',self.onclick_radio_bogus)
        for lbl in self.radio_buttons.labels:
            lbl.set_fontsize(8)
            lbl.set_color('white')
        #iii=0
        #for dd in self.radio_buttons.circles:
        #    radius = dd.get_radius()
        #    print(f"self.radio_buttons.circles[{iii}] radius={radius}")
        #    iii +=1
        #    dd.set(radius=max(radius, 0.004))
        self.update_plottables_window()

    ## ##############################
    def update_plottables_window(self):
        if not (self.plottables_window == None):
            for i in range(len(self.radio_buttons.labels)):
                lbl = self.radio_buttons.labels[i]
                lbl.set_backgroundcolor("#0077FF")
                if (self.lastOpened in self.plottables) and (
                            lbl.get_text() == self.lastOpened.fig_label): 
                    # active = self.plottables.index(self.lastOpened)
                    self.radio_buttons.set_active(i)
                    lbl.set_backgroundcolor("#0000FF")
            fig = plt.figure(LearningPlotManager.PLOTTABLE_LIST_FIG_ID)
            plt.draw()
            
    ## ##############################
    def install_plottable_navigation(self, plottable:Plottable):
        self.last_button = 0

        if not plottable.fig_label in plt.get_figlabels():
            print(f'wtf: fig_label={plottable.fig_label}')
        fig = plt.figure(plottable.fig_label)
        axx = fig.subplots_adjust(bottom=0.2, top=0.99, right=0.99,left=0.12)

        self.bparams = self.add_button("params", self.onclickparams)

    ## ##############################
    def plottables_window_is_open(self):
        return LearningPlotManager.PLOTTABLE_LIST_FIG_ID in plt.get_figlabels()

    ## ##############################
    PARAMS_FIG_ID = "parameters"
    PARAMS_FIG_W = 9
    PARAMS_FIG_H = 7
    PARAMS_LINE_LENGTH = 120
    PARAMS_LINE_MAX = 200

    ## ##############################
    def show_params(self, plottable:Plottable):
        st = plottable.st
        if not 'params' in st:
            print(f"no params available for scenario {st['name_scenario']}")
            return
        fig = plt.figure(LearningPlotManager.PARAMS_FIG_ID, 
                    figsize=(LearningPlotManager.PARAMS_FIG_W,LearningPlotManager.PARAMS_FIG_H))
        
        params = st['params']
        scenario_players = st['scenario_players']
        for player in scenario_players.values():
            if player['pid'] == plottable.pid:
                my_player_str = self.chunk_player(player, params)
            else:
                opponent_str = self.chunk_player(player, params)
            
        s = "--- my player ---\n" + my_player_str
        self.params_axL = fig.add_subplot(1,3,1)
        fig.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99)
        self.params_axL.set_axis_off()
        self.params_axL.set_frame_on(True)
        self.params_axL.text(0.01, 0.01, s,
                backgroundcolor='#FFFF88',
                fontsize=8)

        s = ""
        for key in params.keys():
            if key in ('hands', 'ma_array', 'ma_arrays', 'ma_window', 'nn_players', 'nn-common', 'player2', 'player1'):
                continue
            p = f"{key}: {params[key]}\n"
            s = self.chunk_string(s, p)

        for key in st.keys():
            if key in ['hands', 'params', "ma_array", "ma_arrays", "ma_window", 'nn_players', 'nn_common', 'scenario_players'] or key in params:
                continue
            p = f"{key}: {st[key]}\n"
            s = self.chunk_string(s, p)

        self.params_axM = fig.add_subplot(1,3,2)
        fig.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99)
        self.params_axM.set_axis_off()
        self.params_axM.set_frame_on(True)
        self.params_axM.text(0.01, 0.01, s,
                backgroundcolor='#FFFF88',
                fontsize=8)

        s = "--- opponent ---\n" + opponent_str

        self.params_axR = fig.add_subplot(1,3,3)
        fig.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99)
        self.params_axR.set_axis_off()
        self.params_axR.set_frame_on(True)
        self.params_axR.text(0.01, 0.01, s,
                backgroundcolor='#FFFF88',
                fontsize=8)
        #plt.text(0.01, 0.01, s,
            #backgroundcolor='#FFFFAA',
            #fontsize=8)

        #plt.show()            
        plt.draw()            
        return

    ## ##############################
    def chunk_player(self, player, params):
        s = ""
        pp=""
        nn=""
        for kkk in player.keys():
            if kkk in ['hands', 'params', "ma_array", "ma_arrays", "ma_window", 'nn_players', 'nn-common'] or kkk in params:
                continue
            if kkk == 'nn':
                nnn = player[kkk]
                for lll in nnn.keys():
                    if lll in ['hands', 'params', "ma_array", "ma_arrays", "ma_window", 'nn_players', 'nn-common'] or lll in params:
                        continue
                    nn += f"{lll}: {nnn[lll]}\n"
            else:
                pp += f"{kkk}: {player[kkk]}\n"
        s = self.chunk_string(s, pp)
        s += f"   ---   ---   ---\n"
        s = self.chunk_string(s, nn)
        return s

    ## ##############################
    # avoid matplotlib bug with wrapping long text
    def chunk_string(self, s, p):
        split = ", "
        while len(p)>LearningPlotManager.PARAMS_LINE_MAX:
            ndx=LearningPlotManager.PARAMS_LINE_LENGTH
            chunk = p[:ndx]
            while not split in chunk:
                ndx+=1
                chunk = p[:ndx]
            chunk = chunk[:chunk.rindex(split)+2]
            s += chunk + "\n"
            p = p[len(chunk):]
        if len(p) > 0:
            s += p
        return s
        
    ## ##############################
    def params_window_is_open(self):
        return LearningPlotManager.PARAMS_FIG_ID in plt.get_figlabels()

    ## ##############################
    BUTTON_Y=0.01
    BUTTON_HEIGHT=0.075
    BUTTON_WIDTH=0.1
    BUTTON_X_SPACE=0.02
    BUTTON_X_INC=BUTTON_WIDTH+BUTTON_X_SPACE
    def add_button(self, label:(str)="?", onclick=None, ax:(plt.Axes)=None):
        # prev_fig = plt.gcf()

        if (ax==None):
            button_ax = plt.axes([
                        1-((self.last_button+1)*LearningPlotManager.BUTTON_X_INC), 
                        LearningPlotManager.BUTTON_Y, 
                        LearningPlotManager.BUTTON_WIDTH, 
                        LearningPlotManager.BUTTON_HEIGHT])
        else:
            button_ax = ax.inset_axes([
                        1-((self.last_button+1)*LearningPlotManager.BUTTON_X_INC), 
                        LearningPlotManager.BUTTON_Y, 
                        LearningPlotManager.BUTTON_WIDTH, 
                        0.9])
        button = widgets.Button(button_ax, label)
        if not onclick==None:
            button.on_clicked(onclick)
        self.last_button += 1
        # plt.figure(prev_fig)
        return button


## ###################################################
## ###################################################
## ###################################################
