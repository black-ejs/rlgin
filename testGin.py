import copy
import random
import gin

def testInts():
	i=0
	for c in gin.Deck.cardList():
		print(f"{i}: {c} {c.toInt()} {c.fromInt(c.toInt())}")
		i+=1

def testWins():
	h2match_3matchs = gin.Hand([gin.Card(0,0),gin.Card(0,1),gin.Card(0,2),gin.Card(0,3),
								gin.Card(1,0),gin.Card(1,1),gin.Card(1,2)])
	h2match_fail = gin.Hand([gin.Card(0,0),gin.Card(0,1),gin.Card(0,2),gin.Card(0,3),
								gin.Card(1,0),gin.Card(1,1),gin.Card(4,2)])
	h3run4run_m = gin.Hand([gin.Card(7,2),gin.Card(8,2),gin.Card(9,2),gin.Card(4,3),
								gin.Card(5,3),gin.Card(6,3),gin.Card(7,3)])
	h3run4match_m = gin.Hand([gin.Card(7,2),gin.Card(8,2),gin.Card(9,2),gin.Card(11,3),
								gin.Card(11,0),gin.Card(11,1),gin.Card(11,2)])
	h3match4run_m = gin.Hand([gin.Card(9,0),gin.Card(10,0),gin.Card(7,0),gin.Card(8,0),
								gin.Card(11,0),gin.Card(11,1),gin.Card(11,2)])
	hjunk_f = gin.Hand([gin.Card(9,3),gin.Card(1,0),gin.Card(7,2),gin.Card(5,0),
								gin.Card(7,0),gin.Card(1,1),gin.Card(12,2)])
	tricky_m = gin.Hand([gin.Card(9,3),gin.Card(9,0),gin.Card(9,1),gin.Card(9,2),
								gin.Card(10,0),gin.Card(11,0),gin.Card(12,0)])
	tricky_f = gin.Hand([gin.Card(9,3),gin.Card(9,0),gin.Card(9,1),gin.Card(9,2),
								gin.Card(10,0),gin.Card(11,0),gin.Card(12,1)])
	wf1 = gin.Hand([gin.Card(0,0),gin.Card(0,1),gin.Card(0,2),gin.Card(0,3),
								gin.Card(1,1),gin.Card(11,0),gin.Card(12,1)])

	print(f"h2match_3matchs {h2match_3matchs.wins()}")
	print(f"        {h2match_3matchs.prettyStr()}")
	print(f"h2match_fail {h2match_fail.wins()}")
	print(f"        {h2match_fail.prettyStr()}")
	print(f"h3run4run_m {h3run4run_m.wins()}")
	print(f"        {h3run4run_m.prettyStr()}")
	print(f"h3run4match_m {h3run4match_m.wins()}")
	print(f"        {h3run4match_m.prettyStr()}")
	print(f"h3match4run_m {h3match4run_m.wins()}")
	print(f"        {h3match4run_m.prettyStr()}")
	print(f"hjunk_f {hjunk_f.wins()}")
	print(f"        {hjunk_f.prettyStr()}")
	print(f"tricky_m {tricky_m.wins()}")
	print(f"        {tricky_m.prettyStr()}")
	print(f"tricky_f {tricky_f.wins()}")
	print(f"        {tricky_f.prettyStr()}")

def testWins2():
	d = gin.Deck()
	count = 0
	wincount = 0
	for i in range(50000):
		count+=1
		d.shuffle()
		cards = []
		for j in range(gin.HAND_SIZE):
			cards.append(d.next())
		h = gin.Hand(cards)
		if (h.wins()):
			wincount+=1
			print(f"Winner {h}")
	print(f"***** {wincount} random hands won out of {count}")

def testWins3():
	initWinners()
	print(f"***** {len(winningHands)} winning hands generated")
	count=0
	for hand in winningHands:
		if not hand.wins():
			print(f"non-winning winner: {hand}")
			count+=1
	print(f"***** {count} hands flunked")

def testWins4():
	initWinners()
	for hand in winningHands:
		myHand = copy.copy(hand)
		random.shuffle(myHand.card)
		print(f"** winner: {myHand.prettyStr()}")
		print(f"xx ugly..: {myHand}")

winningHands=[]

