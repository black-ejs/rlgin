import os
import ast
from GPyOpt.methods import BayesianOptimization

#################################################################
#   optimizes "one step" of a Byesfian Optimization       #######
#    input: a file of historical hyperparameters,         #######
#                      and the resulting score            #######
#    output: the "optimial" parameter set,                #######
#               i.e. the valuses for the next generation  #######
#################################################################
import numpy as np
# from numpy.random import seed
np.random.seed(10)
################################################
################################################
################################################
################################################
################################################
class HistoricalBayesianOptimizer():
    def __init__(self, optim_params, historical_file:str):
        self.optim_params = optim_params
        self.iteration_count = 0
        self.historical_file = historical_file
        if os.path.exists(self.historical_file):
            with open(self.historical_file,"r") as f:
                self.history = f.readlines()
        else:
            self.history = []

    ##########################################################
    def customize_inputs(self, inputs:list):
       return inputs

    ##########################################################
    def parse_result(self,line:str):
        result={}
        # myLine="result="+line
        # eval(myLine)
        result=ast.literal_eval(line)
        return result

    def append_next_result(self,inputs:list):
        result = {}
        for inp in inputs:
            result[self.optim_params[len(result)]['name']] = inp
        result['score']=0
        with open(self.historical_file,"a") as f:
            if len(self.history)>0:
                f.write("\n")
            f.write(f"{result}")

    ##########################################################
    def optimize_RL(self, max_iter:(int)=20, initial_iters:(int)=6):
        """
        optimizes the parameter sets conmtained in the historical file
        """
        def optimize(inputs):
            """
            This is the "inner loop" that runs a learning session
            with the provided set of learning parameters 
            """

            inputs=self.customize_inputs(inputs)

            score = 0
            self.iteration_count+=1
            if self.iteration_count == len(self.history) + 1:
                self.append_next_result(inputs[0])
            elif self.iteration_count <= len(self.history):
                print("INPUT", inputs)
                inputs = inputs[0]
                result = self.parse_result(self.history[self.iteration_count-1])
                if not isinstance(result,dict):
                    raise Exception(f"error: invalid historical data in input file {self.input_file}:\n"
                                    f"offending line={self.history[self.iteration_count]}\n"
                                    )

                # validate inputs
                i=0
                for o in inputs:
                    nm = self.optim_params[i]['name']
                    if not (nm in result and result[nm] == o):
                        raise Exception(f"error: historical data dies not match input:\n"
                                        f"inputs={inputs}\n"
                                        f"historical={result}\n"
                                        )
                    i+=1
                score = result['score']
                        
            return score
        
        ## #########################################################
        bayes_optimizer = BayesianOptimization(f=optimize,
                                               domain=self.optim_params,
                                               # model_type="RF",
                                               initial_design_numdata=initial_iters,
                                               acquisition_type="EI",
                                               exact_feval=True,
                                               # verbosity=True,
                                               maximize=True)

        max_iter=max(len(self.history),1)
        bayes_optimizer.run_optimization()
        for i in range(len(self.optim_params)):
            print(f"Optimized {self.optim_params[i]['name']}: ", bayes_optimizer.x_opt[i])
        #self.append_next_result(bayes_optimizer.x_opt)
        return
    
