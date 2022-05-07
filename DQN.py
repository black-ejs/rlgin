import random
import numpy as np
import pandas as pd
import collections
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import copy
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

class DQNAgent(torch.nn.Module):
    def __init__(self, params):
        super().__init__()
        self.reward = 0
        self.gamma = 0.99
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = params['learning_rate']        
        self.epsilon = 1
        self.actual = []
        self.input_size = params['input_size']
        self.output_size = params['output_size']
        self.layer_sizes = params['layer_sizes'] # 'hidden'/interior layers
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.weights_path = params['weights_path']
        self.load_weights = params['load_weights']
        self.load_weights_success = False
        self.optimizer = None
        self.posttrain_weights = None
        self.network()
          
    def create_layers_conv(self):
        # Layers
        llayers = []
        llayers.append(self.create_conv_layer())
        # prev_layer_size = self.calc_conv_output_size(1,2,[4,4], self.input_size)
        prev_layer_size = 22
        for layer_size in self.layer_sizes:
            llayers.append(nn.Linear(prev_layer_size, layer_size))
            prev_layer_size = layer_size
        llayers.append(nn.Linear(prev_layer_size, self.output_size))
        self.layers = nn.ModuleList(llayers)

    def create_conv_layer(self):
        # one-channel input, two filters, 4x4 kernel
        # no stride, no padding, no groups, no dilation
        return nn.Conv2d(1,2,4)

    def calc_conv_output_image_size(self, kernel_size, conv_input_size,
                         padding=[0,0], stride=[1,1], dilation=[1,1]):
        H_out = conv_input_size[0] + (2*padding[0]) + (dilation[0]*(kernel_size[0]-1))
        H_out = H_out/stride[0] + 1
        W_out = conv_input_size[1] + (2*padding[1]) + (dilation[1]*(kernel_size[1]-1))
        W_out = W_out/stride[1] + 1
        return (H_out, W_out)
        
    def calc_conv_output_size(self, input_channels, output_channels, 
                        kernel_size, conv_input_size,
                        padding=[0,0], stride=[1,1], dilation=[1,1]):
        conv_image_size = self.calc_conv_output_image_size(kernel_size, conv_input_size,
                                                        padding, stride, dilation)
        return int(conv_image_size[0]*conv_image_size[1]*output_channels)                          

    def network(self):
        self.create_layers_conv()

        # weights
        if self.load_weights:
            if self.posttrain_weights == None:
                state_dict = torch.load(self.weights_path)
                self.model = self.load_state_dict(torch.load(self.weights_path))
            else:
                self.load_state_dict(self.posttrain_weights)
            self.eval()
            state_dict = self.state_dict()
            self.load_weights_success = True

    def forward(self, x):
        # Conv2D layer
        x = self.layers[0](x)
        # x = x.reshape([22])
        # x = x.reshape(1,22)
        x = x.reshape(22)

        # Linear Layers
        for layer in self.layers[1:-1]:
            x = F.relu(layer(x))
        x = self.layers[-1](x) # last layer
        # coco = x.clone()
        # x = F.softmax(x, dim=-1) 
        # x = F.relu(x) 
        return x
    
    def get_state(self, state_package):
        """
        Return the state.
        The state is a numpy array of [self.input_size] values
        derived classes should implement get_state()
             which returns an array of python numbers
        """
        pass

    def as_numpy_array(array):
        return np.asarray(array)

    def set_reward(self, state_package):
        """
        Return the reward.
        """
        pass

    def remember(self, state, action, reward, next_state, done):
        """
        Store the <state, action, reward, next_state, is_done> tuple in a 
        memory buffer for replay memory.
        """
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory, batch_size):
        """
        Replay memory.
        """
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            self.train()
            torch.set_grad_enabled(True)
            target = reward
            next_state_tensor = torch.tensor(np.expand_dims(next_state, 0), dtype=torch.float32).to(DEVICE)
            state_tensor = torch.tensor(np.expand_dims(state, 0), dtype=torch.float32, requires_grad=True).to(DEVICE)
            if not done:
                target = reward + self.gamma * torch.max(self.forward(next_state_tensor)[0])
            output = self.forward(state_tensor)
            target_f = output.clone()
            if len(target_f.size()) > 1:
                target_f[0][np.argmax(action)] = target
            else:
                target_f[0] = target
            target_f.detach()
            self.optimizer.zero_grad()
            loss = F.mse_loss(output, target_f)
            loss.backward()
            self.optimizer.step()            

    def translatePrediction(prediction):
        translation = np.argmax(prediction.detach().cpu().numpy()[0])
        return translation

    def train_short_memory(self, state, action, reward, next_state, done):
        """
        Train the DQN agent on the <state, action, reward, next_state, is_done>
        tuple at the current timestep.
        """
        self.train()
        torch.set_grad_enabled(True)
        target = reward
        next_state_tensor = torch.tensor(
                            next_state.reshape(1,1,self.input_size[0],self.input_size[1]), 
                            dtype=torch.float32).to(DEVICE)
        state_tensor = torch.tensor(
                            state.reshape(1,1,self.input_size[0],self.input_size[1]), 
                            dtype=torch.float32, requires_grad=True).to(DEVICE)
        if not done:
            target = reward + self.gamma * torch.max(self.forward(next_state_tensor))
        output = self.forward(state_tensor)
        target_f = output.clone()
        if len(target_f.size()) > 1:
            target_f[0][np.argmax(action)] = target
        else:
            target_f[0] = target
        target_f.detach()
        self.optimizer.zero_grad()
        loss = F.mse_loss(output, target_f)
        loss.backward()
        self.optimizer.step()