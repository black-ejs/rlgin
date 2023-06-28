import random
import copy

NUM_SUITS=4
NUM_RANKS=13
HAND_SIZE=4

class Card:
	rankNames = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
	suitNames = ["C","D","H","S"]
	
	def __init__(self, prank, psuit):
		if prank>=NUM_RANKS or prank<0:
			raise Exception(f"illegal rank of {prank}, range is 0-{NUM_RANKS}")
		if psuit<0 or psuit>=NUM_SUITS:
			raise Exception(f"illegal suit of {psuit}, range is 0-{NUM_SUITS}")
		self.rank=int(prank)
		self.suit=int(psuit)

	def rankName(rank):
		return Card.rankNames[rank]

	def rankName(self):
		return Card.rankNames[self.rank]

	def suitName(suit):
		return Card.suitNames[suit]

	def suitName(self):
		return Card.suitNames[self.suit]

	def ginScore(self):
		if self.rank < 9:
			return self.rank+2
		if self.rank == 12: 
			return 1   # ace
		return 10  # picture card

	def __str__(self):
		e = self.rankName()
		f = self.suitName()
		return f"{self.rankName()}{self.suitName()}"

	def __eq__(self, other):
		if other == None:
			return False
		#rs = self.rank
		#ss = self.suit
		#ro = other.rank
		#so = other.suit
		#t = (self.rank==other.rank and self.suit==other.suit)
		#v = (rs==ro and ss==so)

		return self.rank==other.rank and self.suit==other.suit

	def __lt__(self, other):
		if other == None:
			return False
		s=self.toInt()
		o=other.toInt()
		return s<o

	def __gt__(self, other):
		if other == None:
			return True
		s=self.toInt()
		o=other.toInt()
		return s>o

	def toInt(self) -> int:
		return self.suit*NUM_RANKS + self.rank;

	def fromInt(hval):
		i=int(hval)
		return Card(int(i)%int(NUM_RANKS),int(i)/int(NUM_RANKS))

	def fromStr(hval:(str)):
		rank = Card.rankNames.index(hval[:-1])
		suit = Card.suitNames.index(hval[-1])
		return Card(rank,suit)

## #################################################x
class Hand:

	def __init__(self,cards):
		self.card = copy.deepcopy(cards)

	def __str__(self):
		rez=""
		for c in self.card:
			rez += c.__str__()
			rez+=" "
		rez = rez[:-1]
		return rez

	def __eq__(self, other):
		if isinstance(other, Hand):
			for c in self.card:
				if not other.contains(c):
					return False
			return True 
		return False

	def contains(self, c:(Card)):
		return c in self.card

	def sort(self):
		self.card.sort()

	def wins(self):
		Hand.wins(self)

	def wins(hand):
		runs, matches, cards = hand.analyze()
		winningHand = []
		for r in runs:
			for c in r:
				winningHand.append(c) 			
		for m in matches:
			for c in m:
				if not c in winningHand:
					winningHand.append(c)
		return len(winningHand) == HAND_SIZE

	def analyze(self):
		"""
		separate into runs, matches, and cards in neither
		"""
		cards = copy.copy(self.card)

		## find runs
		cards.sort()
		runs = []
		i=0
		while i<len(cards)-2:
			if (cards[i].rank+1 == cards[i+1].rank and 
					cards[i].suit == cards[i+1].suit and 
					cards[i].rank+2 == cards[i+2].rank and
					cards[i].suit == cards[i+2].suit):
				run = []
				runs.append(run)
				for c in cards[i:i+3]:
					run.append(c)
				i+=2
				while (i<len(cards)-1 and 
						cards[i].rank+1 == cards[i+1].rank and 
						cards[i].suit == cards[i+1].suit):
					run.append(cards[i+1])
					i+=1
			i+=1

		## find matches
		matches = []
		for c in cards:
			alreadyMatched = False
			for m in matches:
				if c in m:
					alreadyMatched = True
			if not alreadyMatched:		
				match = []
				match.append(c)
				for p in cards:
					if p.rank == c.rank and not p.suit == c.suit:
						match.append(p)
				if len(match) >2:
					matches.append(match)

		# check for conflicts
		for r in runs:
			for c in r:
				for m in matches:
					if c in m:
						# c shows up in a match and a run
						if len(m) > 3:
							m.remove(c)
						elif len(r)>3 and (c == r[0] or c==r[len(r)-1]):
							r.remove(c)
						else:
							# one will be destroyed
							m.clear()

		return runs, matches, cards

	def prettyStr(self):
		runs, matches, cards = self.analyze()
		prettyHand = []
		for r in runs:
			for c in r:
				if not c in prettyHand:
					prettyHand.append(c) 			
		for m in matches:
			for c in m:
				if not c in prettyHand:
					prettyHand.append(c) 			
		for c in cards:
			if not c in prettyHand:
				prettyHand.append(c)

		result = ""
		for c in prettyHand:
			result = result + c.__str__() + " "
		result = result[:-1]

		if not len(prettyHand) == HAND_SIZE:
			print(f"gin error: analyzed hand contains duplicates: {result}")

		return result

	def deadwood(self):
		runs, matches, cards = self.analyze()
		score=0
		already = []
		for r in runs:
			for c in r:
				if not c in already:
					cards.remove(c)
					already.append(c) 			
		for m in matches:
			for c in m:
				if not c in already:
					cards.remove(c)
					already.append(c) 			
		for c in cards:
			score += c.ginScore()
		return score

