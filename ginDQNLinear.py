import random
import torch
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import ginDQN
import playGin

class ginDQNLinear(ginDQN.DQNAgent):

    def __init__(self, params):
        super().__init__(params)

    def get_state(self, ginhand, player, pile_substitute = None):
        """
        Return the state.
        The state is a numpy array of 53 values, representing:
            - tbe 52 cards in the deck, in 2-to-Ace order within suit, suits are Clubs, Diamonds, Hearts then Spades
                  these 52 values represent the location in the of the card 
                  in the Gin Hand (from the POV of the Player):
                        IN THE OTHER HAND, i.e. the other player 
                               picked it up from the discard pile, 
                               but has not discarded it
                        OUT OF PLAY, i.e. in the DISCARD PILE, 
                               but not the top card available for draw
                        UNKNOWN, i.e. in the DECK or 
                               the other Player's hand
                        the JUST-DISCARDED card, i.e. the one at 
                               the top of the PILE, available for draw
                        IN MY HAND
            - the stage in the players turn, either 
                           0 = deciding the DRAW SOURCE  
                           1 = deciding the DISCARD CARD  
        """
        state = []
        for i in range(self.input_size):
            state.append(self.state_values['UNKNOWN'])

        me = player
        my_hand = ginhand.playing[me].playerHand
        top_of_pile = ginhand.firstPileCard
        for turn in ginhand.turns:

            if turn.draw == None:
                break  # current turn, not yet drawn
            if not turn.draw.source == gin.Draw.PILE:
                state[top_of_pile.toInt()] = self.state_values['OUT_OF_PLAY']
            elif not turn.player == me:
                state[top_of_pile.toInt()] = self.state_values['IN_OTHER_HAND']

            if turn.discard == None:
                break  # current turn, no discard yet
            state[turn.discard.toInt()] = self.state_values['JUST_DISCARDED']
            top_of_pile = turn.discard

        for c in my_hand.card:
            if not c == pile_substitute:
                state[c.toInt()] = self.state_values['IN_MY_HAND']
            else:
                state[top_of_pile.toInt()] = self.state_values['OUT_OF_PLAY']
                state[c.toInt()] = self.state_values['JUST_DISCARDED']

        if pile_substitute == None:
            state[-1] = self.state_values['DECIDE_DRAW_SOURCE']
        else:
            state[-1] = self.state_values['DECIDE_DISCARD_CARD']

        return DQNAgent.as_numpy_array(state)

