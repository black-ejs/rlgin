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
from ginDQNConvFHandOut import ginDQNConvFHandOut

# ******************************
class ginDQNCFHPad(ginDQNConvFHandOut):

    def __init__(self, params):
        super().__init__(params)

    def create_conv_layer(self):
        # one-channel input, two filters, 4x4 kernel
        # no stride, padding of kernel-size-1, no groups, no dilation
        my_padding=[ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE[0]-1,
                 ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE[1]-1]
        self.convo_output_size = self.calc_conv_output_size(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNELS, 
                                            ginDQNConvoFloatPlane.CONVO_OUTPUT_CHANNELS, 
                                            ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE, 
                                            ginDQNConvoFloatPlane.CONVO_INPUT_CHANNEL_SIZE,
                                            padding=my_padding)
        return nn.Conv2d(ginDQNConvoFloatPlane.CONVO_INPUT_CHANNELS,
                         ginDQNConvoFloatPlane.CONVO_OUTPUT_CHANNELS,
                         ginDQNConvoFloatPlane.CONVO_KERNEL_SIZE,
                         padding=my_padding)




