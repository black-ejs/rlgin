import random
import torch
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import playGin

class ginDQNAgent(DQNAgent):
    def __init__(self, params):
        super().__init__(params)

        self.state_size = params['input_size']
        self.win_reward = params['win_reward']
        self.loss_reward = params['loss_reward']
        self.no_winner_reward = params['no_winner_reward']
          
    def get_state(self, ginhand, player, pile_substitute = None):
        """
        Return the state.
        The state is a numpy array of 52 values, representing:
            - tbe 52 cards in the deck, in 2-to-Ace order within suit, suits are Clubs, Diamonds, Hearts then Spades
                  these 52 values represent the location in the of the card 
                  in the Gin Hand (from the POV of the Player):
                        -500 = IN THE OTHER HAND, i.e. the other player 
                               picked it up from the discard pile, 
                               but has not discarded it
                        -100 = OUT OF PLAY, i.e. in the DISCARD PILE, 
                               but not the top card available for draw
                           0 = unknown, i.e. in the DECK or 
                               the other Player's hand
                          10 = the JUST-DISCARDED card, i.e. the one at 
                               the top of the PILE, available for draw
                         100 = in the PLAYER'S HAND

        """
        IN_OTHER_HAND = -500
        OUT_OF_PLAY = -100
        UNKNOWN = 0
        JUST_DISCARDED = 10
        IN_MY_HAND = 100

        state = []
        for i in range(self.state_size):
            state.append(UNKNOWN)

        me = player
        my_hand = ginhand.playing[me].playerHand
        top_of_pile = ginhand.firstPileCard
        for turn in ginhand.turns:

            if turn.draw == None:
                break  # current turn, not yet drawn
            if not turn.draw.source == gin.Draw.PILE:
                state[top_of_pile.toInt()] = OUT_OF_PLAY
            elif not turn.player == me:
                state[top_of_pile.toInt()] = IN_OTHER_HAND

            if turn.discard == None:
                break  # current turn, no discard yet
            state[turn.discard.toInt()] = JUST_DISCARDED
            top_of_pile = turn.discard

        for c in my_hand.card:
            if not c == pile_substitute:
                state[c.toInt()] = IN_MY_HAND
            else:
                state[top_of_pile.toInt()] = OUT_OF_PLAY
                state[c] = JUST_DISCARDED        

        return DQNAgent.as_numpy_array(state)

    def set_reward(self, ginhand, player):
        """
        Return the reward.
        """
        self.reward = 0
        if ginhand.playing[player].playerHand.wins():
            # I won!
            self.reward = self.win_reward
        elif ginhand.currentlyPlaying.playerHand.wins():
            # I lost!
            self.reward = self.loss_reward
        elif ginhand.lifecycle_stage == gin.GinHand.DONE:
            # no winner - not helping
            self.reward = self.no_winner_reward

        return self.reward

## ###############################################
## ###############################################
## ###############################################
## ###############################################
class ginDQNStrategy(playGin.OneDecisionGinStrategy):
    def __init__(self,params,agent):
        playGin.OneDecisionGinStrategy.__init__(self)

        self.epsilon_decay_linear = params['epsilon_decay_linear']
        self.state_size = params['input_size']
        self.agent = agent
        self.old_state = None
        self.myPlayer = None
        self.turns = 0
        self.batch_size = params['batch_size']

    def learnTurn(self, old_state, turn_actions, reward, new_state, isDone = False, is_first_turn=False):
        if is_first_turn: 
            for action in turn_actions:
                self.agent.remember(old_state, action, reward, new_state, isDone)
            self.agent.replay_new(self.agent.memory, self.batch_size)
        else:
            if self.agent.train:
                for action in turn_actions:
                    # train short memory base on the new action and state
                    self.agent.train_short_memory(old_state, action, reward, new_state, isDone)
                    # store the new data into a long term memory
                    self.agent.remember(old_state, action, reward, new_state, isDone)

    def startOfTurn(self, ginhand):
        self.myPlayer = ginhand.currentlyPlaying.player
        new_state = self.agent.get_state(ginhand,self.myPlayer)
        if not self.turns==0:
            # set reward for the new state
            reward = self.agent.set_reward(ginhand,self.myPlayer)
            self.learnTurn(self.old_state, self.turn_scores, reward, new_state, 
                                is_first_turn=(self.turns==1))
            ginhand.turns[-3].turn_scores = self.turn_scores
        self.old_state = new_state
        self.turns += 1
        self.turn_scores = []
        
    def scoreCandidate(self, sevenCardHand, candidate, ginhand):
        # perform random actions based on agent.epsilon, or choose the action
        
        if random.uniform(0, 1) < self.agent.epsilon:
            score = random.random()
        else:
            # predict action based on the old state
            with torch.no_grad():
                state_old_tensor = torch.tensor(self.old_state.reshape((1, self.state_size)), 
                                                dtype=torch.float32).to(DEVICE)
                prediction = self.agent(state_old_tensor)
                score = DQNAgent.translatePrediction(prediction)
        self.turn_scores.append(score)
        return score
        
    def endOfHand(self, ginhand):
        if self.myPlayer == None:
            # the other player was dealt a winning hand
            # nothing to learn here, except perhaps philosophically
            return
        ## deal with our last turn
        new_state = self.agent.get_state(ginhand,self.myPlayer)
        reward = self.agent.set_reward(ginhand,self.myPlayer)
        self.learnTurn(self.old_state, self.turn_scores, reward, new_state, isDone=True)
        if ginhand.currentlyPlaying.player.name == self.myPlayer.name: 
            ginhand.lastTurn().turn_scores = self.turn_scores
        else:
            ginhand.turns[-2].turn_scores = self.turn_scores
        
            
