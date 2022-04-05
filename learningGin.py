import datetime
import sys
import contextlib
import time
import argparse
import numpy as np
import statistics
import torch.optim as optim
import torch 
import distutils.util
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
from playGin import BrandiacGinStrategy
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
        if key in self.stats:
            return self.stats[key]
        return "unknown statistic"

## #############################################
def display(counter_hands, hand_duration, ginhand, log_decisions):
    winner = ginhand.winner
    if not winner == None:
        print(f'Game {counter_hands}    Winner: {winner.player}    Hand: {winner.playerHand.prettyStr()}    Turns: {len(ginhand.turns)}    Time: {hand_duration*1000:3.2f}')
    else:
        print(f'Game {counter_hands}    Winner: {NO_WIN_NAME}    Turns: {len(ginhand.turns)}    Time: {hand_duration*1000:3.2f}')

    if log_decisions:
        i=0
        for t in ginhand.turns:
            if hasattr(t, 'turn_scores'):
                print(f"  turn {i} {t} > {t.turn_scores}")
            i+=1

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
def print_stats(stats, file=None):
    if file == None:
        file = sys.stdout
    for key, value in stats.stats.items():
        print(f"{key}: {value}", file=file)

## #############################################
def compare_weights(pretrain_weights, posttrain_weights):
    count_diffs = 0
    for p in pretrain_weights:
        try:
            pre = pretrain_weights[p]
            post = posttrain_weights[p]
            if not (torch.equal(pre, post)):
                count_diffs += 1
                print(f"unequal -- {p}:  (pre) {pre}")
                print(f"{p}: (post) {post}")
        except RuntimeError as err:
            print(f"error processing element {p}: {err}")
            print 
        
    return count_diffs

## #############################################
def model_is_crashed(ginhand:gin.Hand):
    if not hasattr(ginhand, 'turns'):
        return False
    total_flunks = 0
    total_turns = 0
    count_flunks = 0
    for t in ginhand.turns:
        if not hasattr(t, "turn_scores"):
            continue
        total_turns += 1
        count_zeroes_turn = 0
        for ts in t.turn_scores:
            if ts == 0:
                count_zeroes_turn +=1
        if count_zeroes_turn > len(t.turn_scores)-1:
            count_flunks +=1  # zero or one non-zero value returned
            total_flunks += 1
        elif t.turn_scores[0] != 0:
            count_flunks = 0  # something interesting, anyway

    if count_flunks > 10:
        return True

    if total_flunks > total_turns*0.9:
        return True

    return False

## #############################################
def run(params):
    """
    Use the DQN to play gin, via a ginDQNStrategy            
    """
    pretrain_weights = None

    agent = initalizeDQN(params)
    if agent.load_weights_success:
        print(f"weights loaded from {agent.weights_path}")
        if params['train']:
            pretrain_weights = agent.state_dict()

    counter_hands = 0
    winMap = {}
    winMap[params['player_one_name']] = 0				
    winMap[params['player_two_name']] = 0				
    winMap[NO_WIN_NAME] = 0				

    stats = Stats()
    stats.put("run_timestamp", datetime.datetime.now())
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
                                float(params['noise_epsilon']))

        # create GinHand, re-using the agent each time
        ginhand = gin.GinHand(gin.Player(params['player_one_name']),
                                    BrandiacGinStrategy(params['brandiac_random_percent']),
                                gin.Player(params['player_two_name']),
                                    ginDQN.ginDQNStrategy(params,agent))

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
            display(counter_hands, hand_duration, ginhand, 
                ('log_decisions' in params) and params['log_decisions'])

        if model_is_crashed(ginhand):
            print(f"** possible model crash at hand {counter_hands} **")
            state_dict = agent.state_dict()
            # print(state_dict)

    total_duration = time.time() - startTime
    
    if params['train']:
        posttrain_weights = agent.state_dict()
        params["weights_path"] += ".post_training"
        torch.save(posttrain_weights, params["weights_path"])
        print(f"weights saved to {params['weights_path']}")
        if not pretrain_weights==None:
            count_diffs = compare_weights(pretrain_weights, posttrain_weights)
            if count_diffs == 0:
                print(f"** WARNING: weights appear unchanged after training **")

    mean_durations, stdev_durations = get_mean_stdev(durations)
    mean_turns, stdev_turns = get_mean_stdev(turns_in_hand)

    stats.put("count_hands", counter_hands)
    stats.put("total duration", total_duration)
    stats.put("winMap", winMap)
    stats.put("mean_turns", mean_turns)
    stats.put("stdev_turns", stdev_turns)
    stats.put("mean_durations", mean_durations)
    stats.put("stdev_durations", stdev_durations)
    stats.put("stdev_durations", stdev_durations)

    return stats

## #############################################
if __name__ == '__main__':

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", nargs='?', type=distutils.util.strtobool, default=True)
    args = parser.parse_args()
    print("learningGin: args ", args)

    try:

        params = ginDQNParameters.define_parameters()
        params['display'] = args.display
        
        log = None
        old_stdout = None
        if 'log_path' in params:
            log_path = params['log_path']
            log = open(log_path, "a")
            if log.writable:
                old_stdout = sys.stdout
                sys.stdout = log

        start_time = time.time()
        print(f"****** learningGin execution at {datetime.datetime.now()} ")
        print(f"params: {params}")

        if params['train']:
            print("Training...")
            stats = run(params) 
            print_stats(stats)

        if params['test']:
            print("Testing...")
            params['train'] = False
            params['load_weights'] = True 
            stats = run(params)  
            print_stats(stats)

        print(f"****** learningGin execution took {time.time() - start_time} seconds")

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not log == None:
            log.close()
