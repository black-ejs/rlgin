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
    params['episodes'] = 1000             # gin hands
    params['layer_sizes'] = [60,150,16]   # 'hidden'/interior layers
    params['learning_rate'] = 0.012       # snake_ga = 0.00013629
    params['epsilon_decay_linear'] = .016 # while learning, how quickly randomness decreases in each hand
    params['gamma'] = 0.99                # value of future rewards
    params['noise_epsilon'] = 1/200       # randomness in actions when not training
    params['memory_size'] = 25000
    params['batch_size'] = 2500

    # ##########################################
    # App/execution Settings
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    params['timestamp'] = timestamp
    params['player_one_name'] = "Primo"    # opponent
    params['player_two_name'] = "Tempo"    # DQN
    params['max_steps_per_hand'] = 1000    # turns
    params['extend_hands'] = True          # recycle duscards when deck is exhausted, up to max_steps_per_hand
    params['brandiac_random_percent'] = 90 # assuming opponent = BrandiacGinStrategy 

    params['train'] = True
    params["load_weights"] = True   # False if starting from scratch, True if re-training 
    params["test"] = True           # run from saved weights after training or re-training
    params["display"] = True
    params['plot_score'] = False
    params['log_path'] = 'logs/learningGin_log.' + timestamp +'.txt'
    params['weights_path'] = 'weights/weights.h5'

    return params
