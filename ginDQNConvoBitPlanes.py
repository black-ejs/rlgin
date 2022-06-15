import random
import torch
import torch.nn as nn
import torch.nn.functional as F
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import ginDQN
import playGin

class ginDQNConvoBitPlanes(ginDQN.ginDQN):
    CONVO_INPUT_CHANNELS = 6
    CONVO_INPUT_CHANNEL_SIZE = [gin.NUM_SUITS, gin.NUM_RANKS]
    CONVO_BATCHSIZE = 1
    CONVO_KERNEL_SIZE = [4,4]
    CONVO_OUTPUT_CHANNELS = 2

    def __init__(self, params):
        super().__init__(params)

    def create_state_channel(self):
        channel = []
        # initialze to OUT OF PLAY
        for i in range(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNEL_SIZE[0]):
            ylist = []
            for j in range(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNEL_SIZE[1]):
                ylist.append(0)
            channel.append(ylist)
        return channel

    def get_state(self, ginhand:(gin.GinHand), 
                        player:(gin.Player), 
                        pile_substitute:(gin.Card) = None):

        my_hand_channel = self.create_state_channel()
        just_discarded_channel = self.create_state_channel()
        unknown_channel = self.create_state_channel()
        other_hand_channel = self.create_state_channel()
        out_of_play_channel = self.create_state_channel()
        decision_channel = self.create_state_channel()
        state = []
        state.append(my_hand_channel)
        state.append(just_discarded_channel)
        state.append(other_hand_channel)
        state.append(unknown_channel)
        state.append(out_of_play_channel)
        state.append(decision_channel)

        if (not (ginhand.discard == None)) and (ginhand.discard == pile_substitute):
            # deciding the DRAW source
            for dc in decision_channel:
                dc[0]=1 

        # initialze OUT OF PLAY
        for i in range(len(out_of_play_channel)):
            for j in range(len(out_of_play_channel[0])):
                out_of_play_channel[i][j]=1

        for c in ginhand.deck.undealt:
            self.setState(c, unknown_channel, out_of_play_channel)

        me = player
        my_hand = ginhand.playing[me.name].playerHand

        if ginhand.discard == None:
            if pile_substitute == None:
                print("nothing to select here!")
                return DQNAgent.as_numpy_array([out_of_play_channel])
            if not (pile_substitute in my_hand.card):
                print("** DISCARD DECISION WITH CARD NOT IN MY HAND")

        if not (pile_substitute == None):  
            self.setState(pile_substitute, just_discarded_channel, out_of_play_channel)
        elif not (ginhand.discard == None):  # use ginhand.discard
            self.setState(ginhand.discard, just_discarded_channel, out_of_play_channel)

        other_hand = ginhand.notCurrentlyPlaying().playerHand
        if other_hand == my_hand:
            other_hand = ginhand.currentlyPlaying.playerHand # shouldn't happen
        for c in other_hand.card:
            self.setState(c, unknown_channel, out_of_play_channel)

        for c in my_hand.card:
            if not c == pile_substitute:
                self.setState(c, my_hand_channel, out_of_play_channel)
        
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
                self.setState(c, other_hand_channel, out_of_play_channel)

        #return DQNAgent.as_numpy_array([state])
        return DQNAgent.as_numpy_array(state)

    def setState(self, c:(gin.Card), state:(list), oopc:(list)):
        state[int(c.toInt()/13)][c.toInt()%13] = 1
        oopc[int(c.toInt()/13)][c.toInt()%13] = 0

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

    def create_conv_layer(self):
        # one-channel input, two filters, 4x4 kernel
        # no stride, no padding, no groups, no dilation
        self.convo_output_size = self.calc_conv_output_size(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNELS, 
                                            ginDQNConvoBitPlanes.CONVO_OUTPUT_CHANNELS, 
                                            ginDQNConvoBitPlanes.CONVO_KERNEL_SIZE, 
                                            ginDQNConvoBitPlanes.CONVO_INPUT_CHANNEL_SIZE)
        return nn.Conv2d(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNELS,
                         ginDQNConvoBitPlanes.CONVO_OUTPUT_CHANNELS,
                         ginDQNConvoBitPlanes.CONVO_KERNEL_SIZE)

    def calc_conv_output_image_size(self, kernel_size, conv_input_size,
                         padding=[0,0], stride=[1,1], dilation=[1,1]):
        H_out = conv_input_size[0] + (2*padding[0]) - (dilation[0]*(kernel_size[0]-1)) - 1
        H_out = H_out/stride[0] + 1
        W_out = conv_input_size[1] + (2*padding[1]) - (dilation[1]*(kernel_size[1]-1)) - 1
        W_out = W_out/stride[1] + 1
        return (H_out, W_out)
        
    def calc_conv_output_size(self, input_channels, output_channels, 
                        kernel_size, conv_input_size,
                        padding=[0,0], stride=[1,1], dilation=[1,1]):
        conv_image_size = self.calc_conv_output_image_size(kernel_size, conv_input_size,
                                                        padding, stride, dilation)
        return int(conv_image_size[0]*conv_image_size[1]*output_channels)                          

    ## ###############################################

    def init_input_size(self,params):
        self.input_size = []
        self.input_size.append(ginDQNConvoBitPlanes.CONVO_BATCHSIZE)
        self.input_size.append(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNELS)
        self.input_size.extend(ginDQNConvoBitPlanes.CONVO_INPUT_CHANNEL_SIZE)

    def forward(self, x):
        # Conv2D layer
        x = self.layers[0](x)
        x = x.reshape(self.convo_output_size)  ####### YEECH #####

        # Linear Layers
        for layer in self.layers[1:-1]:
            if 'no_relu' in self.params and self.params['no_relu']:
                x = layer(x)
            else:
                x = F.relu(layer(x))
        x = self.layers[-1](x) # last layer
        return x

