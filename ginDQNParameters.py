import datetime
import copy

def define_parameters():
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    params = dict()

    params['episodes'] = 50                  # gin hands

    # nn-common
    params['nn-common'] = {}
    params['nn-common']['gamma'] = 0.91                  # value of future rewards
    params['nn-common']['epsilon_decay_linear'] = 300/params['episodes']   # 3% of hands
    params['nn-common']['learning_rate'] = 0.0075        # how aggressively to modify weights
    params['nn-common']['noise_epsilon'] = 1/500         # randomness in actions when not training
    params['nn-common']['memory_size'] = 25000
    params['nn-common']['batch_size'] = 2500
    params['nn-common']['win_reward'] = 0.99            # per bayesReward.py April 2022
    params['nn-common']['loss_reward'] = -0.0045        # per bayesReward.py April 2022
    params['nn-common']['no_winner_reward'] = -0.0001   # per bayesReward.py April 2022

    # PLAYER 1
    params['player1'] = {}
    params['player1']['name'] = 'Primo'
    params['player1']['strategy'] = 'br90'
    # params['player1']['strategy'] = 'nn-linearb'
    # params['player1']['nn'] = copy.deepcopy(params['nn-common'])
    # params['player1']['nn']['layer_sizes'] = [312, 800, 50]   # 'hidden'/interior layers - per bayesDqn.py April 2022
    # params['player1']['nn']['train'] = True
    # params['player1']['nn']['test'] = True
    # params['player1']['nn']["load_weights"] = False          # False if starting from scratch, True if re-training 
    # params['player1']['nn']['weights_path'] = "weights/weights." + params['player1']['strategy']  + ".h5"
    # params['player1']['nn']['use_cheat_rewards'] = False

    # PLAYER 2
    params['player2'] = {}
    params['player2']['name'] = 'Tempo'
    params['player2']['strategy'] = 'nn-linearb'
    params['player2']['nn'] = copy.deepcopy(params['nn-common'])
    params['player2']['nn']['layer_sizes'] = [400, 200, 40]   # 'hidden'/interior layers - per bayesDqn.py April 2022
    params['player2']['nn']['train'] = True
    params['player2']['nn']['test'] = True
    params['player2']['nn']["load_weights"] = False   # False if starting from scratch, True if re-training 
    params['player2']['nn']['weights_path'] = "weights/weights." + params['player2']['strategy']  + ".h5"
    params['player2']['nn']['use_cheat_rewards'] = False

    # game structure
    params['extend_hands'] = True          # recycle discards when deck is exhausted, up to max_steps_per_hand
    params['max_steps_per_hand'] = 100     # max turns before no_winner, if 'extend_hands' == TRUE

    # logging 
    params['timestamp'] = timestamp
    params['log_path'] = "logs/learningGin_log." + timestamp + ".txt"
    params["display"] = True
    params["log_decisions"] = True

    return params
