import datetime
import sys
import copy
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
from playGin import BrainiacGinStrategy, BrandiacGinStrategy
import playGin 
import ginDQN
import ginDQNParameters
from ginDQNConvoBitPlanes import ginDQNConvoBitPlanes
from ginDQNConvoFloatPlane import ginDQNConvoFloatPlane
from ginDQNLinear import ginDQNLinear
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
class learningPlayer:
    def __init__(self, params):
        self.params = params
        self.name = params['name']
        self.strategy = params['strategy']
        self.ginDQN = None
        self.pretrain_weights = None

    def is_nn_player(self):
        return "nn-" in self.strategy
    
    def get_strategy(self):
        if self.is_nn_player():
            return self.get_nn_strategy()
        else:
            return playGin.get_strategy(self.strategy)

    def get_nn_strategy(self):
        dqn_params = self.params['nn']
        if self.ginDQN == None:
            self.ginDQN = self.initalizeDQN(dqn_params)
        nn_strategy = ginDQN.ginDQNStrategy(dqn_params, self.ginDQN)
        nn_strategy.benchmark_scorer = BrainiacGinStrategy()
        return nn_strategy

    def initalizeDQN(self,params):
        params['output_size'] = 1      # size of desired response, length of list of numpys 

        if self.strategy == "nn-linear":
            ginDQN = ginDQNLinear(params)
        elif self.strategy == "nn-convf":
            ginDQN = ginDQNConvoFloatPlane(params)
        elif self.strategy == "nn-convb":
            ginDQN = ginDQNConvoBitPlanes(params)    

        ginDQN = ginDQN.to(DEVICE)

        if params['train']:
            ginDQN.optimizer = optim.Adam(ginDQN.parameters(), 
                                weight_decay=0, lr=params['learning_rate'])

        if ginDQN.load_weights_success:
            print(f"weights loaded from {ginDQN.weights_path}")
            if params['train']:
                self.pretrain_weights = copy.deepcopy(ginDQN.state_dict())

        return ginDQN

    def replay_new(self):
        if self.is_nn_player():
            self.ginDQN.replay_new(self.ginDQN.memory, self.params['nn']['batch_size'])

    def save_weights(self):
        if self.is_nn_player():
            posttrain_weights = self.ginDQN.state_dict()
            self.params['nn']['weights_path'] += ".post_training"
            torch.save(posttrain_weights, self.params['nn']['weights_path'])
            print(f"weights saved to {self.params['nn']['weights_path']}")
            if not self.pretrain_weights==None:
                count_diffs = ginDQN.ginDQNStrategy.compare_weights(self.pretrain_weights, posttrain_weights)
                if count_diffs == 0:
                    print(f"** WARNING: {self.name}'s weights appear unchanged after training **")

## #############################################
def display(counter_hands, hand_duration, ginhand, log_decisions):
    winner = ginhand.winner
    if not winner == None:
        winner_name = winner.player.name
        hand = f"Hand: {winner.playerHand.prettyStr()}    "
    else:
        winner_name = NO_WIN_NAME
        hand = ""
    print(  f"Game {counter_hands}    " + 
            f"Winner: {winner_name}    " + 
            f"{hand}" + 
            f"Turns: {len(ginhand.turns)}    " + 
            f"Time: {hand_duration*1000:3.2f}   " + 
            f"Score: {ginhand.ginScore()[1]}   " +  
            f"Reward: {ginhand.total_reward}   " +
            "")

    if log_decisions:
        i=0
        correlation_array_dqn = []
        correlation_array_benchmark = []
        for t in ginhand.turns:
            if hasattr(t, 'turn_scores'):
                print(f"  turn {i} {t} > {t.turn_scores}")
            if hasattr(t, 'turn_benchmarks'):
                print(f"  bench {i} {t} > {t.turn_benchmarks}")
                correlation_array_dqn.extend(t.turn_scores)
                correlation_array_benchmark.extend(t.turn_benchmarks)
            i+=1
        if len(correlation_array_benchmark)>0:
            try:
                p1=len(correlation_array_dqn)
                p2=len(correlation_array_benchmark)
                if not p1==p2:
                    print("** warning correlations arrays different lengths :-(")
                cc = np.corrcoef(
                    np.array(
                        [correlation_array_dqn,
                         correlation_array_benchmark]))                
                print(f"benchmark-correlation: {cc[0,1]}")
            except RuntimeWarning:
                print(f"benchmark-correlation: 0")

## #############################################
def get_mean_stdev(array):
    return statistics.mean(array), statistics.stdev(array)    

