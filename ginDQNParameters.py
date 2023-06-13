import datetime
import copy

def define_parameters():
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    params = dict()

    params['episodes'] = 50    # gin hands
    params['test_runs'] = 5

    epsilon_decay_percent = 3   # 3% of hands
    epsilon_episodes = (epsilon_decay_percent/100)*params['episodes']
    epsilon_decay_linear_increment = 1/epsilon_episodes 

    # nn-common
    params['nn-common'] = {}
    params['nn-common']['learning_rate'] = 0.03          # BLG/train June 2023 
    params['nn-common']['gamma'] = 0.842                 # BLG/train June 2023 
    #params['nn-common']['learning_rate'] = 0.1731       # BLG/scratch June 2023 
    #params['nn-common']['gamma'] = 0.9077               # BLG/scratch June 2023 
    params['nn-common']['epsilon_decay_linear'] = epsilon_decay_linear_increment 
    params['nn-common']['noise_epsilon'] = 1/500         # randomness in actions when not training
    params['nn-common']['replay_memory_size'] = 25000
    params['nn-common']['batch_size'] = 2500
    params['nn-common']['win_reward'] = 0.99            
    params['nn-common']['loss_reward'] = -0.3           
    params['nn-common']['no_winner_reward'] = -0.1   

    # PLAYER 1
    params['player1'] = {}
    params['player1']['name'] = 'Primo'
    params['player1']['strategy'] = 'br90'

    # PLAYER 2
    params['player2'] = {}
    params['player2']['name'] = 'Tempo'
    params['player2']['strategy'] = 'nn-cfhp' 
    params['player2']['nn'] = copy.deepcopy(params['nn-common'])
    params['player2']['nn']['layer_sizes'] = [800, 300, 20]   
    params['player2']['nn']['conv_layer_kernels'] = 20   
    params['player2']['nn']['train'] = True
    params['player2']['nn']['test'] = True
    params['player2']['nn']['pretest'] = params['player2']['nn']['train']
    params['player2']['nn']["load_weights"] = True   
    params['player2']['nn']['weights_path'] = f"weights/weights.{params['player2']['strategy']}.{timestamp}.h5"
    #params['player2']['nn']['weights_path'] = "weights/weights.nn-cfhp.20230612134023.h5"
    params['player2']['nn']['use_cheat_rewards'] = False

    # game structure
    params['extend_hands'] = False          # recycle discards when deck is exhausted, up to max_turns_per_hand
    params['max_turns_per_hand'] = 100     # max turns before no_winner, if 'extend_hands' == TRUE
    params['scratch'] = False

    # logging 
    params['timestamp'] = timestamp
    # params['log_path'] = "logs/learningGin_log." + timestamp + ".txt"
    params['log_path'] = "logs/ttt"
    params["display"] = True
    params["log_decisions"] = False

    return params
