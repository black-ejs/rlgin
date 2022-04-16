import datetime

def define_parameters():
    params = dict()

    # ##########################################
    # Neural Network
    #  we will use a DQN which 
    #  expects an array of values as input
    #      and 
    #  produces an array of values as output 
    #  
    #  (in this implementation "values" are numpy objects, 
    #  basically high-precision floating-point numbers)
    #
    #  their values are specified by the 'input_size' and 'output_size'
    #  parameters
    #  
    #  the DQN can have any number of layers between the input and output
    #  as specified in the 'layer_sizes' array
    params['episodes'] = 5                  # gin hands
    params['layer_sizes'] = [100, 800, 20]  # 'hidden'/interior layers
    params['learning_rate'] = 0.00332519    # snake_ga = 0.00013629
    params['epsilon_decay_linear'] = 0.01   # while learning, how quickly randomness decreases in each hand
    params['gamma'] = 0.99                  # value of future rewards
    params['noise_epsilon'] = 1/200         # randomness in actions when not training
    params['memory_size'] = 25000
    params['batch_size'] = 2500

    # ##########################################
    # gin model control
    ############# these prams for 4-card game, from-scratch learning
    params['win_reward'] = 0.99            # per bayesReward.py 
    params['loss_reward'] = -0.0045        # per bayesReward.py
    params['no_winner_reward'] = -0.0001   # per bayesReward.py
    params['extend_hands'] = True          # recycle discards when deck is exhausted, up to max_steps_per_hand
    params['max_steps_per_hand'] = 1000    # max turns before no_winner, if 'extend_hands' == TRUE
    params['brandiac_random_percent'] = 90 # assuming opponent = BrandiacGinStrategy 

    # ##########################################
    # App/execution Settings
    params['player_one_name'] = "Primo"    # opponent
    params['player_two_name'] = "Tempo"    # DQN

    params['train'] = True
    params["test"] = True           # run from saved weights after training or re-training
    params["load_weights"] = False   # False if starting from scratch, True if re-training 
    params['weights_path'] = 'weights/weights.h5'

    # logging 
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    params['timestamp'] = timestamp
    params['log_path'] = 'logs/learningGin_log.' + timestamp +'.txt'
    params["display"] = True
    params["log_decisions"] = True

    return params