## #############################################
def print_stats(stats, file=None):
    """
    force winMap to be last for parsing
    """
    if file == None:
        file = sys.stdout
    winMap = None
    if 'winMap' in  stats.stats:
        winMap = stats.stats['winMap']
    for key, value in stats.stats.items():
        if not key == 'winMap':
            print(f"{key}: {value}", file=file)
    if not winMap == None:
        print(f"winMap: {winMap}", file=file)

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
    counter_hands = 0
    total_reward = 0
    durations = []
    turns_in_hand = []

    stats = Stats()
    stats.put('run_timestamp', datetime.datetime.now())
    stats.put('params', params)

    player1 = learningPlayer(params['player1'])
    player2 = learningPlayer(params['player2'])
    players = [player1, player2]

    winMap = {player1.name:0, player2.name:0, NO_WIN_NAME:0}
    stats.put('winMap', winMap)

    print(f"--- SCENARIO START at {stats.get('run_timestamp')} ---")

    startTime = time.time()
    while counter_hands < params['episodes']:
        ## TODO: check for abort
        
        # create GinHand, re-using the agent each time
        ginhand = gin.GinHand(gin.Player(player1.name),
                                player1.get_strategy(),
                                gin.Player(player2.name),
                                player2.get_strategy())
        ginhand.deal()

        # agent.epsilon is set to give randomness to actions
        # during training, it starts high and reduces a bit each hand
        # noise eplsilon is the basic level that remains even when not treaining
        for p in players:
            if p.is_nn_player():
                if not p.ginDQN.params['train']:
                    p.ginDQN.epsilon = float(p.ginDQN.params['noise_epsilon'])
                else:
                    p.ginDQN.epsilon = max(
                                    1 - (counter_hands * p.ginDQN.params['epsilon_decay_linear']),
                                    float(p.ginDQN.params['noise_epsilon']))

        # pass in weights for comparison during learning
        ##if params['train'] and (not pretrain_weights==None):
        ##    dqnStrategy.pretrain_weights = pretrain_weights

        # play the hand
        hand_startTime = time.time()
        winner = ginhand.play(params['max_steps_per_hand'])
        counter_hands += 1
        for p in players:
            if p.is_nn_player() and p.ginDQN.params['train']:
                p.replay_new()
        hand_duration = time.time() - hand_startTime

        # stats and reporting
        durations.append(hand_duration)
        turns_in_hand.append(len(ginhand.turns))
        if hasattr(ginhand,'total_reward'):
            total_reward += ginhand.total_reward
        else:
            print('** WARNING: ginhand has no total_reward attribute, providing zero')
            ginhand.total_reward = 0
        if not winner == None:
            winMap[winner.player.name] = winMap[winner.player.name]+1
        else:
            winMap[NO_WIN_NAME] = winMap[NO_WIN_NAME]+1

        if params['display']:
            display(counter_hands, hand_duration, ginhand, 
                ('log_decisions' in params) and params['log_decisions'])

        #if model_is_crashed(ginhand):
        #    print(f"** possible model crash at hand {counter_hands} **")
        #    # state_dict = agent.state_dict()
        #    # print(state_dict)

    total_duration = time.time() - startTime
    
    for p in players:
        if p.is_nn_player() and p.ginDQN.params['train']:
                p.save_weights()

    mean_durations, stdev_durations = get_mean_stdev(durations)
    mean_turns, stdev_turns = get_mean_stdev(turns_in_hand)

    stats.put("count_hands", counter_hands)
    stats.put("total duration", total_duration)
    stats.put("winMap", winMap)
    stats.put("total_reward", total_reward)
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
    parser.add_argument("--episodes", nargs='?', type=int, default=-1)
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    parser.add_argument("--name_scenario", nargs='?', type=str, default=None)
    # parser.add_argument("--display", nargs='?', type=distutils.util.strtobool, default=True)
    args = parser.parse_args()
    print("learningGin: args ", args)

    try:

        params = ginDQNParameters.define_parameters()
        params['display'] = True

        if args.episodes != -1:
            params['episodes'] = args.episodes
        if args.name_scenario != None:
            params['name_scenario'] = args.name_scenario

        if not (args.logfile == None):
            params['log_path'] = args.logfile        
        log = None
        old_stdout = None
        if 'log_path' in params:
            log_path = params['log_path']
            if len(log_path)>0:
                log = open(log_path, "w")
                if log.writable:
                    old_stdout = sys.stdout
                    sys.stdout = log

        start_time = time.time()
        print(f"****** learningGin execution at {datetime.datetime.now()} ")
        print(f"params: {params}")

        do_train = False
        for p in ('player1', 'player2'):
            if ('nn' in params[p]) and ('train' in params[p]['nn']):
                do_train = (do_train or params[p]['nn']['train'])
        if do_train:
            print("Training...")
            stats = run(params) 
            print_stats(stats)

        do_test = False
        for p in ('player1', 'player2'):
            if ('nn' in params[p]) and ('test' in params[p]['nn']):
                test_param = params[p]['nn']['test']
                if test_param:
                    params[p]['nn']['train'] = False
                    params[p]['nn']['load_weights'] = True 
                    do_test = True
        if do_test:
            print("Testing...")
            stats = run(params)  
            print_stats(stats)

        print(f"****** learningGin execution took {time.time() - start_time} seconds")

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not log == None:
            log.close()
