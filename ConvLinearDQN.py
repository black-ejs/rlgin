import collections

import numpy as np
import torch 
import torch.nn as nn
import torch.nn.functional as F

import gin
import ginDQN
from FloatPlaneState import FloatPlaneState

# ******************************
class ConvLinearDQN(ginDQN.ginDQN):

    CONVO_INPUT_CHANNELS = FloatPlaneState.OUTPUT_PLANES
    CONVO_INPUT_CHANNEL_SIZE = FloatPlaneState.OUTPUT_PLANE_SIZE
    CONVO_BATCHSIZE = 1
    CONVO_KERNEL_SIZE = [4,4]
    CONVO_OUTPUT_CHANNELS = 2

    def __init__(self, params):
        super().__init__(params)
        self.forward_invocation_count = 0
        self.forward_action_count = 0
        self.zero_invocation_count = 0
        self.zero_forward_count = 0

    def create_layers(self):
        # Layers
        llayers = []
        llayers.append(self.create_conv_layer())

        # self.convo_output_size has now been set
        prev_layer_size = self.convo_output_size + self.input_size[2]*self.input_size[3]
        llayers.extend(self.create_default_layers(prev_layer_size,self.output_size))
        
        self.layers = nn.ModuleList(llayers)

    def create_conv_layer(self):
        # one-channel input, two filters, 4x4 kernel
        # no stride, padding of kernel-size-1, no groups, no dilation
        my_padding=[self.CONVO_KERNEL_SIZE[0]-1,
                 self.CONVO_KERNEL_SIZE[1]-1]
        if 'conv_layer_kernels'  in self.params:
            convo_output_channels =  self.params['conv_layer_kernels']
        else:
            convo_output_channels =  self.CONVO_OUTPUT_CHANNELS
        self.convo_output_size = self.calc_conv_output_size(self.CONVO_INPUT_CHANNELS, 
                                            convo_output_channels, 
                                            self.CONVO_KERNEL_SIZE, 
                                            self.CONVO_INPUT_CHANNEL_SIZE,
                                            padding=my_padding)
        return nn.Conv2d(self.CONVO_INPUT_CHANNELS,
                         convo_output_channels,
                         self.CONVO_KERNEL_SIZE,
                         padding=my_padding)
    
    def init_input_size(self,params):
        self.input_size = []
        self.input_size.append(self.CONVO_BATCHSIZE)
        self.input_size.append(self.CONVO_INPUT_CHANNELS)
        self.input_size.extend(self.CONVO_INPUT_CHANNEL_SIZE)

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
    ## ###############################################
    ## ###############################################
    ## ###############################################
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
## ###############################################