def initWinners():
	if len(winningHands)>0:
		winningHands.clear()
	hand = []
	for i in range(gin.HAND_SIZE):
		hand.append(gin.Card(1,1))

	## ///////////////////////
	## 4-of-a-kind hands
	for rank4 in range(gin.NUM_RANKS):
			
		## 4 of a kind - one of each suit
		for suit in range(gin.NUM_SUITS):
			hand[suit]=gin.Card(rank4,suit)
			
		## with 3-of-a-kind
		for rank3 in range(gin.NUM_RANKS):
			if rank3!=rank4:
				for suit in range(gin.NUM_SUITS):
					i=4
					for xsuit in range(gin.NUM_SUITS):
						if suit!=xsuit: ## leave out 1 suit
							hand[i]=gin.Card(rank3,xsuit)
							i+=1
					winningHands.append(gin.Hand(hand))
			
		## with 3-sequence
		for seqstart in range(gin.NUM_RANKS-2):
			if seqstart==hand[0].rank | (seqstart+1)==hand[0].rank | (seqstart+2)==hand[0].rank:
				continue	## skip runs containing our four-of-a-kind
				
			for suit in range(gin.NUM_SUITS):
				hand[4]=gin.Card(seqstart,suit)
				hand[5]=gin.Card(seqstart+1,suit)
				hand[6]=gin.Card(seqstart+2,suit)
				winningHands.append(gin.Hand(hand))
		
		
	## ///////////////////////
	## 3-of-a-kind hands
	for rank3 in range(gin.NUM_RANKS):
		## 3 of a kind - one of each suit
		for suit in range(gin.NUM_SUITS):
			i=0
			for xsuit in range(gin.NUM_SUITS):
				if suit!=xsuit:
					hand[i]=gin.Card(rank3,xsuit)
					i=i+1
			
		## with 4-of-a-kind - we already have these!
		
		## with 4-sequence
		# 			
		for seqstart in range(gin.NUM_RANKS-3):
			for suit in range(gin.NUM_SUITS):
				c1 = gin.Card(seqstart,suit)
				if (hand[0]==c1) | (hand[1]==c1) | (hand[2]==c1):
					break
				c2 = gin.Card(seqstart+1,suit)
				if (hand[0]==c2) | (hand[1]==c2) | (hand[2]==c2):
					break
				c3 = gin.Card(seqstart+2,suit)
				if (hand[0]==c3) | (hand[1]==c3) | (hand[2]==c3):
					break
				c4 = gin.Card(seqstart+3,suit)
				if (hand[0]==c4) | (hand[1]==c4) | (hand[2]==c4):
					break
						
				hand[3] = c1
				hand[4] = c2
				hand[5] = c3
				hand[6] = c4
				winningHands.append(gin.Hand(hand))
		
	## ///////////////////////
	## all-sequence hands
	for lowStart in range(gin.NUM_RANKS-2):
		for lowSuit in range(gin.NUM_SUITS):
			## 3-sequence lo, 4-sequence hi
			hand[0] = gin.Card(lowStart, lowSuit)
			hand[1] = gin.Card(lowStart+1, lowSuit)
			hand[2] = gin.Card(lowStart+2, lowSuit)
			for hiStart in range(lowStart+3,gin.NUM_RANKS-3):
				for hiSuit in range(gin.NUM_SUITS):
					hand[3] = gin.Card(hiStart, hiSuit)
					hand[4] = gin.Card(hiStart+1, hiSuit)
					hand[5] = gin.Card(hiStart+2, hiSuit)
					hand[6] = gin.Card(hiStart+3, hiSuit)
					winningHands.append(gin.Hand(hand))
					
			## 4-sequence lo, 3-sequence hi
			if lowStart+3 < gin.NUM_RANKS:
				hand[0] = gin.Card(lowStart, lowSuit)
				hand[1] = gin.Card(lowStart+1, lowSuit)
				hand[2] = gin.Card(lowStart+2, lowSuit)
				hand[3] = gin.Card(lowStart+3, lowSuit)
				for hiStart in range(lowStart+4,hiStart<gin.NUM_RANKS-2):
					for hiSuit in range(gin.NUM_SUITS):
						if hiStart==lowStart+4 and hiSuit==lowSuit:
							continue  ## already did thi
						hand[4] = gin.Card(hiStart, hiSuit)
						hand[5] = gin.Card(hiStart+1, hiSuit)
						hand[6] = gin.Card(hiStart+2, hiSuit)
						winningHands.append(gin.Hand(hand))


def winnersString():
	winnersStr = ""

	for winningHand in winningHands:
		winnersStr+=winningHand.prettyStr()
		winnersStr+='\n'
		
	return winnersStr

## //////////////////////////////////////////////////
if __name__ == '__main__':	
	testInts()
	testWins()
	testWins2()
	testWins3()
	testWins4()


