from collections.abc import Iterable
import random
import torch
import torch.nn as nn
import torch.nn.functional as F 

from DQN import DEVICE
import gin
import ginDQN

## ###############################################
## ###############################################
## ###############################################
class ginDQNStrategy(gin.GinStrategy):
    def __init__(self,params,agent:(ginDQN)):

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
            return (random.random()-0.5)*2
        rez = []
        for i in range(self.agent.output_size):
            rez.append((random.random()-0.5)*2)
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
            # predict action based on the state
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
            
