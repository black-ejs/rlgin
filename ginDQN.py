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
        The state is a numpy array of 53 values, representing:
            - tbe 52 cards in the deck, in 2-to-Ace order within suit, suits are Clubs, Diamonds, Hearts then Spades
                  these 52 values represent the location in the of the card 
                  in the Gin Hand (from the POV of the Player):
                       -.500 = IN THE OTHER HAND, i.e. the other player 
                               picked it up from the discard pile, 
                               but has not discarded it
                       -.100 = OUT OF PLAY, i.e. in the DISCARD PILE, 
                               but not the top card available for draw
                           0 = unknown, i.e. in the DECK or 
                               the other Player's hand
                        .100 = the JUST-DISCARDED card, i.e. the one at 
                               the top of the PILE, available for draw
                        .500 = in the PLAYER'S HAND
            - the stage in the players turn, either 
                           0 = deciding the DRAW SOURCE  
                           1 = deciding the DISCARD CARD  
        """
        IN_OTHER_HAND = -0.500
        OUT_OF_PLAY = -0.100
        UNKNOWN = 0.0
        JUST_DISCARDED = 0.100
        IN_MY_HAND = 0.500
        DECIDE_DRAW_SOURCE = 0.000
        DECIDE_DISCARD_CARD = 1.000

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
                state[c.toInt()] = JUST_DISCARDED        

        if pile_substitute == None:
            state[-1] = DECIDE_DRAW_SOURCE
        else:
            state[-1] = DECIDE_DISCARD_CARD

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
        self.myPlayer = None
        self.turns = 0
        self.batch_size = params['batch_size']
        self.train = params['train']
        self.pretrain_weights = None
        self.benchmark_scorer = None

    def learnTurn(self, turn_states, turn_actions, reward, new_state, isDone = False, is_first_turn=False):
        if is_first_turn:
            i=0 
            for action in turn_actions:
                old_state = turn_states[i]
                self.agent.remember(old_state, action, reward, new_state, isDone)
                i+=1
            self.agent.replay_new(self.agent.memory, self.batch_size)
        else:
            i=0 
            for action in turn_actions:
                old_state = turn_states[i]
                # train short memory base on the new action and state
                self.agent.train_short_memory(old_state, action, reward, new_state, isDone)
                # store the new data into a long term memory
                self.agent.remember(old_state, action, reward, new_state, isDone)
        #if not self.pretrain_weights==None:
        #    count_diffs = ginDQNStrategy.compare_weights(self.pretrain_weights, 
        #                                            self.agent.state_dict())
        #    if count_diffs == 0:
        #            print(f"** WARNING: weights appear unchanged at turn {self.turns}")

    def startOfTurn(self, ginhand):
        self.myPlayer = ginhand.currentlyPlaying.player
        new_state = self.agent.get_state(ginhand,self.myPlayer)
        ## deal with previous turn
        if not self.turns==0:
            ginhand.turns[-3].turn_scores = self.turn_scores # my previous turn
            ginhand.turns[-3].turn_benchmarks = self.turn_benchmarks
            reward = self.agent.set_reward(ginhand,self.myPlayer)
            ginhand.total_reward += reward
            if self.train:
                self.learnTurn(self.turn_states, self.turn_scores, reward, new_state, 
                                    is_first_turn=(self.turns==1))
        else:
            ginhand.total_reward = 0
        self.turns += 1
        self.turn_scores = []
        self.turn_states = []
        self.turn_benchmarks = []
        
    def scoreCandidate(self, sevenCardHand, candidate, ginhand):
        # perform random actions based on agent.epsilon, or choose the action
        
        current_state = self.agent.get_state(ginhand,self.myPlayer,candidate)
        if random.uniform(0, 1) < self.agent.epsilon:
            score = random.random()
        else:
            # predict action based on the old state
            with torch.no_grad():
                state_old_tensor = torch.tensor(current_state.reshape((1, self.state_size)), 
                                                dtype=torch.float32).to(DEVICE)
                prediction = self.agent(state_old_tensor)
                score = DQNAgent.translatePrediction(prediction)
        self.turn_scores.append(score)
        self.turn_states.append(current_state)
        if not self.benchmark_scorer == None:
            benchmark = self.benchmark_scorer.scoreCandidate(
                                sevenCardHand, candidate, ginhand)
            self.turn_benchmarks.append(benchmark)
        return score
        
    def endOfHand(self, ginhand):
        if self.myPlayer == None:
            # the other player was dealt a winning hand
            # nothing to learn here, except perhaps philosophically
            ginhand.total_reward = 0
            return
        reward = self.agent.set_reward(ginhand,self.myPlayer)
        ginhand.total_reward += reward
        if self.train:
            ## deal with our last turn
            new_state = self.agent.get_state(ginhand,self.myPlayer)
            self.learnTurn(self.turn_states, self.turn_scores, reward, new_state, isDone=True)
        if ginhand.currentlyPlaying.player.name == self.myPlayer.name: 
            ginhand.lastTurn().turn_scores = self.turn_scores
            ginhand.lastTurn().turn_benchmarks = self.turn_benchmarks
        else:
            ginhand.turns[-2].turn_scores = self.turn_scores
            ginhand.turns[-2].turn_benchmarks = self.turn_benchmarks
        
    ## #############################################
    def compare_weights(pretrain_weights, posttrain_weights):
        count_diffs = 0
        for p in pretrain_weights:
            try:
                pre = pretrain_weights[p]
                post = posttrain_weights[p]
                if not (torch.equal(pre, post)):
                    count_diffs += 1
                    print(f"unequal state_dict: ")
                    print(f"(pre) {p}: {pre}")
                    print(f"(post){p}: {post}")
            except RuntimeError as err:
                print(f"error processing element {p}: {err}")
                print 
            
        return count_diffs
            
