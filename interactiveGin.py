import gin
import playGin

def	playHand():
	p1 = gin.Player("joe")
	p2 = gin.Player("annie");
	hand = gin.GinHand(p1,InteractiveGinStrategy(), 
					p2, playGin.DumbassGinStrategy())
	hand.deal();
	winner = hand.play(10000)
	if winner == None:
		print("NO WINNER")
	else:
		print(f"WINNER: {winner.player.name} {winner.playerHand.prettyStr()}")

class InteractiveGinStrategy(gin.GinStrategy):
	def __init__(self):
		gin.GinStrategy.__init__(self)
	
	def decideDrawSource(self, hand):
		self.presentForDraw(hand)
		drawSource = None
		while drawSource==None:
			print("DECK or PILE?")
			line = input()
			if len(line)>0:
				if line[0].upper()=='D':
					drawSource=gin.Draw.DECK
				elif line[0].upper()=='P':
					drawSource=gin.Draw.PILE
				elif line[0].upper()=='Q':
					self.quitTheGame()

		return drawSource
	
	def presentForDraw(self, ginHand):
		if len(ginHand.turns)>1:
			opponentMove = ginHand.turns[len(ginHand.turns)-2]
			drawSource = opponentMove.draw.source;
			if drawSource==gin.Draw.PILE:
				drawCardStr = opponentMove.card.__str__()
			else:
				drawCardStr = ""
			print(f"your opponent drew {drawCardStr} from the {drawSource}")
			print(f"your opponent discarded {opponentMove.discard}")
		else:
			print("you are the first player")
		
		print(f"{ginHand.currentlyPlaying.player.name}'s hand: {ginHand.currentlyPlaying.playerHand}     PILE: {ginHand.discard}")

	def decideDiscardCard(self, hand):
		cardChoice = -1; 
		
		playerHand = hand.currentlyPlaying.playerHand
		playerName = hand.currentlyPlaying.player.name
		print(f"{playerName}'s hand: {playerHand}" )

		while cardChoice==-1:
			print("Discard (1-8, left to right)?")
			line = input()
			try:
				if line[0].upper()=='Q':
					self.quitTheGame()
				candidate = int(line)
				if candidate>0 and candidate<9:
					cardChoice = candidate
				else:
					print(f"cannot use {line} as a choice.");
			except ValueError:
				print(f"cannot use {line} as a choice.");

		return playerHand.card[cardChoice-1]

	def quitTheGame(self):
		print("Goodbye.")
		quit()

## ################################################
## ################################################
## ################################################
if __name__ == '__main__':	
	playHand()
	

