import sys
import random
import numpy as np
import pandas as pd
import collections
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

def argmax(l:list):
    max = sys.float_info.min
    index = -1
    for i in range(len(l)):
        if l[i]>max:
            max=l[i]
            index = i
    return index

class DQNAgent(torch.nn.Module):
    MAX_EFFECTIVE_DISCOUNT = 0.009

    def __init__(self, params):
        super().__init__()
        self.params = params

        # nn params
        self.learning_rate = params['learning_rate']        
        self.epsilon = params['noise_epsilon']
        self.gamma = params['gamma']
        self.layer_sizes = params['layer_sizes'] # 'hidden'/interior layers

        self.init_input_size(params)
        self.output_size = params['output_size']

        # persistence
        self.weights_path = params['weights_path']
        self.load_weights = params['load_weights']
        self.load_weights_success = False

        self.reward = 0
        self.optimizer = None
        self.episode_memory = collections.deque(maxlen=1000)
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.posttrain_weights = None

        self.network()

    def init_input_size(self,params):
        self.input_size = params['input_size']

    def create_layers(self):
        pass

    def network(self):
        self.create_layers()

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
        pass
    
    def get_state(self, context_a=None, context_b=None, context_c=None):
        """
        Return the state.
        The state is a numpy array of [self.input_size] values
        derived classes should implement get_state()
             which returns an array of python numbers
        """
        pass

    def as_numpy_array(array):
        return np.asarray(array)

    def set_reward(self, context_a, context_b):
        """
        Return the reward.
        """
        pass

    def remember_episode(self):
        self.memory.extend(self.episode_memory)
        self.episode_memory.clear()

    def remember(self, state, action, reward, next_state, done):
        """
        Store the <state, action, reward, next_state, is_done> tuple in a 
        memory buffer for replay memory.
        """
        self.episode_memory.append((state, action, reward, next_state, done))
        if not reward==0:
            self.distribute_reward_discount(self.episode_memory, reward)

    def distribute_reward_discount(self, memory, undiscounted_reward:float):
        discount = self.gamma
        memory_index = -2
        while discount>DQNAgent.MAX_EFFECTIVE_DISCOUNT and memory_index>0-len(memory): 
            effective_reward = undiscounted_reward*discount
            self.update_reward(memory, memory_index, effective_reward)
            memory_index-=1
            discount *= self.gamma

    def update_reward(self, memory:collections.deque, index:int, addl_reward:float):
        (state, action, reward, next_state, done) = memory[index]
        memory[index] = (state, action, reward+addl_reward, next_state, done)

    #def replay_OLD(self, memory, batch_size):
    #    """
    #    Replay memory.
    #    """
    #    if len(memory) == 0:
    #        return
    #
    #    if len(memory) > batch_size:
    #        minibatch = random.sample(memory, batch_size)
    #    else:
    #        minibatch = memory
    #    for state, action, reward, next_state, done in minibatch:
    #        self.train()
    #        torch.set_grad_enabled(True)
    #        target = reward
    #        next_state_tensor = torch.tensor(np.expand_dims(next_state, 0), dtype=torch.float32).to(DEVICE)
    #        state_tensor      = torch.tensor(np.expand_dims(state,      0), dtype=torch.float32, requires_grad=True).to(DEVICE)
    #        if not done:
    #            target = reward + self.gamma * torch.max(self.forward(next_state_tensor)[0])
    #        output = self.forward(state_tensor)
    #        target_f = output.clone()
    #        if len(target_f.size()) > 1:
    #            target_f[0][np.argmax(action)] = target
    #        else:
    #            target_f[0] = target
    #        target_f.detach()
    #        self.optimizer.zero_grad()
    #        loss = F.mse_loss(output, target_f)
    #        loss.backward()
    #        self.optimizer.step()            

    def replay_new(self, memory, batch_size):
        """
        Replay memory.
        """
        if len(memory) == 0:
            return
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        self.replay_minibatch(minibatch)

    def replay_minibatch(self, minibatch):
        for state, action, reward, next_state, done in minibatch:
            self.train()
            torch.set_grad_enabled(True)
            target = reward
            state_tensor = torch.tensor(np.expand_dims(state, 0), dtype=torch.float32, requires_grad=True).to(DEVICE)
            output = self.forward(state_tensor)
            target_f = output.clone()

            # replace the value of the action taken with the reward
            # the difference between this value (the reward) and the 
            # value supplied will be the back-propagated error
            target_f[np.argmax(action)] = target

            target_f.detach()
            self.optimizer.zero_grad()
            loss = F.mse_loss(output, target_f)
            loss.backward()
            self.optimizer.step()            

    def translatePrediction(self, prediction):
        ##  translation = np.argmax(prediction.detach().cpu().numpy()[0])
        detached = prediction.detach().cpu().numpy()[0]
        translation = float(detached)
        return translation

    def train_episode(self):
        """
        Train the DQN agent on the <state, action, reward, next_state, is_done>
        tuples for the current episode, once the epidoe has completed and the 
        deferred rewards hae been distributed
        """
        return self.replay_minibatch(self.episode_memory)
