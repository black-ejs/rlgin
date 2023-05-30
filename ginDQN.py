from collections.abc import Iterable
import random
import torch
import torch.nn as nn
import torch.nn.functional as F

from DQN import DQNAgent
from DQN import DEVICE
import gin
import playGin

class ginDQN(DQNAgent):

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

        self.win_reward = params['win_reward']
        self.loss_reward = params['loss_reward']
        self.no_winner_reward = params['no_winner_reward']

        if 'state_values' in params:
            self.state_values=params['state_values']
        else:
            self.state_values=ginDQN.default_state_values
          
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
        # Layers
        llayers = []
        prev_layer_size = self.input_size
        for layer_size in self.layer_sizes:
            llayers.append(nn.Linear(prev_layer_size, layer_size))
            prev_layer_size = layer_size
        llayers.append(nn.Linear(prev_layer_size, self.output_size))
        self.layers = nn.ModuleList(llayers)

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
## ###############################################
class ginDQNStrategy(playGin.OneDecisionGinStrategy):
    def __init__(self,params,agent:(ginDQN)):
        playGin.OneDecisionGinStrategy.__init__(self)

        self.epsilon_decay_linear = params['epsilon_decay_linear']
        self.agent = agent
        self.myPlayer = None
        self.turns = 0
        self.batch_size = params['batch_size']
        self.train_mode = params['train']
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
            if not reward == 0:
                print(f"=== WARNING: non-zero reward={reward} before end-of-hand: {ginhand}")
            ginhand.nn_players[self.myPlayer.name]['total_reward'] += reward
            if self.train_mode:
                self.learnTurn(self.turn_states, self.turn_scores, reward, new_state, 
                                    is_first_turn=(self.turns==1))
        else:
            ginhand.nn_players[self.myPlayer.name]['total_reward'] = 0
        self.turns += 1
        self.turn_scores = []
        self.turn_states = []
        self.turn_benchmarks = []
        ginhand.lastTurn().turn_scores = self.turn_scores 
        ginhand.lastTurn().turn_benchmarks = self.turn_benchmarks
        
    def get_random_score(self):
        if self.agent.output_size < 2:
            return random.random()
        rez = []
        for i in range(self.agent.output_size):
            rez.append(random.random())
        return rez

    def scoreCandidate(self, myHand, candidate, ginhand):
        # perform random actions based on agent.epsilon, or choose the action
        current_state = self.agent.get_state(ginhand,self.myPlayer,candidate)
        is_random = False
        score = None
        if random.uniform(0, 1) < self.agent.epsilon:
            score = self.get_random_score()
            is_random = True
        else:
            # predict action based on the old state
            with torch.no_grad():
                state_old_tensor = torch.tensor(current_state.reshape(self.agent.input_size), 
                                                dtype=torch.float32).to(DEVICE)
                prediction = self.agent(state_old_tensor)
                score = self.translatePrediction(prediction)
        self.turn_scores.append(score)
        self.turn_states.append(current_state)
        if (not self.benchmark_scorer == None): ## and (not candidate==None):
            benchmark = self.benchmark_scorer.scoreCandidate(
                                myHand, candidate, ginhand)
            self.turn_benchmarks.append(benchmark)
        return score
        
    def endOfHand(self, ginhand):
        if self.myPlayer == None:
            # the other player was dealt a winning hand
            # nothing to learn here, except perhaps philosophically
            # since we didn't make any decisions
            return
        reward = self.agent.set_reward(ginhand,self.myPlayer)
        #if reward == 0:
        #    print(f"=== WARNING: zero reward={reward} at end-of-hand: {ginhand}")
        #else:
        #    dummy=-1
        ginhand.nn_players[self.myPlayer.name]['total_reward'] += reward
        if self.train_mode:
            ## deal with our final turn
            new_state = self.agent.get_state(ginhand,self.myPlayer)
            self.learnTurn(self.turn_states, self.turn_scores, reward, new_state, isDone=True)
            self.agent.train_episode()
            self.agent.remember_episode()
            
        if ginhand.currentlyPlaying.player.name == self.myPlayer.name: 
            ginhand.lastTurn().turn_scores = self.turn_scores
            ginhand.lastTurn().turn_benchmarks = self.turn_benchmarks
        else:
            ginhand.turns[-2].turn_scores = self.turn_scores
            ginhand.turns[-2].turn_benchmarks = self.turn_benchmarks

        
    ## #############################################
    def compare_weights(pretrain_weights, posttrain_weights, verbose=False):
        count_diffs = 0
        for p in pretrain_weights:
            try:
                pre = pretrain_weights[p]
                post = posttrain_weights[p]
                if not (torch.equal(pre, post)):
                    count_diffs += 1
                    if verbose:
                        print(f"unequal state_dict: ")
                        print(f"(pre) {p}: {pre}")
                        print(f"(post){p}: {post}")
            except RuntimeError as err:
                if verbose:
                    print(f"error processing element {p}: {err}")
                    print 
                break
            
        return count_diffs
            
