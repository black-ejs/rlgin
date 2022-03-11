import gin
import time
import random
import math
import argparse
import distutils.util

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
		score = BrainiacGinStrategy.scoreCard(myHand, candidate) + 0.001
		#if score > 0.002:
		#       print(f"{sevenCardHand} trying {candidate}")
		#       print(f"raw score={score}")
		score = score*(100/152) + 1
		score = math.log10(score)/2
		#if score > 0.01:
		#       print(f"final score={score}")
		return score

	def scoreCard(hand,c):
		match = False
		run = False
		match4 = False
		run4 = False

        # check match
		neighbors = []
		matchcount = 0
		for s in range(gin.NUM_SUITS):
			if not s==c.suit:
				neighbors.append(gin.Card(c.rank,s))
		for n in neighbors:
			if hand.contains(n):
				matchcount+=1
		if matchcount>1:
			match = True
			if matchcount>2:
				match4 = True

        # check run
		neighbors = []
		runcount = 0
		if c.rank>0:
			leftNeighbor=gin.Card(c.rank-1,c.suit)
			if hand.contains(leftNeighbor):
				runcount+=1
				if c.rank>1:
					leftNeighbor2=gin.Card(c.rank-2,c.suit)
					if hand.contains(leftNeighbor2):
						runcount+=1                    
		if c.rank<gin.NUM_RANKS-1:
			rightNeighbor=gin.Card(c.rank+1,c.suit)
			if hand.contains(rightNeighbor):
				runcount+=1
				if c.rank<gin.NUM_RANKS-2:
					rightNeighbor2=gin.Card(c.rank+2,c.suit)
					if hand.contains(rightNeighbor2):
						runcount+=1
		if runcount>1:
			run = True
			if runcount>2:
				run4 = True

		score = runcount + matchcount
		if match or run:
			score += 50
		if match4 or run4:
			score += 100
		return score						

## ##############################
class BrandiacGinStrategy(BrainiacGinStrategy): 
	def __init__(self, random_percent=0.1):
		BrainiacGinStrategy.__init__(self)
		self.random_percent=random_percent/100

	def scoreCandidate(self, myHand, candidate, ginhand):
		if random.random() < self.random_percent:
			return random.random()
		return BrainiacGinStrategy.scoreCandidate(self, myHand, candidate, ginhand)

## ##############################
## ##############################
## command-line and reporting support
## ##############################
def play(num_hands_to_play: int =500, 
			strategy1: str ="b", 
			strategy2: str ="r", 
			name1: str ="player1", 
			name2: str ="player2",
			show_card_counts: bool =False):

	max_duration = -1
	min_duration = 10000000
	wins = 0
	startTime = time.time()

	print("playGin says hello")

	winMap = {}
	winMap[name1] = 0				
	winMap[name2] = 0		
	winMap['nobody'] = 0		
 
	card_counts = []
	for i in range(52):
		card_counts.append(0)

	_strategy1 = get_strategy(strategy1)
	_strategy2 = get_strategy(strategy2)

	for i in range(num_hands_to_play):

		handStartTime = time.time()
		ginhand = playGin.playHand(_strategy1, 
								_strategy2, 
								player1_name=name1, 
								player2_name=name2)
		duration = time.time() - handStartTime

		if not ginhand.winner == None:
			wins+=1
			print(f"{i:5} WINNER: {ginhand.winner.player.name} {ginhand.winner.playerHand.prettyStr()} in {len(ginhand.turns)} turns, {duration:3.2f}s")
			winMap[ginhand.winner.player.name]+=1
			for card in ginhand.winner.playerHand.card:
				card_counts[card.toInt()]+=1
		else:
			print(f"{i:5} WINNER: nobody in {len(ginhand.turns)} turns, {duration:3.2f}s")
			winMap['nobody']+=1
			
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
	if (show_card_counts):
		for i in range(len(card_counts)):
			print(f'{gin.Card.fromInt(i)}: {card_counts[i]}')

## ############################################################
_strategies = { 'B': BrainiacGinStrategy(), 
				'R': RandomGinStrategy(), 
				'D': DumbassGinStrategy(),
				'BR': BrandiacGinStrategy(10)
 			}
def get_strategy(key: str):
	key = key.upper().strip()
	if len(key) > 1:
		if key[0:2] == 'BR':
			if len(key)>2:
				random_percent=int(key[2:])
			else:
				random_percent=10
			return BrandiacGinStrategy(random_percent)
	return _strategies[key]

## ##############################
if __name__ == '__main__':	

	strategy_help = "(r=random, d=dumbass, b=brainiac, brNN=brandiac with NN percent random)"

	parser = argparse.ArgumentParser()
	parser.add_argument('num_hands_to_play',
                    default=500, type=int,
                    nargs='?', help='number of hands to play ' + strategy_help)
	parser.add_argument('strategy1',
                    default='b', type=str,
                    nargs='?', help='the strategy for the first player' + strategy_help)
	parser.add_argument('name1',
                    default='player1', type=str,
                    nargs='?', help='the name for the first player')
	parser.add_argument('strategy2',
                    default='b', type=str,
                    nargs='?', help='the strategy for the second player' + strategy_help)
	parser.add_argument('name2',
                    default='player2', type=str,
                    nargs='?', help='the name for the second player')
	#parser.add_argument('--feature', dest='feature', default=False, action='store_true')				
	parser.add_argument('show_card_counts',
                    default='False', 
					type=str,
					# action=bool(),
					# action=bool,
					# type=bool,
					# action=distutils.util.strtobool,
					# action=lambda x:bool(distutils.util.strtobool(x)),
					# action=argparse.BooleanOptionalAction, 
					#action='store_true',
                    nargs='?', 
					help='show frequency counts of cards in winning hands')
	args = parser.parse_args()

	if not args.show_card_counts == 'False':
		show_card_counts = distutils.util.strtobool(args.show_card_counts)
	else:
		show_card_counts = False

	play(num_hands_to_play=args.num_hands_to_play, 
			strategy1=args.strategy1, 
			strategy2=args.strategy2, 
			name1=args.name1, 
			name2=args.name2,
			show_card_counts=show_card_counts)

