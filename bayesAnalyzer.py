from collections.abc import Iterable
import distutils.util
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

from decisionProfiler import DecisionPlotter, DecisionPlotManager, DecisionProfiler

MA_SIZE = 50
DQN_PLAYER_NAME = "Tempo"

## #############################################
class BayesPlotter(DecisionPlotter):
    def plot_bayes_param(statsList, param_name, splines=1, order=1):
        array_score = []
        array_param = []
        for st in statsList:
            param_val = None
            if param_name in st:
                param_val = st[param_name]
            elif 'params' in st and param_name in st['params']:
                param_val = st['params'][param_name]
            if (not (param_val==None)) and ('moving_average_spline_slopes' in st):
                slopes = st['moving_average_spline_slopes']
                array_param.append(param_val)
                ## array_score.append(st['wins2'])
                array_score.append(slopes[-1])
        
        if len(array_param)>0:
            BayesPlotter.plot_regression(array_score, 
                                        array_param, 
                                        param_name, 
                                        splines=splines,
                                        order=order,
                            ylabel="slope - moving average of wins, last {} hands".format(MA_SIZE))

## #############################################
class BayesPlotManager(DecisionPlotManager):

    def get_bayes_param_names(self):
        dqn_params = ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]
        reward_params = ["win_reward","no_winner_reward","loss_reward"]
        rez = dqn_params
        v = []
        for st in self.statsList:
            val = st['params'][reward_params[0]]
            if len(v) > 0 and (val not in v):
                rez = reward_params
                break
            v.append(val)
        return rez

    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        super().__init__(statsList, cumulative_averages)
        self.regression_mods = [False, False]
        for st in statsList:
            for param_name in self.get_bayes_param_names():
                self.figures.append(param_name)
            break

    def activateFigure(self, fig_label:(str)):
        if not fig_label in self.get_bayes_param_names():
            return super().activateFigure(fig_label)
        else:
            BayesPlotter.plot_bayes_param(self.statsList, fig_label, 
                                    splines=(3 if self.regression_mods[0] else 1),
                                    order=(3 if self.regression_mods[1] else 1))            
            self.install_navigation(fig_label)
            rax = plt.axes([0.01, 0.01, 0.07, 0.15])
            self.regression_checkbuttons = widgets.CheckButtons(
                                                rax,
                                                ["splines", "cubic"],
                                                actives=self.regression_mods)
            self.regression_checkbuttons.on_clicked(self.on_checkclick)
            self.lastOpened = fig_label

    def deactivateFigure(self, figure_id):
        self.regression_checkbuttons = None
        super().deactivateFigure(figure_id)

    def on_checkclick(self, event):
        figure_id = self.get_figure_id(event)
        if self.regression_checkbuttons == None:
            return super().on_checkclick(event)
        else:
            status = self.regression_checkbuttons.get_status()
            if not status == self.regression_mods:
                self.regression_mods=status
                self.deactivateFigure(figure_id)
                self.activateFigure(figure_id)

## ##############################
class BayesAnalyzer(DecisionProfiler):
    def __init__(self):
        self.first_figure = "l1"

    def get_first_figure(self, statsList):
        return self.first_figure

    def create_PlotManager(self,statsList, cumulative_averages):
        plotManager = BayesPlotManager(statsList, cumulative_averages)
        self.first_figure = plotManager.get_bayes_param_names()[0]
        return plotManager

## ##############################
import argparse
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path_to_logfile',
                    default='logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results eve without bayesian end-tags')
    args = argparser.parse_args()

    BayesAnalyzer().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