## //////////////////////////////////////////////////
class Deck:

	_cardList = []

	def cardList():
		return copy.deepcopy(Deck._cardList)

	def __init__(self):
		if len(Deck._cardList)==0:
			Deck.initCardList()
		self.shuffle()
	
	def next(self): 
		nextCard = self.undealt.pop()
		return nextCard
	
	def isEmpty(self):
		return len(self.undealt)<=0
	
	def shuffle(self):
		self.undealt=copy.copy(Deck._cardList)
		random.shuffle(self.undealt)
	
	def contains(self,card):
		return card in self.undealt

	def card2Int(card):
		return Deck._cardList.index(card)

	def int2Card(i):
		return Deck._cardList[i]

	def initCardList():
		for rank in range(NUM_RANKS):
			for suit in range(NUM_SUITS):
				Deck._cardList.append(Card(rank,suit))

## ##X####x###########################################x
class Player:
	def __init__(self, playerName):
		self.name=playerName

	def __eq__(self, other):
		return (not (other == None)) and self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def __int__(self):
		return hash(self.name)

	def __str__(self):
		return self.name

## ##X####x###########################################x
class Draw:
	"""
	a "draw" of a Card, to start a Turn, binds together
	 - the Card drawn
	 - the Source of the Draw, either PILE (top card) or DECK
	"""
	PILE="PILE"
	DECK="DECK"
	def __init__(self, source, card):
		self.source=source
		self.card=card

## ##X####x###########################################x
class Turn:
	"""
	a Player's turn, a Draw followed by the discard of a Card
	"""
	## distinguishes phases of a Turn
	DRAW=0
	DISCARD=1
	
	def __init__(self, player):
		self.player=player   ## a Player
		self.draw=None       ## a Draw
		self.discard=None ## a Card
	
	def __str__(self):
		rez  = f"{self.player.name} drew {self.draw.card} from the {self.draw.source}"
		rez += f", and "
		rez += f"discarded {self.discard}" 
		return rez

class Playing:
	"""
	Binds together a Player and a GinHand, using
	   - a Player 
	   - a PlayerHand (from an active GinHand)
	   - a Strategy (to play the GinHand)
	"""
	def __init__(self,player,strategy):
		self.player=player
		self.strategy=strategy
		
		def __copy__(self):
			p=Playing(self.player,self.strategy)
			if hasattr(self, "playerHand"):
				p.playerHand=Hand(self.playerHand.card)
			return p

## #########################################	
class GinStrategy:
	"""
	Abstract Class - implement these two methods 
	"""
	def __init__(self):
		return self

	def startOfTurn(self, ginHand):
		pass

	def decideDrawSource(self, ginhand):
		pass

	def decideDiscardCard(self, ginHand):
		pass

	def endOfTurn(self, ginHand):
		pass

	def endOfHand(self, ginHand):
		pass

