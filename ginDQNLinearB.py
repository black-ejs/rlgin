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
        tensor_state = ginDQNBitPlanes.get_state(ginhand,player,pile_substitute)
        # flatten it
        state = []
        for channel in tensor_state:
            for row in channel:
                state.extend(row)
        return  DQNAgent.as_numpy_array(state)

    def init_input_size(self,params):
        plane_sizes = ginDQNBitPlanes.calc_input_size(params)
        rez = 1
        for sz in plane_sizes:
            rez *= sz
        self.input_size=rez


    


