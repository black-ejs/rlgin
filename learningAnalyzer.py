import time
import distutils.util

import matplotlib.pyplot as plt
from learningGin import NO_WIN_NAME
from learningLogParser import LearningLogParser
from learningPlotter import LearningPlotManager, LearningPlotter

MA_SIZE = 50

## #############################################
## #############################################
## #############################################
## ##############################
class LearningAnalyzer:
    def __init__(self):
        self.banana =1

    def get_first_figure(self,statsList):
        return statsList[0]['name_scenario']

    def create_PlotManager(self,statsList, cumulative_averages):
        return LearningPlotManager(statsList, cumulative_averages)

    def create_LogParser(self):
        return LearningLogParser()

    def get_scenario_sort_key(self):
        # return 'moving_average_last_spline_slope'
        return 'timestamp'
        # return 'generation'

    def display_scenarios(self,statsList):
        """
        maxlen = -100000
        for st in statsList:
            maxlen = max(maxlen,len(st['name_scenarioz']))
        name_title = " name_scenario "
        while len(name_title) < maxlen-2:
            name_title = "-" + name_title + "-"
        """
        print(f"total_reward\twpk\tma_last_slope  ma_full_slope\tcum_last_slope\tcum_ratio\tgen")

        for st in statsList:
            star = ""
            if not 'wins2' in st:
                star = "*"  # should only happen if "include_partials==True"
            if 'generation' in st:
                gen=st['generation']
            else:
                gen='-'
            print(f"{star}{st['name_scenario']}:")
            for p in st['scenario_players']:
                pparams = st['scenario_players'][p]
                if pparams['name'] in st['nn_players']:
                    nnparams = st['nn_players'][pparams['name']]
                else:
                    nnparams = None
                print(f"'{pparams['name']}': {pparams['strategy']}")
                if not nnparams == None:
                    print(f"{nnparams['total_reward']: 2.4f}  "
                            f"\t{nnparams['wins_per_1000_hands']:2.3f}"
                            f"\t{nnparams['moving_average_last_spline_slope']: 1.7f}  "
                            f"\t{nnparams['moving_average_overall_slope']: 1.7f}"
                            f"\t{nnparams['cumulative_wins_last_spline_slope']:1.7f}"
                            f"\t{nnparams['cumulative_wins_ratio']:1.3f}"
                            f"\t{gen}"
                    )
        print(f"{len(statsList)} scenarios sorted by {self.get_scenario_sort_key()}")    

    ## ##############################
    def analyze(self, path_to_logfile, include_partials:(bool)=False):
        logParser = self.create_LogParser()
        logParser.parseLogs(path_to_logfile, include_partials)

        print("* * * * * * * * * * * * * * * * * * * ")
        print(LearningLogParser.format_score_stats(logParser.score_stats))
        if logParser.score_stats['count_scenarios'] == 0:
            print(f"No scenarios to analyze, found {len(logParser.statsList)} stats")
            print("* * * * * * * * * * * * * * * * * * * ")
            return
        print("* * * * * * * * * * * * * * * * * * * ")

        LearningPlotter.rank_all_cumulative_wins(logParser.statsList)
        LearningPlotter.rank_all_moving_averages(logParser.statsList)

        sortkey = self.get_scenario_sort_key()
        logParser.statsList.sort(key=lambda x: x[sortkey])
        self.display_scenarios(logParser.statsList)

        try:

            plotManager = self.create_PlotManager(logParser.statsList, logParser.cumulative_average)
            scenario = self.get_first_figure(logParser.statsList)


            gstart = time.time()
            plottable = plotManager.activatePlottable(plotManager.plottables[0])
            if not plottable == plotManager.plottables[0]:
                print(f"** WARNING ** at startup, activatePlottable(<{plotManager.plottables[0]}>) did not return the proper plottable")
            plotManager.show_plottables_window()

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
                    default='logs/bayesDqn-june.2.log', #'logs/dueling.scratch.log',  #'logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results even without bayesian end-tags')
    args = argparser.parse_args()

    print(f"analyzing {args.path_to_logfile}")
    LearningAnalyzer().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

