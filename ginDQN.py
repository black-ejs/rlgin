import random
import torch
import torch.nn as nn
import torch.nn.functional as F
DEVICE = 'cpu' # 'cuda' if torch.cuda.is_available() else 'cpu'

from DQN import DQNAgent
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

    def set_reward(self, ginhand, player):
        """
        Return the reward.
        """
        self.reward = 0
        if ginhand.playing[player.name].playerHand.wins():
            # I won!
            self.reward = self.win_reward
        elif ginhand.currentlyPlaying.playerHand.wins():
            # I lost!
            self.reward = self.loss_reward
        elif ginhand.lifecycle_stage == gin.GinHand.DONE:
            # no winner - not helping
            self.reward = self.no_winner_reward

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
        return cheat_reward

## ###############################################

    def init_input_size(self,params):
        self.input_size = params['input_size']

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
            ginhand.nn_players[self.myPlayer.name]['total_reward'] += reward
            if self.train:
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
                state_old_tensor = torch.tensor(current_state.reshape(self.agent.input_size), 
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
            return
        reward = self.agent.set_reward(ginhand,self.myPlayer)
        ginhand.nn_players[self.myPlayer.name]['total_reward'] += reward
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
            
