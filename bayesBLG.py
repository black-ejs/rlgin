import datetime
import sys 
import math
import argparse
from  bayesHistory import HistoricalBayesianOptimizer

optim_params = [
    {"name": "lr", "type": "continuous", "domain": ( -6.0, -0.6932), "fmt": "0.4f"},
    {"name": "gamma", "type": "continuous", "domain": (0.6, 0.91), "fmt": "0.3f"},
    ]

class BLGBayesAnalyzer(HistoricalBayesianOptimizer):
    def __init__(self,optim_params:list,historical_file:str):
        super().__init__(optim_params,historical_file)

    ##########################################################
    def customize_inputs(self, inputs:list):
        inputs[0][0] = math.exp(inputs[0][0])
        return inputs

##################
#      Main      #
##################
if __name__ == '__main__':
    start_time = datetime.datetime.now()

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--history_file", nargs='?', type=str, default=None)
    parser.add_argument("--lr_low", nargs='?', type=float, default=-6.0)
    parser.add_argument("--lr_high", nargs='?', type=float, default=-0.69)
    parser.add_argument("--gamma_low", nargs='?', type=float, default=0.6)
    parser.add_argument("--gamma_high", nargs='?', type=float, default=0.91)
    args = parser.parse_args()

    if args.history_file ==None:
        args.history_file=f"bayesBLG.{start_time}.out"

    for op in optim_params:
        if op['name'] == "lr":
            op['domain'] = (args.lr_low, args.lr_high)
        elif op['name'] == "gamma":
            op['domain'] = (args.gamma_low, args.gamma_high)

    ## run optimization
    bayesOpt = BLGBayesAnalyzer(optim_params,args.history_file)
    bayesOpt.optimize_RL(max_iter=200,initial_iters=6)

    ## report
    end_time = datetime.datetime.now() - start_time
    print(f"done.") 

