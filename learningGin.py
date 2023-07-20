import copy
import datetime
import sys
import time
import argparse
import statistics
import os
import psutil

import resource
MAX_MEMORY= 1024*1024*1024

import gin
from ginDQNStrategy import ginDQNStrategy
import ginDQNParameters
NO_WIN_NAME = 'nobody'

import learningPlayer

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
def display(counter_hands:int, hand_duration:int, ginhand:(gin.GinHand), log_decisions:bool):
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
            f"Scoring: {ginhand.playingOne.player.name} {ginhand.playingOne.playerHand.deadwood()}  " +
                   f"{ginhand.playingTwo.player.name} {ginhand.playingTwo.playerHand.deadwood()}  " +  
                   f"net2win {gin_score}   " +  
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

    player1 = learningPlayer.learningPlayer(params['player1'])
    player2 = learningPlayer.learningPlayer(params['player2'])
    players = [player1, player2]
    nn_players = []
    for p in players:
        if p.is_nn_player():
            nn_players.append(p)
            p.get_strategy()
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
        ginhand.extend_hands =  params['extend_hands']
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

        if params['extend_hands']:
            max_turns=params['max_turns_per_hand']
        else:
            max_turns=1000

        # play the hand
        hand_startTime = time.time()
        try:
            winner = ginhand.play(max_turns)
        except Exception as err:
            print(f"*** ERROR *** : Exception raised while playing: {err}")
            print(f"ginhand: {ginhand}")

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
            if os.path.exists(p.ginDQN.params['weights_path']):
                p.ginDQN.params['weights_path'] += ".post_training"
            posttrain_weights = p.save_weights()
            if not (p.pretrain_weights==None or posttrain_weights==None):
                count_diffs = ginDQNStrategy.compare_weights(p.pretrain_weights, posttrain_weights)
                if count_diffs == 0:
                    print(f"** WARNING: {p.name}'s weights appear unchanged after training **")
        total_reward.append((p.name,p.total_reward))
        if hasattr(p.ginDQN,"forward_invocation_count"):
            if "dqn_forward_stats" in stats.stats:
                dqn_forward_stats = stats.get('dqn_forward_stats')
            else:
                dqn_forward_stats = {}
                stats.put("dqn_forward_stats", dqn_forward_stats)
            dfs = {}                  
            dqn_forward_stats[p.name] = dfs
            dfs['player'] = p.name
            dfs['player_strategy'] = p.strategy
            dfs['forward_invocation_count'] = p.ginDQN.forward_invocation_count
            dfs['forward_action_count'] = p.ginDQN.forward_action_count
            dfs['zero_invocation_count'] = p.ginDQN.zero_invocation_count
            dfs['zero_forward_count'] = p.ginDQN.zero_forward_count

    if len(durations)>0:
        mean_durations, stdev_durations = get_mean_stdev(durations)
    else:
         mean_durations, stdev_durations = 0,0
    if len(turns_in_hand)>0:
        mean_turns, stdev_turns = get_mean_stdev(turns_in_hand)
    else:
        mean_turns, stdev_turns = 0,0

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
def run_pretest(params):
    ## pretest
    return run_test(params, True)

## #############################################
def run_scratch(params):
    scratch_params = copy.deepcopy(params)
    do_scratch = False
    for p in ('player1', 'player2'):
        if 'nn' in scratch_params[p]:
            nnp = scratch_params[p]['nn']
            nnp['pretest']=False
            nnp['test']=False
            nnp['train']=True
            nnp['load_weights']=False
            do_scratch = True

    if do_scratch:
        scratch_params['episodes']=0
        print("Scratching...")
        stats = run(scratch_params) 
        print_stats(stats)

## #############################################
def run_train(params):
    ## train
    do_train = False
    for p in ('player1', 'player2'):
        if ('nn' in params[p]) and ('train' in params[p]['nn']):
            do_train = (do_train or params[p]['nn']['train'])
    if do_train:
        print("Training...")
        stats = run(params) 
        print_stats(stats)
    
## #############################################
def run_test(params,is_pretest:bool=False):

    ## test or pre-test
    if is_pretest:
        key="pretest"
        status="Pretest"
    else:
        key="test"
        status="Test"

    do_test = False
    do_train = False # just a snaity check for pretrain
    test_params = copy.deepcopy(params)
    for p in ('player1', 'player2'):
        if ('nn' in params[p]) and (key in params[p]['nn']):
            test_param = params[p]['nn'][key]
            if test_param:
                test_params[p]['nn']['train'] = False
                test_params[p]['nn']['load_weights'] = True 
                do_test = True
                if params[p]['nn']['train']:
                    do_train=True
                
    if do_test:
        if is_pretest and (not do_train):
            print(f"****** WARNING pretesting was requested, but no models are to be trained")
        test_runs=1
        if 'test_runs' in params:
            test_runs=max(int(params['test_runs']),0)
        if test_runs > 0:
            for test_run in range(test_runs):
                print(f"{status}ing...")
                print(f"{status.lower()} run: {test_run+1} of {test_runs}")
                if 'test_epsiodes' in params:
                    test_params['episodes'] = params['test_episodes']
                stats = run(test_params)  
                print_stats(stats)

