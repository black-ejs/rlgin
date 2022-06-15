import random
import torch
import torch.nn as nn
import torch.nn.functional as F
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import ginDQN
import playGin

class ginDQNConvoFloatPlane(ginDQN.ginDQN):
    CONVO_INPUT_CHANNELS = 1
    CONVO_INPUT_CHANNEL_SIZE = [gin.NUM_SUITS, gin.NUM_RANKS + 1]
    CONVO_BATCHSIZE = 1
    CONVO_KERNEL_SIZE = [4,4]
    CONVO_OUTPUT_CHANNELS = 2

    def __init__(self, params):
        super().__init__(params)

    def init_input_size(self,params):
        self.input_size = []
        self.input_size.append(ginDQNConvoFloatPlane.CONVO_BATCHSIZE)
        self.input_size.append(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNELS)
        self.input_size.extend(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNEL_SIZE)

    def create_layers(self):
        # Layers
        llayers = []
        llayers.append(self.create_conv_layer())
        prev_layer_size = self.convo_output_size
        for layer_size in self.layer_sizes:
            llayers.append(nn.Linear(prev_layer_size, layer_size))
            prev_layer_size = layer_size
        llayers.append(nn.Linear(prev_layer_size, self.output_size))
        self.layers = nn.ModuleList(llayers)

    def forward(self, x):
        # Conv2D layer
        x = self.layers[0](x)
        x = x.reshape(self.convo_output_size)  

        # Linear Layers
        for layer in self.layers[1:-1]:
            if 'no_relu' in self.params and self.params['no_relu']:
                x = layer(x)
            else:
                x = F.relu(layer(x))
        x = self.layers[-1](x) # last layer
        return x

    def get_state(self, ginhand:(gin.GinHand), 
                         player:(gin.Player), 
                         pile_substitute:(gin.Card) = None):

        decide_val = self.state_values['DECIDE_DISCARD_CARD']
        if (not (ginhand.discard == None)) and (ginhand.discard == pile_substitute):
            decide_val = self.state_values['DECIDE_DRAW_SOURCE']
 
        state = []
 
        # initialze to OUT OF PLAY
        for i in range(self.input_size[-2]):
            ylist = []
            for j in range(self.input_size[-1]-1):
                ylist.append(self.state_values['OUT_OF_PLAY'])
            state.append(ylist)

        # set decision
        for i in range(len(state)):
            state[i].append(decide_val)

        for c in ginhand.deck.undealt:
            self.val2State(c, state, self.state_values['UNKNOWN'])
        
        me = player
        my_hand = ginhand.playing[me.name].playerHand

        if ginhand.discard == None:
            if pile_substitute == None:
                print("nothing to select here!")
                return DQNAgent.as_numpy_array([state])
            if not (pile_substitute in my_hand.card):
                print("** DISCARD DECISION WITH CARD NOT IN MY HAND")
 
        if not (pile_substitute == None):  
            self.val2State(pile_substitute, state, self.state_values['JUST_DISCARDED'])
        elif not (ginhand.discard == None):  # use ginhand.discard
            self.val2State(ginhand.discard, state, self.state_values['JUST_DISCARDED'])
 
        other_hand = ginhand.notCurrentlyPlaying().playerHand
        if other_hand == my_hand:
            other_hand = ginhand.currentlyPlaying.playerHand # shouldn't happen
        for c in other_hand.card:
            self.val2State(c, state, self.state_values['UNKNOWN'])
 
        for c in my_hand.card:
            if not c == pile_substitute:
                self.val2State(c, state, self.state_values['IN_MY_HAND'])
         
        ## look for IN_OTHER_HAND (drawn, never discarded)
        cards_opponent_holds = []
        for turn in ginhand.turns:
            if turn.draw == None:
                break  # current turn, not yet drawn
            if turn.player == me:
                continue
            if turn.draw.source == gin.Draw.PILE:
                cards_opponent_holds.append(turn.draw.card)
            if turn.discard == None:
                break  # current turn, no discard yet
            if turn.discard in cards_opponent_holds:
                cards_opponent_holds.remove(turn.discard)
        for c in cards_opponent_holds:
            if len(cards_opponent_holds) > gin.HAND_SIZE:
                print(f"** warning: get_state() finds too many cards in other hand {cards_opponent_holds}")
            self.val2State(c, state, self.state_values['IN_OTHER_HAND'])
 
        return DQNAgent.as_numpy_array([state])
 
    def val2State(self, c:(gin.Card), state:(list), val:(float)):
        state[int(c.toInt()/13)][c.toInt()%13] = val
 
    def create_conv_layer(self):
        # one-channel input, two filters, 4x4 kernel
        # no stride, no padding, no groups, no dilation
        self.convo_output_size = self.calc_conv_output_size(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNELS, 
                                            ginDQNConvoFloatPlane.CONVO_OUTPUT_CHANNELS, 
                                            ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE, 
                                            ginDQNConvoFloatPlane.CONVO_INPUT_CHANNEL_SIZE)
        return nn.Conv2d(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNELS,
                         ginDQNConvoFloatPlane.CONVO_OUTPUT_CHANNELS,
                         ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE)

    def calc_conv_output_image_size(self, kernel_size, conv_input_size,
                         padding=[0,0], stride=[1,1], dilation=[1,1]):
        H_out = conv_input_size[0] + (2*padding[0]) - (dilation[0]*(kernel_size[0]-1)) - 1
        H_out = H_out/stride[0] + 1
        W_out = conv_input_size[1] + (2*padding[1]) - (dilation[1]*(kernel_size[1]-1)) - 1
        W_out = W_out/stride[1] + 1
        return (H_out, W_out)
        
    def calc_conv_output_size(self, input_channels, output_channels, 
                        kernel_size, conv_input_size, groups=None,
                        padding=[0,0], stride=[1,1], dilation=[1,1]):
        if groups == None:
            groups = input_channels
        conv_image_size = self.calc_conv_output_image_size(kernel_size, conv_input_size,
                                                        padding, stride, dilation)
        return int(conv_image_size[0]*conv_image_size[1]*output_channels*groups)                          

    ## ###############################################

