from collections.abc import Iterable
import random
import torch
import torch.nn as nn
import torch.nn.functional as F

from DQN import DEVICE
from  ginDQNStrategy import ginDQNStrategy
from  ginDQN import ginDQN
import playGin

## ###############################################
class ODStrategy(ginDQNStrategy):
    def __init__(self,params,agent:(ginDQN)):
        super().__init__(self)

        self.delegate = playGin.OneDecisionGinStrategy()

    def scoreCandidate(self, myHand, candidate, ginhand):
        # perform random actions based on agent.epsilon, or choose the action
        current_state = self.agent.get_state(ginhand,self.myPlayer,candidate)
        is_random = False
        score = None
        if random.uniform(0, 1) < self.agent.epsilon:
            score = self.get_random_score()
            is_random = True
        else:
            # predict action based on the state
            with torch.no_grad():
                state_old_tensor = torch.tensor(current_state.reshape(self.agent.input_size), 
                                                dtype=torch.float32).to(DEVICE)
                prediction = self.agent(state_old_tensor)
                score = self.translatePrediction(prediction)
        self.turn_scores.append(score)
        self.turn_states.append(current_state)
        if (not self.benchmark_scorer == None): ## and (not candidate==None):
            benchmark = self.benchmark_scorer.scoreCandidate(
                                myHand, candidate, ginhand)
            self.turn_benchmarks.append(benchmark)
        return score
        
            
