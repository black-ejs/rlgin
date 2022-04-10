import datetime
import ginDQNParameters
from  bayesOpt import TrainingBayesianOptimizer

optim_params = [
    {"name": "win_reward", "type": "continuous", "domain": (0.75, 0.99), "fmt": "0.3f"},
    {"name": "loss_reward", "type": "continuous", "domain": (-0.20, -0.009), "fmt": "0.3f"},
    {"name": "no_winner_reward", "type": "continuous", "domain": (-0.01, -0.001), "fmt": "0.3f"}
    ]

##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(f"bayesReward.py: Bayesian model optimization starting at {start_time}") 

    ## set up params
    params = ginDQNParameters.define_parameters()
    params['log_path'] = 'logs/bayesReward_log.' + params['timestamp'] +'.txt'
    params['episodes'] = 3  ##################
    params['max_steps_per_hand'] = 100 ####################

    ## run optimization
    bayesOpt = TrainingBayesianOptimizer(params, optim_params)
    bayesOpt.optimize_RL()

    ## report
    end_time = datetime.datetime.now() - start_time
    print(f"bayesModel.py: Bayesian optimization run took {end_time}") 

