import torch.nn as nn
import torch.nn.functional as F
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import ginDQN
from ginDQNBitPlanes import ginDQNBitPlanes

class ginDQNConvoBitPlanes(ginDQN.ginDQN):
    CONVO_KERNEL_SIZE = [4,4]
    CONVO_OUTPUT_CHANNELS = 2

    def __init__(self, params):
        super().__init__(params)

    def get_state(self, ginhand:(gin.GinHand), 
                        player:(gin.Player), 
                        pile_substitute:(gin.Card) = None):
        return ginDQNBitPlanes.get_state(ginhand,player,pile_substitute)

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
        self.convo_output_size = self.calc_conv_output_size(ginDQNBitPlanes.CONVO_INPUT_CHANNELS, 
                                            ginDQNConvoBitPlanes.CONVO_OUTPUT_CHANNELS, 
                                            ginDQNConvoBitPlanes.CONVO_KERNEL_SIZE, 
                                            ginDQNBitPlanes.CONVO_INPUT_CHANNEL_SIZE)
        return nn.Conv2d(ginDQNBitPlanes.CONVO_INPUT_CHANNELS,
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
        self.input_size = ginDQNBitPlanes.calc_input_size()

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

