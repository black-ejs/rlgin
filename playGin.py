import gin
import time
import random
import math

class playGin:	
	def playHand(strategyOne, strategyTwo, 
					player1_name="player1", player2_name="player2", 
					maxTurns=1000, logWins=True):
		ginhand = gin.GinHand(gin.Player(player1_name), strategyOne, 
				gin.Player(player2_name), strategyTwo)
		return playGin.playThisHand(ginhand, maxTurns, logWins)
	
	def playThisHand(ginhand, maxTurns, logWins):
		ginhand.deal()
		winner = ginhand.play(maxTurns)
		return ginhand
	
# ##############################################	
## Dumbass 0.78% win
class DumbassGinStrategy(gin.GinStrategy):
	def __init__(self):
		gin.GinStrategy.__init__(self)

	def decideDrawSource(self, hand):
		return gin.Draw.DECK
		
	def decideDiscardCard(self, hand):
		return hand.currentlyPlaying.playerHand.card[3]
	
# ##############################################	
## Random 1.48% win
class RandomGinStrategy(gin.GinStrategy): 
	def __init__(self):
		gin.GinStrategy.__init__(self)

	def decideDrawSource(self,hand):
		whichOne=random.random()
		if whichOne<0.5:
			return gin.Draw.DECK
		else:
			return gin.Draw.PILE
		
	def decideDiscardCard(self,hand):
			return hand.currentlyPlaying.playerHand.card[math.floor(random.random()*gin.HAND_SIZE+1)]

# ##############################################	
class OneDecisionGinStrategy(gin.GinStrategy): 
	"""
	Remap "decideDiscardCard()" 
	so that it uses "decideDrawSource()" iteratively
	"""
	def __init__(self):
		gin.GinStrategy.__init__(self)

	## how much do we want this card? 
	## return a value from 0 to 1
	## derived classes override this
	def scoreCandidate(self, sevenCardHand, candidate, ginhand):
		return random.random()

	def decideDrawSource(self,ginhand):
		howYaLikeMe = self.scoreCandidate(ginhand.currentlyPlaying.playerHand, 
											ginhand.discard, ginhand)
		if howYaLikeMe>0.5:
			# print(f"{ginhand.currentlyPlaying.playerHand} accepted {ginhand.discard}")
			return gin.Draw.PILE
		else:
			return gin.Draw.DECK
		
	def decideDiscardCard(self,ginhand):
		## the hand will have 8 cards
		hand = ginhand.currentlyPlaying.playerHand
		worstScore = 500
		worstCard = hand.card[0]

		for c in hand.card:
			cards = []
			for d in hand.card:
				if not d==c:
					cards.append(d)
			score = self.scoreCandidate(gin.Hand(cards),c,ginhand)
			if score < worstScore:
				worstScore = score
				worstCard = c
		 
		# print(f"{ginhand.currentlyPlaying.playerHand} discarded {worstCard}")
		return worstCard
	
## ##############################
class BrainiacGinStrategy(OneDecisionGinStrategy): 
	def __init__(self):
		OneDecisionGinStrategy.__init__(self)

	def scoreCandidate(self, myHand, candidate, ginhand):
		score = gin.Hand.scoreCard(myHand, candidate) + 0.001
		#if score > 0.002:
		#	print(f"{sevenCardHand} trying {candidate}")
		#	print(f"raw score={score}")
		score = score*(100/112) + 1
		score = math.log10(score)/2
		#if score > 0.01:
		#	print(f"final score={score}")
		return score

## ##############################
class BrandiacGinStrategy(BrainiacGinStrategy): 
	def __init__(self, random_percent=50):
		BrainiacGinStrategy.__init__(self)
		self.random_percent=random_percent/100

	def scoreCandidate(self, myHand, candidate, ginhand):
		if random.random() < self.random_percent:
			return random.random()
		return BrainiacGinStrategy.scoreCandidate(self, myHand, candidate, ginhand)

## ##############################
if __name__ == '__main__':	
	num_hands_to_play = 500

	max_duration = -1
	min_duration = 10000000
	wins = 0
	startTime = time.time()

	print("playGin says hello")

	p1="schuyler"
	p2="francesca"

	winMap = {}
	winMap[p1] = 0				
	winMap[p2] = 0		
	winMap['nobody'] = 0		

	for i in range(num_hands_to_play):

		handStartTime = time.time()
		ginhand = playGin.playHand(RandomGinStrategy(), 
								RandomGinStrategy(), 
								player1_name=p1, player2_name=p2)
		duration = time.time() - handStartTime

		if not ginhand.winner == None:
			wins+=1
			print(f"{i:5} WINNER: {ginhand.winner.player.name} {ginhand.winner.playerHand} in {len(ginhand.turns)} turns, {duration:3.2f}s")
			winMap[ginhand.winner.player.name]+=1
		else:
			print(f"{i:5} WINNER: nobody in {len(ginhand.turns)} turns, {duration:3.2f}s")
			
		if duration < min_duration:
			min_duration = duration
		if duration > max_duration:
			max_duration = duration

	duration = time.time() - startTime
	print(f"won {wins} hands out of {num_hands_to_play}"
		  		f" = {(wins/num_hands_to_play)*100:3.2f}%"
		  		f" in {duration*1000:.2f}ms ({(duration/num_hands_to_play)*1000:.2f}ms/hand)"
		  		f" min/max duration(ms): {min_duration*1000:3.2f}/{max_duration*1000:3.2f}")
	print(f"winners: {winMap}")

