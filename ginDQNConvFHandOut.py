import collections

import numpy as np
import torch 
import torch.nn as nn
import torch.nn.functional as F
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

import gin
import playGin
import ginDQN
from ginDQNConvoFloatPlane import ginDQNConvoFloatPlane

# ******************************
class ginDQNConvFHandOut(ginDQNConvoFloatPlane):

    def __init__(self, params):
        params['output_size'] = gin.HAND_SIZE + 1 
        super().__init__(params)
        self.output_size = gin.HAND_SIZE + 1
        self.input_state = None

    def get_state(self, ginhand:(gin.GinHand), 
                         player:(gin.Player), 
                         pile_substitute:(gin.Card) = None):
        self.input_state = super().get_state(ginhand, player, pile_substitute)
        return self.input_state

    def create_layers(self):
        # Layers
        llayers = []
        llayers.append(self.create_conv_layer())

        # self.convo_output_size has now been set
        prev_layer_size = self.convo_output_size + self.input_size[2]*self.input_size[3]

        for layer_size in self.layer_sizes:
            llayers.append(nn.Linear(prev_layer_size, layer_size))
            prev_layer_size = layer_size
        llayers.append(nn.Linear(prev_layer_size, self.output_size))
        self.layers = nn.ModuleList(llayers)

    def forward(self, x):
        # Conv2D layer
        x = self.layers[0](x)
        x = x.reshape(self.convo_output_size)  

        # append to input state and pass to linear layers
        input_state_size = self.input_size[2]*self.input_size[3]
        y = torch.tensor(self.input_state.reshape(input_state_size)).float()
        combined_input_size = self.convo_output_size + input_state_size
        x = torch.cat((y,x))

        # Linear Layers
        for layer in self.layers[1:-1]:
            if 'no_relu' in self.params and self.params['no_relu']:
                x = layer(x)
            else:
                x = layer(x)
                x = F.relu(x)
        x = self.layers[-1](x) # last layer
        return x

    # because we use "argmin" to parse our model's output
    # we want LOWER values to be MORE correct
    # we will reverse the normal "more is more" 
    #def set_reward(self, ginhand, player):
    #    self.reward = -super().set_reward(ginhand, player)
    #    return self.reward

## ###############################################
## ###############################################
## ###############################################
## ###############################################
class ginDQNHandOutStrategy(ginDQN.ginDQNStrategy):
    def __init__(self,params,agent:(ginDQN)):
        return super().__init__(params, agent)

    # if lowest-value card is the offered discard, choose from the DECK
    # otherwise choose the offered discard, we will subsequently 
    # discard the lowest-value card
    def decideDrawSource(self,ginhand:gin.GinHand):
        score_array = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
        lowest = 99999.99999
        lowest_i = -1
        for i in range(len(score_array)):
            if score_array[i] < lowest:
                lowest = score_array[i]
                lowest_i = i
        
        if lowest_i == len(score_array)-1:
            return gin.Draw.DECK
        else:
            return gin.Draw.PILE

    def decideDiscardCard(self,ginhand:gin.GinHand):
        score_array = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
        lowest = 99999.99999
        lowest_i = -1
        for i in range(len(score_array)):
            if score_array[i] < lowest:
                lowest = score_array[i]
                lowest_i = i

        if lowest_i < 0:
            return ginhand.currentlyPlaying.playerHand.card[lowest_i]
        elif lowest_i < len(score_array):
             return ginhand.currentlyPlaying.playerHand.card[lowest_i]
        else:
            return ginhand.discard

    def translatePrediction(self, prediction):
        detached = prediction.detach().cpu().numpy()
        if not isinstance(detached, collections.Iterable):
            translation = float(detached)
        else:
            detached_list = detached.tolist()
            translation = []
            for i in detached_list:
                translation.append(float(i))
        return translation

    def learnTurn(self, turn_states, turn_scores, reward, new_state, isDone = False, is_first_turn=False):
        """
        there should be 2 each of states/scores/benchmarks
           - [0] == DrawDecision
           - [1] == DiscardDecision
        """
        if not len(turn_scores)==2 and len(turn_states)==2:
            print("WTF")
        draw_state = turn_states[0]
        draw_score = turn_scores[0]
        discard_state = turn_states[1]
        discard_score = turn_scores[1]

        # store the new data into memory for experience replay
        self.agent.remember(draw_state, draw_score, reward, discard_state, False)
        self.agent.remember(discard_state, discard_score, reward, new_state, isDone)
        
## ###############################################
## ###############################################
## ###############################################
## ###############################################
class ginHandOutBenchmarkStrategy(playGin.BrainiacGinStrategy):
    def scoreCandidate(self, myHand:gin.Hand, candidate:gin.Card, ginhand:gin.GinHand):
        allCandidates = myHand.card.copy()
        allScores = []
        if not candidate == None:
            allCandidates.append(candidate)
        for c in allCandidates:
            h = allCandidates.copy()
            h.remove(c)
            allScores.append(super().scoreCandidate(gin.Hand(h), c, ginhand))
        return allScores

            