## #############################################
def run_learningGin(params):
    start_time = time.time()
    print(f"****** learningGin execution at {datetime.datetime.now()} ")
    print(f"environment: {os.environ}")
    print(f"params: {params}")

    if params['scratch']:
        run_scratch(params)

    run_pretest(params)

    run_train(params)

    run_test(params)

    print(f"****** learningGin execution took {int(time.time()) - start_time} seconds at {datetime.datetime.now()}")

## #############################################
def print_psinfo(prefix=""):
    process = psutil.Process(os.getpid())
    print(f"{prefix}max_rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} "
        f"psinfo={process.memory_info().rss}/{process.memory_percent():1.2f}%")

## #############################################
def set_max_python_memory(target_mpm:int):
    print(f"setting max_python_memory={target_mpm}")
    process = psutil.Process(os.getpid())
    print_psinfo(" pre:  ")
    old_mpm = resource.getrlimit(resource.RLIMIT_AS)
    rez_mpm = resource.setrlimit(resource.RLIMIT_AS,
                                target_mpm,target_mpm)
    new_mpm = resource.getrlimit(resource.RLIMIT_AS)
    print(f" old={old_mpm} rez={rez_mpm} new={new_mpm}")
    print_psinfo(" post: ")

## #############################################
def run_with_logging(params:dict):
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
            set_max_python_memory(params["max_python_memory"])

        run_learningGin(params)

    finally:
        if not old_stdout == None:
            sys.stdout = old_stdout
        if not old_stderr == None:
            sys.stderr = old_stderr
        if not log == None:
            log.close()

## #############################################
## #############################################
## #############################################
import importlib
def import_parameters(parameters_file:str) -> dict:
    package_name = ""
    parameters_file=os.path.expanduser(parameters_file)
    module_name=parameters_file.replace("/",".")
    #elements=parameters_file.split("/")
    #module_name=elements[-1]
    #if len(elements) > 0:
    #   for e in elements:
    #       if len(package_name)>0:
    #           package_name+='.'
    #       package_name+=e
    if package_name == "":
        print(f"importing params from: {module_name}")
    else:
        print(f"importing params from: {module_name} in package {package_name}")
    p=importlib.import_module(module_name)
    params = p.define_parameters()
    return params

## #############################################
if __name__ == '__main__':

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", nargs='?', type=int, default=-1)
    parser.add_argument("--params_module", nargs='?', type=str, default=None)
    parser.add_argument("--name_scenario", nargs='?', type=str, default=None)
    parser.add_argument("--logfile", nargs='?', type=str, default=None)
    parser.add_argument("--generation", nargs='?', type=int, default=-1)
    parser.add_argument("--max_python_memory", nargs='?', type=int, default=-1)
    parser.add_argument("--weights_path_1", nargs='?', type=str, default=None)
    parser.add_argument("--weights_path_2", nargs='?', type=str, default=None) # default="weights/weights.nn-cfhp.20230625152610.h5") 
    parser.add_argument("--learning_rate_1", nargs='?', type=float, default=None)
    parser.add_argument("--learning_rate_2", nargs='?', type=float, default=None)
    parser.add_argument("--gamma_1", nargs='?', type=float, default=None)
    parser.add_argument("--gamma_2", nargs='?', type=float, default=None)
    parser.add_argument("--scratch", nargs='?', type=int, default=argparse.SUPPRESS)
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
    if args.generation != -1:
        params['generation'] = args.generation
    if args.max_python_memory != -1:
        params["max_python_memory"] = args.max_python_memory
             
    for player_index in ("1","2"):
        player_key="player" + player_index
        for key_root in ("weights_path", "gamma", "learning_rate"):
            params_key=key_root
            args_key=f"{key_root}_{player_index}"
            argvars = vars(args)
            if (args_key in argvars) and (not (argvars[args_key] == None)):
                param_val = argvars[args_key]
                if isinstance(param_val,str):
                    param_val=os.path.expanduser(param_val)
                if 'nn' in params[player_key]:
                    params[player_key]['nn'][params_key]  = param_val
                else:
                    print(f"*** WARNING, --{args_key} specified but {player_key} is not a neural net ")

    if hasattr(args,'scratch'):
        params['scratch'] = True
    elif not 'scratch' in params:
        params['scratch'] = False

    run_with_logging(params)

