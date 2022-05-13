from collections.abc import Iterable
import distutils.util

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

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
        array_no_winners = []
        array_nordinals = []
        array_winners = []
        array_wordinals = []
        array_losers = []
        array_lordinals = []
        array_epsilon = []
        noise_epsilon = float(st['params']['noise_epsilon'])
        if st['params']['train']:
            epsilon_decay = float(st['params']['epsilon_decay_linear'])

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

            if not st['params']['train']:
                array_epsilon.append(noise_epsilon)
            else:
                array_epsilon.append(max(1-(hand['hand_index']*epsilon_decay), noise_epsilon))

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
            else:
                array_no_winners.append(count_zeroes/len(hand_decisions))
                array_nordinals.append(hand['hand_index'])

        return [array_zeroes,array_ordinals,
                array_winners, array_wordinals,
                array_losers, array_lordinals,
                array_no_winners, array_nordinals,
                array_epsilon]

    ####################################
    def plot_zeroes_by_hand(st, fig_label, 
                win_filters:(list)=[True, True, True], 
                crop_epsilon:(bool)=True):
        arrays = DecisionPlotter.get_zeroes_by_hand(st, fig_label)
        array_zeroes = arrays[0]
        array_ordinals = arrays[1]
        array_winners = arrays[2]
        array_wordinals = arrays[3]
        array_losers = arrays[4]
        array_lordinals = arrays[5]
        array_no_winners = arrays[6]
        array_nordinals = arrays[7]
        array_epsilon = arrays[8]

        start_index = 0
        start_pos = 0

        show_wins      = win_filters[0]
        show_losses    = win_filters[1]
        show_no_winner = win_filters[2]

        if crop_epsilon:
            for i in range(len(array_epsilon)):
                if array_epsilon[i] == float(st['params']['noise_epsilon']):
                    start_pos=i
                    start_index = array_ordinals[i]
                    break
    
        if show_no_winner:
            plot_y = array_zeroes[start_pos:]
            plot_x = array_ordinals[start_pos:]
        else:
            plot_y = []
            plot_x = []
            if show_losses:
                for i in range(len(array_lordinals)):
                    if array_lordinals[i]>=start_index:
                        start_pos=i
                        break
                plot_y.extend(array_losers[start_pos:])
                plot_x.extend(array_lordinals[start_pos:])
            if show_wins:
                for i in range(len(array_wordinals)):
                    if array_wordinals[i]>=start_index:
                        start_pos=i
                        break
                plot_y.extend(array_winners[start_pos:])
                plot_x.extend(array_wordinals[start_pos:])

        DecisionPlotter.plot_regression(plot_y, 
                    plot_x,
                    fig_label, 
                    splines=[1,3],
                    scatter=False,
                    ylabel=f"% zero in hand",
                    xlabel="hands")

        if show_no_winner:
            start_pos = 0
            for i in range(len(array_nordinals)):
                if array_nordinals[i]>=start_index:
                    start_pos=i
                    break
            regplot.scatter(array_nordinals[start_pos:],                                                       
                            array_no_winners[start_pos:], 
                            color="#36688D",
                            #ax=plt.gca(),
                            ) 

        if show_losses:
            start_pos = 0
            for i in range(len(array_lordinals)):
                if array_lordinals[i]>=start_index:
                    start_pos=i
                    break
            regplot.scatter(array_lordinals[start_pos:],                                                       
                            array_losers[start_pos:], 
                            color="#F8283D",
                            #ax=plt.gca(),
                            ) 

        if show_wins:
            start_pos = 0
            for i in range(len(array_wordinals)):
                if array_wordinals[i]>=start_index:
                    start_pos=i
                    break
            regplot.scatter(array_wordinals[start_pos:],
                            array_winners[start_pos:], 
                            color="#08B83D",
                            #ax=plt.gca(),
                            ) 

        if not crop_epsilon:
            plt.gca().plot(array_ordinals,
                            array_epsilon, 
                            label='epsilon', 
                            linestyle='dotted', color="black")

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
        self.win_filters = [True, True, True, True]
        for st in statsList:
            name_scenario=st['name_scenario']
            nl = len(name_scenario)
            ## fig_label = 'Decisions (draw source) - {}'.format(st['name_scenario'])
            fig_label = 'Zeroes by hand (draw source) - {}'.format(name_scenario)
            i=0
            insert_point = len(self.figures)
            for f in self.figures:
                if (len(f)>=nl) and (f[-nl:]==name_scenario):
                    insert_point=i
                    break
                i+=1
            self.figures.insert(insert_point, fig_label)

    def activateFigure(self, fig_label:(str)):
        # print(f"decisionProfiler: activating figure {fig_label}")
        if 'zeroes by hand' in fig_label.lower():
            name_scenario = fig_label[fig_label.index(' - ')+3:]
            stats = self.find_stats(name_scenario)
            DecisionPlotter.plot_zeroes_by_hand(stats, fig_label, self.win_filters, crop_epsilon=self.win_filters[3])            
            self.lastOpened = fig_label
            self.install_navigation(fig_label)
            rax = plt.axes([0.01, 0.01, 0.14, 0.12])
            self.win_filter_checkbuttonsa = widgets.CheckButtons(
                                                rax,
                                                ["wins", "losses"],
                                                actives=self.win_filters[0:2])
            rax = plt.axes([0.18, 0.01, 0.14, 0.12])
            self.win_filter_checkbuttonsb = widgets.CheckButtons(
                                                rax,
                                                ["no winner", "crop epsilon"],
                                                actives=self.win_filters[2:4])
            self.win_filter_checkbuttonsa.on_clicked(self.on_checkclick)
            self.win_filter_checkbuttonsb.on_clicked(self.on_checkclick)
        elif 'ecisions' in fig_label:
            name_scenario = fig_label[fig_label.index(' - ')+3:]
            stats = self.find_stats(name_scenario)
            DecisionPlotter.plot_decision_histogram(stats, fig_label)            
            self.lastOpened = fig_label
            self.install_navigation(fig_label)
        else:
            return super().activateFigure(fig_label)


    def deactivateFigure(self, figure_id):
        self.win_filter_checkbuttonsa = None
        self.win_filter_checkbuttonsb = None
        super().deactivateFigure(figure_id)

    ## #############################################
    def on_checkclick(self, event):
        figure_id = self.get_figure_id(event)
        status = []
        status.extend(self.win_filter_checkbuttonsa.get_status())
        status.extend(self.win_filter_checkbuttonsb.get_status())
        if not status == self.win_filters:
            self.win_filters=status
            self.deactivateFigure(figure_id)
            self.activateFigure(figure_id)

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
        self.count_decisions = 0

    ## ##############################
    def get_default_name_scenario(self):
        return self.filepath + '.decide_' + str(self.session_count)

    ## ##############################
    def init_training_session(self):
        super().init_training_session()
        self.decisions = []

    ## ##############################
    def processLine(self, line:(str), include_partials:(bool)=False):
        if ("  turn " == line[:7]) and ("[" in line):
            toks = line.split()
            turn_index = toks[1]
            name = toks[2]
            draw_card = toks[4]
            draw_source = toks[7][:-2]
            discard = toks[10][:-2]
            #decisions = eval(line[line.index('['):line.index(']')+1])
            decisions = line[line.index('[')+1:line.index(']')].split(",")
            for i in range(len(decisions)):
                decisions[i] = float(decisions[i])
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

## ##############################
## ##############################
## ##############################
## ##############################
import argparse

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path_to_logfile',
                    default='logs/convo.megalog', # 'logs/erw',  
                    nargs='?', help='path to the logfile to be plotted')
    argparser.add_argument('include_partials',
                    default='False', 
                    nargs='?', help='include results eve without bayesian end-tags')
    args = argparser.parse_args()

    DecisionProfiler().analyze(args.path_to_logfile, 
                        distutils.util.strtobool(args.include_partials))



            

