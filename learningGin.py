import datetime
import sys
import time
import argparse
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statistics
import torch.optim as optim
import torch 
from GPyOpt.methods import BayesianOptimization
#from bayesOpt import *
import distutils.util
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import playGin
import ginDQN
import ginDQNParameters
NO_WIN_NAME = 'nobody'

## #############################################
## #############################################
class Stats:
    def __init__(self):
        self.stats = {}    

    def put(self, key, value):
        self.stats[key]=value

    def get(self, key):
        if self.stats.has_key(key):
            return self.stats[key]
        return "unknown statistic"

## #############################################
def display(counter_hands, hand_duration, ginhand):
    winner = ginhand.winner
    if not winner == None:
        print(f'Game {counter_hands}    Winner: {winner.player}    Hand: {winner.playerHand}    Time: {hand_duration*1000:3.2f}')
    else:
        print(f'Game {counter_hands}    Winner: Nobody    Time: {hand_duration*1000:3.2f}')

## #############################################
def plot_seaborn(array_counter, array_score, train):
    sns.set(color_codes=True, font_scale=1.5)
    sns.set_style("white")
    plt.figure(figsize=(13,8))
    fit_reg = False if train== False else True        
    ax = sns.regplot(
        np.array([array_counter])[0],
        np.array([array_score])[0],
        #color="#36688D",
        x_jitter=.1,
        scatter_kws={"color": "#36688D"},
        label='Data',
        fit_reg = fit_reg,
        line_kws={"color": "#F49F05"}
    )
    # Plot the average line
    y_mean = [np.mean(array_score)]*len(array_counter)
    ax.plot(array_counter,y_mean, label='Mean', linestyle='--')
    ax.legend(loc='upper right')
    ax.set(xlabel='# games', ylabel='score')
    plt.show()

## #############################################
def get_mean_stdev(array):
    return statistics.mean(array), statistics.stdev(array)    

## #############################################
def test(params):
    params['load_weights'] = True
    params['train'] = False
    params["test"] = False 
    return run(params)

## #############################################
def initalizeDQN(params):
    params['input_size'] = 52 # size of state, length of list of numpys 
    params['output_size'] = 1 # size of desired response, length of list of numpys 
    agent = ginDQN.ginDQNAgent(params)
    agent = agent.to(DEVICE)
    agent.optimizer = optim.Adam(agent.parameters(), 
                            weight_decay=0, lr=params['learning_rate'])
    return agent

## #############################################
def print_stats(stats, file=sys.stdout):
    for key, value in stats.stats.items():
        print(f"{key}: {value}", file=file)

## #############################################
def run(params):
    """
    Use the DQN to play gin, via a ginDQNStrategy            
    """
    agent = initalizeDQN(params)

    counter_hands = 0
    score_plot = []
    counter_plot = []

    winMap = {}
    winMap[params['player_one_name']] = 0				
    winMap[params['player_two_name']] = 0				
    winMap[NO_WIN_NAME] = 0				

    stats = Stats()
    stats.put("run_timestamp", eval('f"{datetime.datetime.now()}"'))
    stats.put("params", params)
    stats.put("winMap", winMap)

    durations = []
    turns_in_hand = []

    startTime = time.time()
    while counter_hands < params['episodes']:
        ## TODO: check for abort
        
        # agent.epsilon is set to give randomness to actions
        # during training, it starts high and reduces a bit each hand
        # noise eplsilon is the basic level that remains even when not treaining
        if not params['train']:
            agent.epsilon = float(params['noise_epsilon'])
        else:
            agent.epsilon = max(1 - (counter_hands * params['epsilon_decay_linear']),
                                float(params['noise_epsilon']),)

        # create GinHand, re-using the agent each time
        ginhand = gin.GinHand(gin.Player(params['player_one_name']),playGin.RandomGinStrategy(),
                    gin.Player(params['player_two_name']),ginDQN.ginDQNStrategy(params,agent))

        ginhand.deal()
        
        hand_startTime = time.time()
        winner = ginhand.play(params['max_steps_per_hand'])
        counter_hands += 1
        if params['train']:
            agent.replay_new(agent.memory, params['batch_size'])
        hand_duration = time.time() - hand_startTime

        durations.append(hand_duration)
        turns_in_hand.append(len(ginhand.turns))
        if not winner == None:
            winMap[winner.player.name] = winMap[winner.player.name]+1
        else:
            winMap[NO_WIN_NAME] = winMap[NO_WIN_NAME]+1

        if params['display']:
            display(counter_hands, hand_duration, ginhand)

        # score_plot.append(game.score)
        # counter_plot.append(counter_games)

    total_duration = time.time() - startTime
    
    if params['train']:
        model_weights = agent.state_dict()
        torch.save(model_weights, params["weights_path"])

    mean_durations, stdev_durations = get_mean_stdev(durations)
    mean_turns, stdev_turns = get_mean_stdev(turns_in_hand)
    ## if params['plot_score']:
    ##    plot_seaborn(counter_plot, score_plot, params['train'])

    stats.put("count_hands", counter_hands)
    stats.put("total duration", total_duration)
    stats.put("winMap", winMap)
    stats.put("mean_turns", mean_turns)
    stats.put("stdev_turns", stdev_turns)
    stats.put("mean_durations", mean_durations)
    stats.put("stdev_durations", stdev_durations)

    return stats

## #############################################
if __name__ == '__main__':
    # Set options to activate or deactivate the game view, and its speed
    parser = argparse.ArgumentParser()
    params = ginDQNParameters.define_parameters()
    parser.add_argument("--display", nargs='?', type=distutils.util.strtobool, default=True)
    parser.add_argument("--speed", nargs='?', type=int, default=50)
    parser.add_argument("--bayesianopt", nargs='?', type=distutils.util.strtobool, default=False)
    parser.add_argument("--learning_rate", nargs='?', type=float, default=0.0)
    args = parser.parse_args()
    print("Args", args)
    params['display'] = args.display
    params['speed'] = args.speed
    #if args.bayesianopt:
    #    bayesOpt = BayesianOptimizer(params)
    #    bayesOpt.optimize_RL()
    if params['train']:
        print("Training...")
        params['load_weights'] = False   # when training, the network is not pre-trained
        stats = run(params)
        print_stats(stats)
    if params['test']:
        print("Testing...")
        params['train'] = False
        params['load_weights'] = True
        stats = run(params)
        print_stats(stats)
