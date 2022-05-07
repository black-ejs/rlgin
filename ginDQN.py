import random
import torch
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
import gin
import playGin

class ginDQNAgent(DQNAgent):

    default_state_values = {'IN_OTHER_HAND': -0.500,
                'OUT_OF_PLAY': -0.100,
                'UNKNOWN': 0.0,
                'JUST_DISCARDED': 0.100,
                'IN_MY_HAND': 0.500,
                'DECIDE_DRAW_SOURCE': 0.000,
                'DECIDE_DISCARD_CARD': 1.000
    }

    def __init__(self, params):
        super().__init__(params)

        self.state_size = params['input_size']
        self.win_reward = params['win_reward']
        self.loss_reward = params['loss_reward']
        self.no_winner_reward = params['no_winner_reward']

        if 'state_values' in params:
            self.state_values=params['state_values']
        else:
            self.state_values=ginDQNAgent.default_state_values
          
    def get_state(self, ginhand:(gin.GinHand), 
                        player:(gin.Player), 
                        pile_substitute:(gin.Card) = None):
        """
        Return the state.
        The state is a 2d numpy array, 4x14 representing:
            - tbe 52 cards in the deck, as 4 rows of 13 values 
              in 2-to-Ace order within suit, the 4 rows are
              Clubs, Diamonds, Hearts then Spades in that order
                  these 52 values represent the location in the of the card 
                  in the Gin Hand (from the POV of the Player):
                        OUT OF PLAY, i.e. in the DISCARD PILE, 
                               but not the top card available for draw
                        UNKNOWN, i.e. in the DECK or 
                               the other Player's hand
                        IN THE OTHER HAND, i.e. the other player 
                               picked it up from the discard pile, 
                               but has not discarded it
                        the JUST-DISCARDED card, i.e. the one at 
                               the top of the PILE, available for draw
                        IN MY HAND
            - the stage in the players turn, as the 14th 
                DECIDE_DRAW_SOURCE = deciding the DRAW SOURCE  
                DECIDE_DISCARD_CARD = deciding the DISCARD CARD  
        """
        decide_val = self.state_values['DECIDE_DISCARD_CARD']
        if (not (ginhand.discard == None)) and (ginhand.discard == pile_substitute):
            decide_val = self.state_values['DECIDE_DRAW_SOURCE']

        state = []

        # initialze to OUT OF PLAY
        for i in range(self.state_size[1]):
            ylist = []
            for j in range(self.state_size[0]-1):
                ylist.append(self.state_values['OUT_OF_PLAY'])
            state.append(ylist)
        # set decision
        for i in range(len(state)):
            state[i].append(decide_val)

        for c in ginhand.deck.undealt:
            self.val2State(c, state, self.state_values['UNKNOWN'])

        me = player
        my_hand = ginhand.playing[me].playerHand

        if ginhand.discard == None:
            if pile_substitute == None:
                print("nothing to select here!")
                return DQNAgent.as_numpy_array(state)
            if not (pile_substitute in my_hand.card):
                print("** DISCARD DECISION WITH CARD NOT IN MY HAND")

        if not (pile_substitute == None):  
            self.val2State(pile_substitute, state, self.state_values['JUST_DISCARDED'])
        elif not (ginhand.discard == None):  # use ginhand.discard
            self.val2State(ginhand.discard, state, self.state_values['JUST_DISCARDED'])

        other_hand = ginhand.notCurrentlyPlaying().playerHand
        if other_hand == my_hand:
            other_hand = ginhand.currentlyPlaying.playerHand # shouldn't happen

        for c in other_hand.card:
            self.val2State(c, state, self.state_values['UNKNOWN'])

        for c in my_hand.card:
            if not c == pile_substitute:
                self.val2State(c, state, self.state_values['IN_MY_HAND'])
        
        ## look for IN_OTHER_HAND (drawn, nevcer discarded)
        cards_opponent_holds = []
        for turn in ginhand.turns:
            if turn.draw == None:
                break  # current turn, not yet drawn
            if turn.player == me:
                continue
            if turn.draw.source == gin.Draw.PILE:
                cards_opponent_holds.append(turn.draw.card)
            if turn.discard == None:
                break  # current turn, no discard yet
            if turn.discard in cards_opponent_holds:
                cards_opponent_holds.remove(turn.discard)
        for c in cards_opponent_holds:
            if len(cards_opponent_holds) > gin.HAND_SIZE:
                print(f"** warning: get_state() finds too many cards in other hand {cards_opponent_holds}")
            self.val2State(c, state, self.state_values['IN_OTHER_HAND'])

        return DQNAgent.as_numpy_array([state])

    def val2State(self, c:(gin.Card), state:(list), val:(float)):
        state[int(c.toInt()/13)][c.toInt()%13] = val

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

    def learnTurn(self, turn_states, turn_scores, reward, new_state, isDone = False, is_first_turn=False):
        if (len(turn_scores)>1):
            discard_reward = float(reward/(len(turn_scores)-1))
        else:
            discard_reward = 0
        i=0
        for score in turn_scores:
            old_state = turn_states[i]
            if i==0:
                sub_reward = reward
            else:
                sub_reward = discard_reward
            # store the new data into a long term memory
            if not is_first_turn:
                # train short memory base on the new action and state
                self.agent.train_short_memory(old_state, score, sub_reward, new_state, isDone)
            self.agent.remember(old_state, score, sub_reward, new_state, isDone)
            i+=1
        if is_first_turn:
            self.agent.replay_new(self.agent.memory, self.batch_size)
        #if not self.pretrain_weights==None:
        #    count_diffs = ginDQNStrategy.compare_weights(self.pretrain_weights, 
        #                                            self.agent.state_dict())
        #    if count_diffs == 0:
        #            print(f"** WARNING: weights appear unchanged at turn {self.turns}")

    def startOfTurn(self, ginhand:(gin.GinHand)):
        self.myPlayer = ginhand.currentlyPlaying.player
        new_state = self.agent.get_state(ginhand,self.myPlayer)
        ## deal with previous turn
        if not self.turns==0:
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
        ginhand.lastTurn().turn_scores = self.turn_scores 
        ginhand.lastTurn().turn_benchmarks = self.turn_benchmarks
        
    def scoreCandidate(self, sevenCardHand, candidate, ginhand):
        # perform random actions based on agent.epsilon, or choose the action
        current_state = self.agent.get_state(ginhand,self.myPlayer,candidate)
        is_random = False
        if random.uniform(0, 1) < self.agent.epsilon:
            score = random.random()
            is_random = True
        else:
            # predict action based on the old state
            with torch.no_grad():
                state_old_tensor = torch.tensor(current_state.reshape((1, 1, self.state_size[0], self.state_size[1])), 
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
            
