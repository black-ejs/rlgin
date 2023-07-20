from collections.abc import Iterable
import torch.nn as nn
import torch.nn.functional as F

from DQN import DQNAgent
import gin

class ginDQN(DQNAgent):

    def __init__(self, params):
        super().__init__(params)

        self.win_reward = params['win_reward']
        self.loss_reward = params['loss_reward']
        self.no_winner_reward = params['no_winner_reward']
          
    ## #####################################################
    ## ###############################################################

    def set_reward(self, ginhand:gin.GinHand, player):
        """
        Return the reward.
        """
        self.reward = 0

        hand_winner, winner_score, is_done = ginhand.ginScore()

        if is_done:
            """
            if ginhand.winner==None:
                ginHand_winner="None"
            else:
                ginHand_winner=ginhand.winner.player.name
            playing = ginhand.playing[player.name]
            otherPlaying = ginhand.otherPlaying(playing)
            print(f"setting reward for {player.name} when hand is done: ")
            print(f"ginhand.winner={ginHand_winner}")
            print(f"{player.name}'s hand={playing.playerHand}")
            print(f"{player.name}'s deadwood={playing.playerHand.deadwood()}")
            print(f"{otherPlaying.player.name}'s hand={otherPlaying.playerHand}")
            print(f"{otherPlaying.player.name}'s deadwood={otherPlaying.playerHand.deadwood()}")
            print(f"ginhand.ginScore() returned: hand_winner={hand_winner.player.name}, winner_score={winner_score}, is_done={is_done} ")
            if not ((ginhand.winner==None) 
                    or (hand_winner.player.name==ginHand_winner)):
                print(f"## ## ## winner mismatch ## ## ##")
            """    
            
            if ginhand.playing[player.name] == hand_winner:
                # I won!
                #self.reward = self.win_reward
                self.reward = winner_score
            elif ginhand.currentlyPlaying.playerHand == hand_winner:
                # I lost!
                # self.reward = self.loss_reward
                self.reward = -winner_score
            else:
                # no winner - not helping
                #self.reward = self.no_winner_reward
                self.reward = -ginhand.playing[player.name].playerHand.deadwood()

            # normalize the reward so that is is between 0 and 1
            # the highest possible score is 10Xgin.
            denom=10*gin.HAND_SIZE+gin.GinHand.GIN_BONUS
            self.reward = round(self.reward*(1/denom),4)

        if (('use_cheat_rewards' in self.params)
                and (self.params['use_cheat_rewards'])):
            self.reward = self.get_cheat_reward(ginhand, player,  self.reward)

        return self.reward

    def get_cheat_reward(self, ginhand:(gin.GinHand), player, normal_reward):
        if not hasattr(self, 'prev_cheat_score'):
            self.prev_cheat_score = 0
        if self.reward > 0:
            return self.reward
        myhand = ginhand.playing[player.name].playerHand
        cards = []
        pretty = myhand.prettyStr().split()
        for cstr in pretty:
            cards.append(gin.Card.fromStr(cstr))
        size=0
        for i in range(1,len(cards)):
            if ((cards[i].rank == cards[i-1].rank+1) and 
                        (cards[i].suit == cards[i-1].suit)):
                size+=1 # run
            if cards[i].rank == cards[i-1].rank:
                size+=1 # match
        cheat_score = float(size)/float(len(cards))
        cheat_reward = cheat_score - self.prev_cheat_score
        if cheat_reward!=0:
            print(f"cheat_reward={cheat_reward}, size={size} hand={myhand.prettyStr()}  prev={self.prev_cheat_score}")
        self.prev_cheat_score = cheat_score
        return cheat_reward

## ###############################################

    def init_input_size(self,params):
        self.input_size = params['input_size']
        if isinstance(self.input_size,Iterable):
            self.input_size = tuple(self.input_size)

    def create_layers(self):
        self.layers = nn.ModuleList(self.create_default_layers(self.input_size,
                                                               self.output_size))

    def create_default_layers(self, prev_layer_size, output_size):
        # Layers
        llayers = []
        for layer_size in self.layer_sizes:
            llayers.append(nn.Linear(prev_layer_size, layer_size))
            prev_layer_size = layer_size
        llayers.append(nn.Linear(prev_layer_size, output_size))
        return llayers

    def forward(self, x):
        # Linear Layers
        for layer in self.layers[:-1]:
            if 'no_relu' in self.params and self.params['no_relu']:
                x = layer(x)
            else:
                x = F.relu(layer(x))
        x = self.layers[-1](x) # last layer
        return x

## ###############################################
## ###############################################