## #########################################	
class GinHand:
	"""
	plays a single hand of "gin"
	   - stores history in a list of Turns
	"""
	UNDEALT = "undealt"
	READY_TO_PLAY = "ready to play"
	PLAYING = "playing"
	DONE = "done"

	GIN_BONUS = 25

	def __init__(self,playerOne,strategyOne,playerTwo,strategyTwo):
		self.lifecycle_stage = GinHand.UNDEALT
		self.playing = {}
		self.playingOne = Playing(playerOne,strategyOne)
		self.playing[playerOne.name] = self.playingOne
		self.playingTwo = Playing(playerTwo,strategyTwo)
		self.playing[playerTwo.name] = self.playingTwo
		self.deck = Deck()
		self.deck.shuffle()		
		self.turns = []
		self.extend_hands = True
		# self.currentlyPlaying = 
		# self.discard = 
		# self.winner =
		# self.firstPileCard 
	
	def lastTurn(self):
		if hasattr(self,"turns") == False or len(self.turns)==0:
			return None
		return self.turns[len(self.turns)-1]
	
	def deal(self):
		self.deck.shuffle()
		self.playingOne.playerHand = self.dealPlayerHand()
		self.playingTwo.playerHand = self.dealPlayerHand()
		
		self.discard = self.deck.next()
		self.firstPileCard = self.discard
		self.out_of_play = []

		# play() loop starts by activating the non-current player
		self.currentlyPlaying = self.playingTwo
		self.lifecycle_stage = GinHand.READY_TO_PLAY
			
	def dealPlayerHand(self):
		cards = []
		for i in range(HAND_SIZE):
			cards.append(self.deck.next())
		return Hand(cards)
	
	def recycleDiscards(self):
		for c in self.out_of_play:
			self.deck.undealt.append(c)
		random.shuffle(self.deck.undealt)
		self.out_of_play = []
	
	def play(self):
		"""
		returns the winner as a Playing, or last player if no winner
		"""
		return self.play(1000) # should kill the Deck :-)

	def play(self, maxTurns):
		"""
		returns the winning hand, or None if no winner
		"""
		turns = 0
		self.winner = None
		self.lifecycle_stage = GinHand.PLAYING

		while (self.winner == None 
				and turns<maxTurns):

			if self.deck.isEmpty():
				if self.extend_hands:
					self.recycleDiscards()
				else:
					break

			turns+=1			
			
			self.nextTurn()

			strategy=self.currentlyPlaying.strategy
			playerHand=self.currentlyPlaying.playerHand

			strategy.startOfTurn(self)

			drawSource = strategy.decideDrawSource(self)
			self.doDraw(drawSource)
			
			discardCard = strategy.decideDiscardCard(self)
			self.doDiscard(discardCard)

			if playerHand.wins():
				self.winner = self.currentlyPlaying

			strategy.endOfTurn(self)

		self.lifecycle_stage = GinHand.DONE
		self.playingOne.strategy.endOfHand(self)
		self.playingTwo.strategy.endOfHand(self)
		return self.winner
	
	def doDraw(self, drawSource):
		if drawSource==Draw.DECK:
			drawCard = self.deck.next()
		else:
			drawCard = self.discard
			self.discard = None
		
		self.currentlyPlaying.playerHand.card.append(drawCard)
		self.lastTurn().draw = Draw(drawSource, drawCard)
	
	def doDiscard(self,discardCard):
		if not self.discard == None:
			self.out_of_play.append(self.discard)
		self.discard = discardCard
		self.currentlyPlaying.playerHand.card.remove(discardCard)
		self.lastTurn().discard = discardCard	

	def nextTurn(self):
		if self.currentlyPlaying == self.playingOne:
			self.currentlyPlaying = self.playingTwo
		else:
			self.currentlyPlaying = self.playingOne
		
		self.turns.append(Turn(self.currentlyPlaying.player))

	def pendingAction(self):
		if self.lastTurn() == None:
			return Turn.DRAW
		if not hasattr(self.lastMove(),("draw")):
			return Turn.DRAW
		else:
			return Turn.DISCARD

	def __str__(self):
		rez = ""
		
		turn_count = len(self.turns)
		if turn_count>0:
			rez += f"Turn {turn_count}" + '\n'
			m = self.turns[turn_count-1]
			rez += str(m)
		else:
			rez += "awaiting first play"
		
		rez += '\n'
		
		rez += self.toString(self.playingOne) + '\n'
		rez += self.toString(self.playingTwo) + '\n'
		
		return rez
	
	def notCurrentlyPlaying(self):
		return self.otherPlaying(self.currentlyPlaying)

	def otherPlaying(self,notThisOne:Playing):
		if notThisOne == self.playingOne:
			return self.playingTwo
		return  self.playingOne
	
	def toString(self,which):
		if which==1:
			return self.toString(self.playingOne)
		return self.toString(self.playingTwo)
	
	def toString(self,playing):
		rez = ""
		
		rez += playing.player.name
		if hasattr(playing, "playerHand"):
			rez += "'s hand: " + str(playing.playerHand)
		
		if hasattr(self, "discard"):
			rez += "     PILE: " + str(self.discard)
		
		return rez

	def ginScore(self):
		"""
		returns a 3-tuple
		   - the winner (as a Playing), 
		   - the score to award to the winner 
		   - a boolean indicating if the hand has completed
		   if the boolean is False (i.e., the hand has not yet completed), 
		          - the "winner" is the player with the higher score in their hand, 
		          - the "score" is the difference
		          - if the two player's scores are equal at that time, 
			            - the winner is None
			            - the score is zero
		"""
		winner = self.winner
		h1 = self.playingOne.playerHand
		h2 = self.playingTwo.playerHand
		if self.winner == self.playingOne:
			score = (h2.deadwood() - h1.deadwood()) + GinHand.GIN_BONUS
			winner = self.playingOne
		elif self.winner == self.playingTwo:
			score = (h1.deadwood() - h2.deadwood()) + GinHand.GIN_BONUS
			winner = self.playingTwo
		else:
			score = h2.deadwood() - h1.deadwood()
			if score>0:
				winner = self.playingOne
			else:
				winner = self.playingTwo
				score = -score

		return winner, score, self.lifecycle_stage==GinHand.DONE


			

## #########################################	

