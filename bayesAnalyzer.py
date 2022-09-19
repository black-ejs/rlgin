from collections.abc import Iterable
import random
import distutils.util
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

from learningPlotter import Plottable
from decisionProfiler import DecisionPlotter, DecisionPlotManager, DecisionProfiler

## #############################################
class BayesPlotter(DecisionPlotter):    
    def plot_bayes_param(statsList, param_name, 
                        y_param_name:(str)='wins_per_1000_hands', # 'moving_average_spline_slopes',
                        ylabel:(str)="wins per 1000 hands", # "slope - moving average of wins, last {} hands".format(LearningPlotter.MA_SIZE),
                        splines=1, order=1):
        strat_map = {'nn-linear':0, 'nn-convf':1, 'nn-convb':2, 'nn-linearb':3 }
        array_score = []
        array_param = []
        for st in statsList:
            param_val = None
            if param_name in st:
                param_val = st[param_name]
            elif 'params' in st and param_name in st['params']:
                param_val = st['params'][param_name]
            if (not (param_val==None)) and (y_param_name in st):
                y_param = st[y_param_name]
                array_param.append(param_val)
                if isinstance(y_param,Iterable):
                    array_score.append(y_param[-1])
                else:
                    array_score.append(y_param)
            elif 'nn_players' in st:
                for nnp in st['nn_players'].values():
                    if 'use_cheat_rewards' in nnp and nnp['use_cheat_rewards']:
                        continue
                    if (param_name in nnp) and (y_param_name in nnp):
                        y_param = nnp[y_param_name]            
                        if param_name == 'strategy':
                            param_val = strat_map[nnp[param_name]]
                            if splines>1:
                                splines = 2
                        else:
                            param_val = nnp[param_name]
                        array_param.append(param_val)
                        if isinstance(y_param,Iterable):
                            array_score.append(y_param[-1])
                        else:
                            array_score.append(y_param)
        
        bayes_slopes = []
        if len(array_param)>0:
            average_array = BayesPlotter.create_average_array(array_param, array_score)
            bayes_slopes = BayesPlotter.plot_regression(array_score, 
                                        array_param, 
                                        "bayes - " + param_name, 
                                        splines=splines,
                                        order=order,
                                        average_array = average_array,
                                        ylabel=ylabel)
        return bayes_slopes

    def create_average_array(array_param, array_score):
        counts = {}
        totals = {}
        ndx = 0
        for p in array_param:
            if p in counts:
                counts[p] += 1
                totals[p] += array_score[ndx]
            else:
                counts[p] = 1
                totals[p] = array_score[ndx]
            ndx += 1

        if len(totals) > 10:
            return None

        averages_score = []
        for t in counts:
            averages_score.append(totals[t]/counts[t])
        
        return averages_score

## #############################################
class BayesPlotManager(DecisionPlotManager):

    def get_bayes_param_names(self):
        dqn_params_o = ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]
        dqn_params_x = ["l1","l2","l3","l4","learning_rate", "epsilon_decay_linear",
                        "strategy", "no_relu"]
        dqn_params = ["strategy", "gamma", "generation"] # lb-br-a, etc. 
        dqn_params_b = ["strategy", "gamma"] # bStra
        reward_params = ["win_reward","no_winner_reward","loss_reward"]
        generation_params = ["generation"]
        candidates = dqn_params
        rez = []
        for candidate in candidates:
            for p in self.plottables:
                for source in (p.st, p.st['params'], p.nn_player):
                    if candidate in source:
                        rez.append(candidate)
                        break
                if candidate in rez:
                    break

        return rez

    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        super().__init__(statsList, cumulative_averages)
        self.regression_mods = [False, False]
        # get dummy values from some Plottable for our "bayes" plots
        dummy = self.plottables[0]
        bayes_plottables = []
        for param_name in self.get_bayes_param_names():
            plottable = Plottable('bayes', dummy.st, dummy.nn_key)
            plottable.bayesian_param_name = param_name
            plottable.fig_label = "bayes - " + param_name
            bayes_plottables.append(plottable)
        self.plottables = bayes_plottables + self.plottables

    def activatePlottable(self, plottable:(Plottable)):
        if plottable.plot == 'bayes':
            param_name = plottable.bayesian_param_name
            slopes = BayesPlotter.plot_bayes_param(self.statsList, param_name, 
                                    splines=(3 if self.regression_mods[0] else 1),
                                    order=(3 if self.regression_mods[1] else 1))            
            print(f"bayes slopes for param {param_name}: {slopes}")
            rax = plt.axes([0.01, 0.01, 0.07, 0.15])
            self.regression_checkbuttons = widgets.CheckButtons(rax,
                                                ["splines", "cubic"],
                                                actives=self.regression_mods)
            self.regression_checkbuttons.on_clicked(self.on_checkclick)
        return super().activatePlottable(plottable)

    def deactivatePlottable(self, plottable):
        self.regression_checkbuttons = None
        super().deactivatePlottable(plottable)

    def on_checkclick(self, event):
        plottable = self.get_plottable(event)
        if self.regression_checkbuttons == None:
            return super().on_checkclick(event)
        else:
            status = self.regression_checkbuttons.get_status()
            if not status == self.regression_mods:
                self.regression_mods=status
                self.deactivatePlottable(plottable)
                self.activatePlottable(plottable)

## ##############################
class BayesAnalyzer(DecisionProfiler):
    def __init__(self):
        self.first_figure = "bayes - l1"

    #def get_first_figure(self, statsList):
    #    return self.first_figure

    def create_PlotManager(self,statsList, cumulative_averages):
        plotManager = BayesPlotManager(statsList, cumulative_averages)
        self.first_figure = plotManager.get_bayes_param_names()[0]
        return plotManager

## ##############################
import argparse
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path_to_logfile',
                    # default='logs/oneBayes.log',  #'logs/bayesDqn-junea.megalog', 
                    default='logs/megatrain.azz',  #'logs/bayesDqn-junea.megalog', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results eve without bayesian end-tags')
    args = argparser.parse_args()

    BayesAnalyzer().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

