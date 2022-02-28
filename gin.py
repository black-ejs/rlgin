import random
import copy

NUM_SUITS=4
NUM_RANKS=13
HAND_SIZE=4

class Card:
	rankNames = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
	suitNames = ["C","D","H","S"]
	
	def __init__(self, prank, psuit):
		if prank>=NUM_RANKS | prank<0:
			raise Exception(f"illegal rank of {prank}, range is 0-{NUM_RANKS}")
		if psuit<0 | psuit>=NUM_SUITS:
			raise Exception(f"illegal suit of {psuit}, range is 0-{NUM_SUITS}")
		self.rank=prank
		self.suit=psuit

	def rankName(rank):
		return Card.rankNames[rank]

	def rankName(self):
		return Card.rankNames[self.rank]

	def suitName(suit):
		return Card.suitNames[suit]

	def suitName(self):
		return Card.suitNames[self.suit]

	def __str__(self):
		e = self.rankName()
		f = self.suitName()
		return f"{self.rankName()}{self.suitName()}"

	def __eq__(self, other):
		if other == None:
			return False
		rs = self.rank
		ss = self.suit
		ro = other.rank
		so = other.suit
		t = (self.rank==other.rank and self.suit==other.suit)
		v = (rs==ro and ss==so)

		return self.rank==other.rank and self.suit==other.suit

	def __lt__(self, other):
		s=self.__hash__()
		o=other.__hash__()
		return s<o

	def __gt__(self, other):
		s=self.__hash__()
		o=other.__hash__()
		return s>o

	def toInt(self) -> int:
		return self.suit*13 + self.suit;

	def fromInt(hval):
		i=int(hval)
		return Card(int(i)%int(NUM_RANKS),int(i)/int(13))

## #################################################x
class Hand:

	def __init__(self,cards):
		self.card = copy.deepcopy(cards)

	def __str__(self):
		rez=""
		for i in range(len(self.card)):
			rez += self.card[i].__str__()
			if i<(len(self.card)-1):
				rez+=" "
		return rez

	def __eq__(self, other):
		if isinstance(other, Hand):
			for c in self.card:
				if not other.contains(c):
					return False
			return True 
		return False

	def contains(self, c):
		return c in self.card

	def sort(self):
		self.card.sort()

	def wins(self):
		Hand.wins(self)

	def wins(hand):
		# if any card is not part of a match or
		# part of a run, the hand is not a winner
		# if all cards are part of a match or run, and
		# one is 4 cards lon, the hand is a winner
		four = False
		for c in hand.card:
			score = Hand.scoreCard(hand, c)
			if (score < 50):  
				# no match or run
				return False
			if (score > 100):  
				four = True

		if not four:
			return False

		return True

	def scoreCard(hand,c):
		match = False
		run = False
		match4 = False
		run4 = False

		# check match
		neighbors = []
		matchcount = 0
		for s in range(NUM_SUITS):
			if not s==c.suit:
				neighbors.append(Card(c.rank,s))
		for n in neighbors:
			if hand.contains(n):
				matchcount+=1
		if matchcount>1:
			match = True
			if matchcount==3:
				match4 = True

		# check run
		neighbors = []
		runcount = 0
		if c.rank>0:
			leftNeighbor=Card(c.rank-1,c.suit)
			if hand.contains(leftNeighbor):
				runcount+=1
				if c.rank>1:
					leftNeighbor2=Card(c.rank-2,c.suit)
					if hand.contains(leftNeighbor2):
						runcount+=1
						
		if c.rank<NUM_RANKS-1:
			rightNeighbor=Card(c.rank+1,c.suit)
			if hand.contains(rightNeighbor):
				runcount+=1
				if c.rank<NUM_RANKS-2:
					rightNeighbor2=Card(c.rank+2,c.suit)
					if hand.contains(rightNeighbor2):
						runcount+=1

		if runcount>1:
			run = True
			if runcount==3:
				run4 = True

		score = runcount + matchcount
		if match or run:
			score += 50
			if match4 or run4:
				score += 100

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
		return self.undealt.contains(card)

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
		return self.name == other.name

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
	
	def __init__(self, player, draw=Draw(Draw.DECK,Card(0,0)), discard=Card(0,0)):
		self.player=player   ## a Player
		self.draw=draw       ## a Draw
		self.discard=discard ## a Card
	
	def __str__(self):
		rez = "opponent drew "
		if self.draw.source == "PILE":
			# only show cards opponent picks up from the PILE
			rez += self.draw.card
			rez += " "
		rez += f"from the {self.draw.source}\n"
		rez += f"opponent discarded {self.discard}" 
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

	def __init__(self,playerOne,strategyOne,playerTwo,strategyTwo):
		self.lifecycle_stage = GinHand.UNDEALT
		self.playing = {}
		self.playingOne = Playing(playerOne,strategyOne)
		self.playing[playerOne] = self.playingOne
		self.playingTwo = Playing(playerTwo,strategyTwo)
		self.playing[playerTwo] = self.playingTwo
		self.deck = Deck()
		self.deck.shuffle()		
		self.turns = []
		# self.currentlyPlaying = 
		# self.discard = 
		# self.winner =
		# self.firstPileCard 
	
	def lastTurn(self):
		if hasattr(self,"turns") == False | len(self.turns)==0:
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
				self.recycleDiscards()

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
		
		self.currentlyPlaying.playerHand.card.append(drawCard)
		self.lastTurn().draw = Draw(drawSource, drawCard)
	
	def doDiscard(self,discardCard):
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
		
		if len(self.turns)>0:
			m = self.turns[len(self.turns)-1]
			rez += m
		else:
			rez += "awaiting first play"
		
		rez += '\n'
		
		rez += self.toString(self.playingOne) + '\n'
		rez += self.toString(self.playingTwo) + '\n'
		
		return rez
	
	def toString(self,which):
		if which==1:
			return self.toString(self.playingOne)
		return self.toString(self.playingTwo)
	
	def toString(self,playing):
		rez = ""
		
		rez += playing.player.name
		if hasattr(playing, "playerHand"):
			rez += "'s hand: " + playing.playerHand
		
		if hasattr(self, "discard"):
			rez += "     PILE: " + self.discard
		
		return rez

## #########################################	

