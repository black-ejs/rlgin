import datetime

def define_parameters():
    params = dict()

    params['episodes'] = 5                  # gin hands

    # PLAYER 1
    params['player1'] = {}
    params['player1']['name'] = 'Primo'
    #params['player1']['strategy'] = 'br90'
    #params['player1']['brandiac_random_percent'] = 90 # assuming opponent = BrandiacGinStrategy 
    params['player1']['strategy'] = 'nn-convb'
    params['player1']['nn'] = {}
    params['player1']['nn']['layer_sizes'] = [88, 300, 20]   # 'hidden'/interior layers - per bayesDqn.py April 2022
    params['player1']['nn']['weights_path'] = 'weights/weights.nn-convb.h5'
    params['player1']['nn']['train'] = True
    params['player1']['nn']['test'] = True
    params['player1']['nn']["load_weights"] = False          # False if starting from scratch, True if re-training 
    params['player1']['nn']['gamma'] = 0.99                  # value of future rewards
    params['player1']['nn']['epsilon_decay_linear'] = 0.1    # while learning, how quickly randomness decreases in each hand - per bayesDqn.py April 2022
    params['player1']['nn']['learning_rate'] = 0.01          # how aggressively to modify weights - per bayesDqn.py April 2022
    params['player1']['nn']['noise_epsilon'] = 1/200         # randomness in actions when not training
    params['player1']['nn']['memory_size'] = 25000
    params['player1']['nn']['batch_size'] = 2500
    params['player1']['nn']['win_reward'] = 0.99            # per bayesReward.py April 2022
    params['player1']['nn']['loss_reward'] = -0.0045        # per bayesReward.py April 2022
    params['player1']['nn']['no_winner_reward'] = -0.0001   # per bayesReward.py April 2022

    # PLAYER 2
    params['player2'] = {}
    params['player2']['name'] = 'Tempo'
    params['player2']['strategy'] = 'nn-convf'
    params['player2']['nn'] = {}
    params['player2']['nn']['gamma'] = 0.99                  # value of future rewards
    params['player2']['nn']['layer_sizes'] = [100, 50, 20]  # 'hidden'/interior layers - per bayesDqn.py April 2022
    params['player2']['nn']['epsilon_decay_linear'] = 0.1    # while learning, how quickly randomness decreases in each hand - per bayesDqn.py April 2022
    params['player2']['nn']['learning_rate'] = 0.01          # how aggressively to modify weights - per bayesDqn.py April 2022
    params['player2']['nn']['noise_epsilon'] = 1/200         # randomness in actions when not training
    params['player2']['nn']['memory_size'] = 25000
    params['player2']['nn']['batch_size'] = 2500
    params['player2']['nn']['win_reward'] = 0.99            # per bayesReward.py April 2022
    params['player2']['nn']['loss_reward'] = -0.0045        # per bayesReward.py April 2022
    params['player2']['nn']['no_winner_reward'] = -0.0001   # per bayesReward.py April 2022
    params['player2']['nn']['train'] = True
    params['player2']['nn']['test'] = True
    params['player2']['nn']["load_weights"] = False   # False if starting from scratch, True if re-training 
    params['player2']['nn']['weights_path'] = 'weights/weights.nn-convf.h5'


    # game structure
    params['extend_hands'] = True          # recycle discards when deck is exhausted, up to max_steps_per_hand
    params['max_steps_per_hand'] = 1000    # max turns before no_winner, if 'extend_hands' == TRUE

    # logging 
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    params['timestamp'] = timestamp
    params['log_path'] = "logs/learningGin_log." + timestamp + ".txt"
    params["display"] = True
    params["log_decisions"] = True


    ############# these prams for 4-card game, from-scratch learning
    #params['gamma'] = 0.99                  # value of future rewards
    #params['noise_epsilon'] = 1/200         # randomness in actions when not training
    #params['memory_size'] = 25000
    #params['batch_size'] = 2500
    #params['layer_sizes'] = [100, 50, 20]  # 'hidden'/interior layers - per bayesDqn.py April 2022
    #params['epsilon_decay_linear'] = 0.1    # while learning, how quickly randomness decreases in each hand - per bayesDqn.py April 2022
    ## this is quite high             ^^^^   but perhaps for initial training on the simpolified game is it OK
    #params['learning_rate'] = 0.01          # how aggressively to modify weights - per bayesDqn.py April 2022

    # ##########################################
    # gin model control
    ############# these prams for 4-card game, from-scratch learning
    #params['win_reward'] = 0.99            # per bayesReward.py April 2022
    #params['loss_reward'] = -0.0045        # per bayesReward.py April 2022
    #params['no_winner_reward'] = -0.0001   # per bayesReward.py April 2022
    #params['brandiac_random_percent'] = 90 # assuming opponent = BrandiacGinStrategy 

    # ##########################################
    # App/execution Settings
    #params['player_one_name'] = "Primo"    # opponent
    #params['player_two_name'] = "Tempo"    # DQN

    #params['train'] = True
    #params["test"] = True           # run from saved weights after training or re-training
    #params["load_weights"] = False   # False if starting from scratch, True if re-training 
    #params['weights_path'] = 'weights/weights.h5'


    return params
