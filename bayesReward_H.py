import datetime
import sys 
from  bayesHistory import HistoricalBayesianOptimizer

optim_params = [
    {"name": "win_reward", "type": "continuous", "domain": (0.75, 0.99), "fmt": "0.3f"},
    {"name": "loss_reward", "type": "continuous", "domain": (-0.09, -0.009), "fmt": "0.3f"},
    {"name": "no_winner_reward", "type": "continuous", "domain": (-0.001, -0.000001), "fmt": "0.3f"}
    ]

##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(f"bayesReward.py: Bayesian model optimization starting at {start_time}") 

    if len(sys.argv)>1:
        input_file = sys.argv[1]
    else:
        input_file="doodoo.k"

    ## run optimization
    bayesOpt = HistoricalBayesianOptimizer(optim_params,input_file)
    bayesOpt.optimize_RL()

    ## report
    end_time = datetime.datetime.now() - start_time
    print(f"bayesReward.py: Bayesian optimization run took {end_time}") 

