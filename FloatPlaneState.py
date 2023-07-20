import numpy as np
import gin

## ###############################################
class FloatPlaneState():
    OUTPUT_PLANES = 1
    OUTPUT_PLANE_SIZE = [gin.NUM_SUITS, gin.NUM_RANKS + 1]
    OUTPUT_SIZE = (OUTPUT_PLANES,OUTPUT_PLANE_SIZE[0],OUTPUT_PLANE_SIZE[1])

    default_state_values = {'IN_OTHER_HAND': -0.500,
                'OUT_OF_PLAY': -0.100,
                'UNKNOWN': 0.0,
                'JUST_DISCARDED': 0.100,
                'IN_MY_HAND': 0.500,
                'DECIDE_DRAW_SOURCE': 0.000,
                'DECIDE_DISCARD_CARD': 1.000
    }

    def __init__(self, params):
        if 'state_values' in params:
            self.state_values=params['state_values']
        else:
            self.state_values=self.default_state_values
          
    def get_state(self, ginhand:(gin.GinHand), 
                         player:(gin.Player), 
                         pile_substitute:(gin.Card) = None):

        decide_val = self.state_values['DECIDE_DISCARD_CARD']
        if (not (ginhand.discard == None)) and (ginhand.discard == pile_substitute):
            decide_val = self.state_values['DECIDE_DRAW_SOURCE']
 
        state = []
 
        # initialze to OUT OF PLAY
        for i in range(self.OUTPUT_PLANE_SIZE[0]):
            ylist = []
            for j in range(self.OUTPUT_PLANE_SIZE[1]-1):
                ylist.append(self.state_values['OUT_OF_PLAY'])
            state.append(ylist)

        # set decision
        for i in range(len(state)):
            state[i].append(decide_val)

        for c in ginhand.deck.undealt:
            self.val2State(c, state, self.state_values['UNKNOWN'])
        
        me = player
        my_hand = ginhand.playing[me.name].playerHand

        if ginhand.discard == None and len(my_hand.card)<gin.HAND_SIZE+1:
            if pile_substitute == None:
                print("nothing to select here!")
                return np.asarray([state])
            elif not (pile_substitute in my_hand.card):
                print("** DISCARD DECISION WITH CARD NOT IN MY HAND")
 
        if not (pile_substitute == None):  
            self.val2State(pile_substitute, state, self.state_values['JUST_DISCARDED'])
        elif not (ginhand.discard == None):  # use ginhand.discard
            self.val2State(ginhand.discard, state, self.state_values['JUST_DISCARDED'])
 
        other_hand = ginhand.notCurrentlyPlaying().playerHand
        if other_hand == my_hand:
            other_hand = ginhand.currentlyPlaying.playerHand # shouldn't happen
        for c in other_hand.card:
            self.val2State(c, state, self.state_values['UNKNOWN'])
 
        for c in my_hand.card:
            if not c == pile_substitute:
                self.val2State(c, state, self.state_values['IN_MY_HAND'])
         
        ## look for IN_OTHER_HAND (drawn, never discarded)
        cards_opponent_holds = []
        for turn in ginhand.turns:
            if turn.draw == None:
                break  # current turn, not yet drawn
            if turn.player == me:
                continue
            if turn.draw.source == gin.Draw.PILE:
                cards_opponent_holds.append(turn.draw.card)
            if turn.discard == None:
                break  # current turn, no discard yet
            if turn.discard in cards_opponent_holds:
                cards_opponent_holds.remove(turn.discard)
        for c in cards_opponent_holds:
            if len(cards_opponent_holds) > gin.HAND_SIZE:
                print(f"** warning: get_state() finds too many cards in other hand {cards_opponent_holds}")
            self.val2State(c, state, self.state_values['IN_OTHER_HAND'])
 
        return np.asarray([state])
 
    def val2State(self, c:(gin.Card), state:(list), val:(float)):
        state[int(c.toInt()/13)][c.toInt()%13] = val
 

    ## ###############################################

