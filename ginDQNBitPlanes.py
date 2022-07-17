
import numpy as np
import gin

class ginDQNBitPlanes():
    CONVO_INPUT_CHANNELS = 6
    CONVO_INPUT_CHANNEL_SIZE = [gin.NUM_SUITS, gin.NUM_RANKS]
    CONVO_BATCHSIZE = 1

    def create_state_channel():
        channel = []
        # initialze to OUT OF PLAY
        for i in range(ginDQNBitPlanes.CONVO_INPUT_CHANNEL_SIZE[0]):
            ylist = []
            for j in range(ginDQNBitPlanes.CONVO_INPUT_CHANNEL_SIZE[1]):
                ylist.append(0)
            channel.append(ylist)
        return channel

    def get_state(ginhand:(gin.GinHand), 
                        player:(gin.Player), 
                        pile_substitute:(gin.Card) = None):

        my_hand_channel = ginDQNBitPlanes.create_state_channel()
        just_discarded_channel = ginDQNBitPlanes.create_state_channel()
        unknown_channel = ginDQNBitPlanes.create_state_channel()
        other_hand_channel = ginDQNBitPlanes.create_state_channel()
        out_of_play_channel = ginDQNBitPlanes.create_state_channel()
        decision_channel = ginDQNBitPlanes.create_state_channel()
        state = []
        state.append(my_hand_channel)
        state.append(just_discarded_channel)
        state.append(other_hand_channel)
        state.append(unknown_channel)
        state.append(out_of_play_channel)
        state.append(decision_channel)

        if (not (ginhand.discard == None)) and (ginhand.discard == pile_substitute):
            # deciding the DRAW source
            for dc in decision_channel:
                dc[0]=1 

        # initialze OUT OF PLAY
        for i in range(len(out_of_play_channel)):
            for j in range(len(out_of_play_channel[0])):
                out_of_play_channel[i][j]=1

        for c in ginhand.deck.undealt:
            ginDQNBitPlanes.setState(c, unknown_channel, out_of_play_channel)

        me = player
        my_hand = ginhand.playing[me.name].playerHand

        if ginhand.discard == None:
            if pile_substitute == None:
                print("nothing to select here!")
                return np.asarray([out_of_play_channel])
            if not (pile_substitute in my_hand.card):
                print("** DISCARD DECISION WITH CARD NOT IN MY HAND")

        if not (pile_substitute == None):  
            ginDQNBitPlanes.setState(pile_substitute, just_discarded_channel, out_of_play_channel)
        elif not (ginhand.discard == None):  # use ginhand.discard
            ginDQNBitPlanes.setState(ginhand.discard, just_discarded_channel, out_of_play_channel)

        other_hand = ginhand.notCurrentlyPlaying().playerHand
        if other_hand == my_hand:
            other_hand = ginhand.currentlyPlaying.playerHand # shouldn't happen
        for c in other_hand.card:
            ginDQNBitPlanes.setState(c, unknown_channel, out_of_play_channel)

        for c in my_hand.card:
            if not c == pile_substitute:
                ginDQNBitPlanes.setState(c, my_hand_channel, out_of_play_channel)
        
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
                ginDQNBitPlanes.setState(c, other_hand_channel, out_of_play_channel)

        #return DQNAgent.as_numpy_array([state])
        return np.asarray(state)

    def setState(c:(gin.Card), state:(list), oopc:(list)):
        state[int(c.toInt()/13)][c.toInt()%13] = 1
        oopc[int(c.toInt()/13)][c.toInt()%13] = 0

    def calc_input_size(params):
        input_size = []
        input_size.append(ginDQNBitPlanes.CONVO_BATCHSIZE)
        input_size.append(ginDQNBitPlanes.CONVO_INPUT_CHANNELS)
        input_size.extend(ginDQNBitPlanes.CONVO_INPUT_CHANNEL_SIZE)
        return tuple(input_size)

