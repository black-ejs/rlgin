import datetime
import sys
import time
import argparse
import statistics

import resource
MAX_MEMORY= 1024*1024*1024
import os
import psutil

import copy
import torch.optim as optim
import torch 

import DQN 
import gin
from playGin import BrainiacGinStrategy, BrandiacGinStrategy
import playGin 
import ginDQN
import ginDQNParameters
from ginDQNConvoBitPlanes import ginDQNConvoBitPlanes
from ginDQNConvoFloatPlane import ginDQNConvoFloatPlane
from ginDQNLinear import ginDQNLinear
from ginDQNLinearB import ginDQNLinearB
import ginDQNConvFHandOut
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
            self.ginDQN = self.initializeDQN(dqn_params)
        if self.strategy == "nn-cfh":
            nn_strategy = ginDQNConvFHandOut.ginDQNHandOutStrategy(dqn_params, self.ginDQN)
            nn_strategy.benchmark_scorer = ginDQNConvFHandOut.ginHandOutBenchmarkStrategy ()
        else:
            nn_strategy = ginDQN.ginDQNStrategy(dqn_params, self.ginDQN)
            nn_strategy.benchmark_scorer = BrainiacGinStrategy()
        return nn_strategy

    def initializeDQN(self,params):
        params['output_size'] = 1    

        if self.strategy == "nn-linear":
            ginDQN = ginDQNLinear(params)
        elif self.strategy == "nn-linearb":
            ginDQN = ginDQNLinearB(params)
        elif self.strategy == "nn-convf":
            ginDQN = ginDQNConvoFloatPlane(params)
        elif self.strategy == "nn-convb":
            ginDQN = ginDQNConvoBitPlanes(params)    
        elif self.strategy == "nn-cfh":
            ginDQN = ginDQNConvFHandOut.ginDQNConvFHandOut(params)

        print(f"sending DQN ({self.strategy}/{type(ginDQN).__name__}) to DEVICE ('{DQN.DEVICE}') for player {self.name}")
        ginDQN = ginDQN.to(DQN.DEVICE)

        if params['train']:
            ginDQN.optimizer = optim.Adam(ginDQN.parameters(), 
                                weight_decay=0, lr=params['learning_rate'])

        if ginDQN.load_weights_success:
            print(f"weights loaded from {ginDQN.weights_path} for player '{self.name}' with strategy '{self.strategy}'")
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
def display(counter_hands, hand_duration, ginhand:(gin.GinHand), log_decisions):
    winner = ginhand.winner
    if not winner == None:
        winner_name = winner.player.name
        hand = f"Hand: {winner.playerHand.prettyStr()}    "
    else:
        winner_name = NO_WIN_NAME
        hand = ""
    gs_winner, gin_score, is_done = ginhand.ginScore()
    display_line = (  
            f"Game {counter_hands}    " + 
            f"Winner: {winner_name}    " + 
            f"{hand}" + 
            f"Turns: {len(ginhand.turns)}    " + 
            f"Time: {hand_duration*1000:3.2f}   " + 
            f"Score: {ginhand.playingOne.player.name} {ginhand.playingOne.playerHand.ginScore()}  " +
                   f"{ginhand.playingTwo.player.name} {ginhand.playingTwo.playerHand.ginScore()}  " +  
                   f"net {ginhand.ginScore()[1]}   " +  
            "")
    if len(ginhand.nn_players)>0:
        reward_str = "Reward: "
        for p in ginhand.nn_players:
            reward_str += f"{p}  {ginhand.nn_players[p]['total_reward']}   " 
        display_line += reward_str
    print(display_line)

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
                    return
                #cc = np.corrcoef(
                #    np.array(
                #        [correlation_array_dqn,
                #         correlation_array_benchmark]))                
                #print(f"benchmark-correlation: {cc[0,1]}")
                #print(f"benchmark-correlation: N/A")
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
    nn_players = []
    for p in players:
        if p.is_nn_player():
            nn_players.append(p)
            p.total_reward = 0

    winMap = {player1.name:0, player2.name:0, NO_WIN_NAME:0}
    stats.put('winMap', winMap)

    startTime = time.time()
    print(f"--- SCENARIO START at {startTime} ---")
    print(params)

    while counter_hands < params['episodes']:
        ## TODO: check for abort
        
        # create GinHand, re-using the agent each time
        ginhand = gin.GinHand(gin.Player(player1.name),
                                player1.get_strategy(),
                                gin.Player(player2.name),
                                player2.get_strategy())
        ginhand.nn_players = {}
        for p in nn_players:
            ginhand.nn_players[p.name] = {}
            ginhand.nn_players[p.name]['name'] = p.name
            ginhand.nn_players[p.name]['total_reward'] = 0

        ginhand.deal()

        # agent.epsilon is set to give randomness to actions
        # during training, it starts high and reduces a bit each hand
        # noise eplsilon is the basic level that remains even when not treaining
        for p in nn_players:
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
        for p in nn_players:
            if p.ginDQN.params['train']:
                p.replay_new()
        hand_duration = time.time() - hand_startTime

        # stats and reporting
        durations.append(hand_duration)
        turns_in_hand.append(len(ginhand.turns))
        if not winner == None:
            winMap[winner.player.name] = winMap[winner.player.name]+1
        else:
            winMap[NO_WIN_NAME] = winMap[NO_WIN_NAME]+1
        for p in nn_players:
            p.total_reward += ginhand.nn_players[p.name]['total_reward']

        if params['display']:
            display(counter_hands, hand_duration, ginhand, 
                ('log_decisions' in params) and params['log_decisions'])
            
        if 'max_python_memory' in params:
            print_psinfo()

        #if model_is_crashed(ginhand):
        #    print(f"** possible model crash at hand {counter_hands} **")
        #    # state_dict = agent.state_dict()
        #    # print(state_dict)

    endTime = time.time()
    total_duration = endTime - startTime
    
    total_reward = []
    for p in nn_players:
        if p.ginDQN.params['train']:
                p.save_weights()
        total_reward.append((p.name,p.total_reward))

    mean_durations, stdev_durations = get_mean_stdev(durations)
    mean_turns, stdev_turns = get_mean_stdev(turns_in_hand)

    stats.put("start_time", startTime)
    stats.put("end_time", endTime)
    stats.put("count_hands", counter_hands)
    stats.put("count_hands", counter_hands)
    stats.put("total_duration", total_duration)
    stats.put("total_reward", total_reward) # list 
    stats.put("winMap", winMap)
    stats.put("mean_turns", mean_turns)
    stats.put("stdev_turns", stdev_turns)
    stats.put("mean_durations", mean_durations)
    stats.put("stdev_durations", stdev_durations)
    print(f"--- SCENARIO END at {time.time()} ---")

    return stats

