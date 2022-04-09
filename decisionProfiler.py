from collections.abc import Iterable
import time
import distutils.util

import matplotlib.pyplot as plt

from trainingAnalyzer import TrainingPlotManager, TrainingLogParser, TrainingAnalyzer, TrainingPlotter
import regplot

## #############################################
class DecisionPlotter(TrainingPlotter):

    ## ##############################
    def get_decision_count(st):
        hands = st['hands']        
        decision_count = -1
        for hand in hands:
            if 'decisions' in hand and len(hand['decisions'])>0:
                decision_count = len(hands[0]['decisions'][0])
                break
        return  decision_count

    ## ##############################
    def plot_decision_histogram(st, fig_label):
        hands = st['hands']        
        array_bins = []

        decision_count = DecisionPlotter.get_decision_count(st)
        if decision_count == -1:
            print("plot_decision_histogram: no decisions")
            return

        target = 0
        for i in range(1,decision_count):
            if "iscard (" + str(i) +")" in fig_label:
                target = i
                break

        target_decisions = []
        for hand in hands:
            if 'decisions' in hand:
                hand_decisions = hand['decisions']
                for d in hand_decisions:
                    target_decisions.append(d[target])

        DecisionPlotter.plot_histogram(target_decisions, 
                        10, fig_label, 
                        ylabel="Decision count",
                        xlabel="decision {}".format(target))

    ## ##############################
    def get_zeroes_by_hand(st, fig_label):
        hands = st['hands']        
        array_zeroes = []
        array_ordinals = []
        array_winners = []
        array_wordinals = []
        array_losers = []
        array_lordinals = []

        decision_count = DecisionPlotter.get_decision_count(st)
        if decision_count == -1:
            print("plot_zeroes_by_hand: no decisions")
            return

        target = 0
        for i in range(1,decision_count):
            if "iscard " + str(i) +")" in fig_label:
                target = i
                break

        for hand in hands:
            if not (('decisions' in hand) 
                    and (len(hand['decisions'])>0)):
                continue
            count_zeroes = 0
            hand_decisions = hand['decisions']
            for d in hand_decisions:
                if d[target] == 0:
                    count_zeroes += 1
            array_zeroes.append(count_zeroes/len(hand_decisions))
            array_ordinals.append(hand['hand_index'])
            if hand['winner'] == TrainingLogParser.DQN_PLAYER_NAME:
                array_winners.append(count_zeroes/len(hand_decisions))
                array_wordinals.append(hand['hand_index'])
            elif not (hand['winner'] == 'nobody'):
                array_losers.append(count_zeroes/len(hand_decisions))
                array_lordinals.append(hand['hand_index'])

        return [array_zeroes,array_ordinals,
                array_winners, array_wordinals,
                array_losers, array_lordinals]

    ####################################
    def plot_zeroes_by_hand(st, fig_label):
        arrays = DecisionPlotter.get_zeroes_by_hand(st, fig_label)
        array_zeroes = arrays[0]
        array_ordinals = arrays[1]
        array_winners = arrays[2]
        array_wordinals = arrays[3]
        array_losers = arrays[4]
        array_lordinals = arrays[5]

        DecisionPlotter.plot_regression(array_zeroes, 
                        array_ordinals,
                        fig_label, 
                        ylabel="% zero in hand",
                        xlabel="hands")

        regplot.scatter(array_wordinals,
                        array_winners, 
                        color="#F8283D"
                        #ax=plt.gca(),
                        ) 

        regplot.scatter(array_lordinals,
                        array_losers, 
                        color="#08B83D"
                        #ax=plt.gca(),
                        ) 
        plt.draw()

## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################

class DecisionPlotManager(TrainingPlotManager):

    def __init__(self, statsList:(Iterable), cumulative_averages:(Iterable)):
        super().__init__(statsList, cumulative_averages)
        self.figures = []
        for st in statsList:
            ## fig_label = 'Decisions (draw source) - {}'.format(st['name_scenario'])
            fig_label = 'Zeroes by hand (draw source) - {}'.format(st['name_scenario'])
            self.figures.append(fig_label)
            for i in range(1,len(statsList[0]['hands'][0]['decisions'][0])):
                # self.figures.append(f"Decisions (discard {i}) - {st['name_scenario']}")
                self.figures.append(f"Zeroes by hand (discard {i}) - {st['name_scenario']}")

    def activateFigure(self, fig_label:(str)):
        if 'zeroes by hand' in fig_label.lower():
            name_scenario = fig_label[fig_label.index(' - ')+3:]
            stats = self.find_stats(name_scenario)
            DecisionPlotter.plot_zeroes_by_hand(stats, fig_label)            
            self.install_navigation(fig_label)
            self.lastOpened = fig_label
        elif 'ecisions' in fig_label:
            name_scenario = fig_label[fig_label.index(' - ')+3:]
            stats = self.find_stats(name_scenario)
            DecisionPlotter.plot_decision_histogram(stats, fig_label)            
            self.install_navigation(fig_label)
            self.lastOpened = fig_label
        else:
            super().activateFigure(fig_label)


## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
## ###################################################
class DecisionLogParser(TrainingLogParser):

    ## ##############################
    def __init__(self):
        super().__init__()
        self.decisions = []
        self.lines = 0
        self.start_time = time.time()
        self.count_decisions = 0

    ## ##############################
    def init_training_session(self):
        super().init_training_session()
        self.stats['name_scenario'] = self.filepath + '.decide.' + str(self.session_count)
        self.decisions = []

    ## ##############################
    def processLine(self, line:(str), include_partials:(bool)=False):
        self.lines += 1
        if self.lines%10000 == 0:
            print(f"parsed {self.lines} lines in {time.time()-self.start_time:3.3f}s")
        if ("  turn " == line[:7]) and ("[" in line):
            toks = line.split()
            turn_index = toks[1]
            name = toks[2]
            draw_card = toks[4]
            draw_source = toks[7][:-2]
            discard = toks[10][:-2]
            decisions = eval(line[line.index('['):line.index(']')+1])
            self.decisions.append(decisions)
        else:
            if ("Winner: " in line) and len(self.decisions)>0:
                self.hands[-1]['decisions'] = self.decisions
                self.decisions = []
            super().processLine(line, include_partials)

## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
class DecisionProfiler(TrainingAnalyzer):
    def __init__(self):
        super().__init__()

    def create_LogParser(self):
        return DecisionLogParser()

    def create_PlotManager(self,statsList, cumulative_averages):
        return DecisionPlotManager(statsList, cumulative_averages)

    def get_first_figure(self,statsList):
        # return 'Decisions (draw source) - {}'.format(statsList[0]['name_scenario'])
        return 'Zeroes by hand (draw source) - {}'.format(statsList[0]['name_scenario'])

    def analyze(self, path_to_logfile, include_partials:(bool)=False):
        logParser = self.create_LogParser()
        logParser.parseLogs(path_to_logfile, include_partials)

        print("* * * * * * * * * * * * * * * * * * * ")
        DecisionLogParser.print_score_stats(logParser.create_score_stats())
        print("* * * * * * * * * * * * * * * * * * * ")

        DecisionPlotter.rank_all_cumulative_wins(logParser.statsList)
        DecisionPlotter.rank_all_moving_averages(logParser.statsList)

        # logParser.statsList.sort(key=lambda x: x['moving_average_last_spline_slope'])
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
                    default='logs/bayesModel_reward-bayes_2022-04-08_214231', # 'logs/histo',  #'logs/mega2', 
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results eve without bayesian end-tags')
    args = argparser.parse_args()

    DecisionProfiler().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

