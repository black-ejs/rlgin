import collections

import numpy as np
import torch 
import torch.nn as nn
import torch.nn.functional as F

import gin
import playGin
import DQN
import ginDQN
from ginDQNConvoFloatPlane import ginDQNConvoFloatPlane

# ******************************
class ginDQNConvFHandOut(ginDQNConvoFloatPlane):

    OUTPUT_SIZE = gin.HAND_SIZE + 1
    zero_action = torch.zeros((OUTPUT_SIZE))

    def __init__(self, params):
        params['output_size'] = self.OUTPUT_SIZE 
        super().__init__(params)
        self.output_size = self.OUTPUT_SIZE
        self.input_state = None
        self.forward_invocation_count = 0
        self.forward_action_count = 0
        self.zero_invocation_count = 0
        self.zero_forward_count = 0

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

    ## ###############################################
    def check_forward_product(self, x:torch.Tensor, 
                              input_tensor:torch.Tensor=None, 
                              title:str= "forward-product-tensor"):
        input_states_count = 0
        if not (type(input_tensor) == type(None)):
            input_states_count = input_tensor.shape[0]
            if not x.shape[0] == input_states_count:
                print(f"*** WARNING: {title}: count is: {x.shape[0]}, expected {input_states_count}")
        non_dupe=0
        non_zero=0
        for u in x:
            if not torch.eq(u,x[0]).all():
                non_dupe+=1
            if not torch.eq(u,torch.zeros(u.shape)).all():
                non_zero+=1
        if x.shape[0]>1:
            if not non_dupe>0:
                print(f"*** WARNING: {title}: entire list len={x.shape[0]} is identical")
            if not non_zero>0:
                print(f"*** WARNING: {title}: entire list len={x.shape[0]} is zeros")
                self.zero_forward_count+=1
        return non_dupe, non_zero
        
    ## ###############################################
    def forward(self, x):
        self.forward_invocation_count += 1

        # capture input stateÍ
        input_tensor = x
        input_shape = x.shape
        input_states_count = input_shape[0]
        if input_states_count > 1:
            #print(f"tensor of {input_states_count}")
            pass

        # Conv2D layer
        x = self.layers[0](x)   
        self.check_forward_product(x, input_tensor, "conv layer output")

        x = torch.flatten(x,1)  
        self.check_forward_product(x, input_tensor, "flattened conv layer output")

        # append to input state and pass to linear layers
        input_state_size = self.input_size[2]*self.input_size[3]
        flat_input = torch.flatten(input_tensor,1)
        self.check_forward_product(flat_input, input_tensor, "flattened input")
        
        obs=torch.cat((x,flat_input),1)
        self.check_forward_product(obs, input_tensor, "flattened conv and input combined")

        x=torch.Tensor(obs)
        self.check_forward_product(x, input_tensor, "flattened conv and input combined 2")

        # Linear Layers
        for layer in self.layers[1:-1]:
            if 'no_relu' in self.params and self.params['no_relu']:
                x = layer(x)
            else:
                x = layer(x)
                x = F.relu(x)

            non_dupe, non_zero = self.check_forward_product(x, input_tensor, f"linear layer[{layer.in_features}/{layer.out_features}] output")

        x = self.layers[-1](x) # last layer
        self.forward_action_count += x.shape[0]
        non_dupe, non_zero = self.check_forward_product(x, input_tensor, f"final output")
        if non_zero==0:
            self.zero_invocation_count += 1

        if x.shape[1] != gin.HAND_SIZE+1:
            print(f"***: WARNING: final output: count is: {x.shape[1]}, expected {gin.HAND_SIZE+1}")

        return x

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
        discard_me = DQN.argmax(score_array)
        
        if discard_me == len(score_array)-1:
            return gin.Draw.DECK
        else:
            return gin.Draw.PILE

    def decideDiscardCard(self,ginhand:gin.GinHand):
        score_array = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
        discard_me = DQN.argmax(score_array)

        if discard_me < 0:
            print(f"WARNING: invalid discard index {discard_me} in hand {ginhand.currentlyPlaying.playerHand}")
            return ginhand.currentlyPlaying.playerHand.card[0]
        elif discard_me < len(score_array):
            return ginhand.currentlyPlaying.playerHand.card[discard_me]
        else:
            return ginhand.discard

    def translatePrediction(self, prediction):
        detached = prediction.detach().cpu().numpy()
        if not isinstance(detached, collections.Iterable):
            translation = float(detached)
        else:
            detached_list = detached.tolist()
            translation = []
            for i in detached_list[0]:
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