## #############################################
def run_train_test(params):
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
        if 'test_epsiodes' in params:
            params['episodes'] = params['test_episodes']
        stats = run(params)  
        print_stats(stats)

    print(f"****** learningGin execution took {time.time() - start_time} seconds at {datetime.datetime.now()}")

def print_psinfo(prefix=""):
    process = psutil.Process(os.getpid())
    print(f"{prefix}max_rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} "
        f"psinfo={process.memory_info().rss}/{process.memory_percent():1.2f}%")

## #############################################
## #############################################
## #############################################
import importlib
def import_parameters(parameters_file:str) -> dict:
    parameters_file=os.path.expanduser(parameters_file)
    elements=parameters_file.split("/")
    module_name=elements[-1]
    print(f"importing params from: {module_name}")
    p=importlib.import_module(module_name)
    params = p.define_parameters()
    #params = parameters_file.define_parameters()
    return params

## #############################################
if __name__ == '__main__':

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", nargs='?', type=int, default=-1)
    parser.add_argument("--params_module", nargs='?', type=str, default=None)
    parser.add_argument("--name_scenario", nargs='?', type=str, default=None)
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    parser.add_argument("--weightsfile_1", nargs='?', type=str, default=None)
    parser.add_argument("--weightsfile_2", nargs='?', type=str, default=None)
    parser.add_argument("--generation", nargs='?', type=int, default=-1)
    parser.add_argument("--max_memory", nargs='?', type=int, default=-1)
    # parser.add_argument("--display", nargs='?', type=distutils.util.strtobool, default=True)
    args = parser.parse_args()
    print("learningGin: args ", args)

    if (args.params_module == None):
        print("using default parameters")
        params = ginDQNParameters.define_parameters()
    else:
        params = import_parameters(args.params_module)

    params['display'] = True

    if args.episodes != -1:
        params['episodes'] = args.episodes
    if args.name_scenario != None:
        params['name_scenario'] = args.name_scenario
    if not (args.logfile == None):
        params['log_path'] = args.logfile        
    if not (args.weightsfile_1 == None):
        if 'nn' in params['player1']:
            weightsfile=os.path.expanduser(args.weightsfile_1)
            params['player1']['nn']['weights_path']  = weightsfile
        else:
            print("*** WARNING, --weightsfile_1 specificed but player1 is not a neural net ")
    if not (args.weightsfile_2 == None):
        if 'nn' in params['player2']:
            weightsfile=os.path.expanduser(args.weightsfile_2)
            params['player2']['nn']['weights_path']  = weightsfile
        else:
            print("*** WARNING, --weightsfile_2 specificed but player2 is not a neural net ")
    if args.generation != -1:
        params['generation'] = args.generation
    if args.max_memory != -1:
        params["max_python_memory"] = args.max_memory

    old_stdout = None
    old_stderr = None
    log = None
    try:
            
        if 'log_path' in params:
            log_path = params['log_path']
            log_path = os.path.expanduser(log_path)
            if len(log_path)>0:
                log = open(log_path, "w")
                if log.writable:
                    old_stdout = sys.stdout
                    sys.stdout = log
                    old_stderr = sys.stderr
                    sys.stderr = log

        if 'max_python_memory' in params:
            target_mpm = params["max_python_memory"]
            print(f"setting max_python_memory={target_mpm}")
            process = psutil.Process(os.getpid())
            print_psinfo(" pre:  ")
            old_mpm = resource.getrlimit(resource.RLIMIT_AS)
            rez_mpm = resource.setrlimit(resource.RLIMIT_AS,
                            [params["max_python_memory"],
                             params["max_python_memory"]])
            new_mpm = resource.getrlimit(resource.RLIMIT_AS)
            print(f" old={old_mpm} rez={rez_mpm} new={new_mpm}")
            print_psinfo(" post: ")

        run_train_test(params)

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not old_stderr == None:
            sys.stderr = old_stderr
        if not log == None:
            log.close()

