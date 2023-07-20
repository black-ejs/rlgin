import collections

import gin
import playGin
import DQN
import ginDQN
import ginDQNStrategy

## ###############################################
## ###############################################
## ###############################################
## ###############################################
class ginDQNHandOutStrategy(ginDQNStrategy.ginDQNStrategy):
    def __init__(self,params,agent:(ginDQN)):
        return super().__init__(params, agent)

    # if lowest-value card is the offered discard, choose from the DECK
    # otherwise choose the offered discard, we will subsequently 
    # discard the lowest-value card
    def decideDrawSource(self,ginhand:gin.GinHand):
        score_array = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
        discard_me = DQN.argmax(score_array)
        
        if discard_me == len(score_array)-1:
            return gin.Draw.DECK
        else:
            return gin.Draw.PILE

    def decideDiscardCard(self,ginhand:gin.GinHand):
        score_array = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
        discard_me = DQN.argmax(score_array)

        if discard_me < 0:
            print(f"WARNING: invalid discard index {discard_me} in hand {ginhand.currentlyPlaying.playerHand}")
            return ginhand.currentlyPlaying.playerHand.card[0]
        elif discard_me < len(score_array):
            return ginhand.currentlyPlaying.playerHand.card[discard_me]
        else:
            return ginhand.discard

    def translatePrediction(self, prediction):
        detached = prediction.detach().cpu().numpy()
        if not isinstance(detached, collections.Iterable):
            translation = float(detached)
        else:
            detached_list = detached.tolist()
            translation = []
            for i in detached_list[0]:
                translation.append(float(i))
        return translation

    def learnTurn(self, turn_states, turn_scores, reward, new_state, isDone = False, is_first_turn=False):
        """
        there should be 2 each of states/scores/benchmarks
           - [0] == DrawDecision
           - [1] == DiscardDecision
        """
        if not len(turn_scores)==2 and len(turn_states)==2:
            print("WTF")
        draw_state = turn_states[0]
        draw_score = turn_scores[0]
        discard_state = turn_states[1]
        discard_score = turn_scores[1]

        # store the new data into memory for experience replay
        self.agent.remember(draw_state, draw_score, reward/2, discard_state, False)
        self.agent.remember(discard_state, discard_score, reward/2, new_state, isDone)
        
## ###############################################
## ###############################################
## ###############################################
## ###############################################
class ginHandOutBenchmarkStrategy(playGin.BrainiacGinStrategy):
    def scoreCandidate(self, myHand:gin.Hand, candidate:gin.Card, ginhand:gin.GinHand):
        allCandidates = myHand.card.copy()
        allScores = []
        if not candidate == None:
            allCandidates.append(candidate)
        for c in allCandidates:
            h = allCandidates.copy()
            h.remove(c)
            allScores.append(super().scoreCandidate(gin.Hand(h), c, ginhand))
        return allScores


