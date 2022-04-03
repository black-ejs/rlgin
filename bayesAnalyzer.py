from collections.abc import Iterable
import distutils.util

from trainingAnalyzer import TrainingPlotter, TrainingPlotManager, TrainingAnalyzer

MA_SIZE = 50
DQN_PLAYER_NAME = "Tempo"

## #############################################
class BayesPlotter(TrainingPlotter):
    def plot_rl_param(statsList, param_name):
        array_score = []
        array_param = []
        for st in statsList:
            if param_name in st and 'moving_average_spline_slopes' in st:
                slopes = st['moving_average_spline_slopes']
                array_param.append(st[param_name])
                ## array_score.append(st['wins2'])
                array_score.append(slopes[-1])
        
        if len(array_param)>0:
            BayesPlotter.plot_regression(array_score, array_param, param_name, splines=1,
                    ylabel="slope - moving average of wins, last {} hands".format(MA_SIZE))

## #############################################
class BayesPlotManager(TrainingPlotManager):
    rl_param_names = ["l1","l2","l3","learning_rate", "epsilon_decay_linear"]

    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        super().__init__(statsList, cumulative_averages)
        for st in statsList:
            for param_name in BayesPlotManager.rl_param_names:
                self.figures.append(param_name)
            break

    def activateFigure(self, fig_label:(str)):
        if not fig_label in self.rl_param_names:
            return super().activateFigure(fig_label)
        else:
            BayesPlotter.plot_rl_param(self.statsList, fig_label)            
            self.install_navigation(fig_label)
            self.lastOpened = fig_label

## ##############################
class BayesAnalyzer(TrainingAnalyzer):
    def get_first_figure(self, statsList):
        return "l1"

    def create_PlotManager(self,statsList, cumulative_averages):
        return BayesPlotManager(statsList, cumulative_averages)

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



            

