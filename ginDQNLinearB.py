import random
import torch
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import ginDQN
from ginDQNBitPlanes import ginDQNBitPlanes

class ginDQNLinearB(ginDQN.ginDQN):

    def __init__(self, params):
        super().__init__(params)

    def get_state(self, ginhand:(gin.Hand), 
                    player:(gin.Player),
                    pile_substitute:(gin.Card) = None):
        return ginDQNBitPlanes.get_state(ginhand,player,pile_substitute)

    def init_input_size(self,params):
        return ginDQNBitPlanes.calc_input_size()

    


