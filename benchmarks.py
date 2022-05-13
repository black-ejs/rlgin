NUM_HANDS=10000
BENCHMARK_MAX_TURNS=1000
benchmarks={}

t=('b', 5189, 'b', 4811, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 5667, 'br10', 4333, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 8558, 'br50', 1442, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 9917, 'br90', 83, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 5554, 'br', 4446, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 9970, 'd', 30, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('b', 9958, 'r', 42, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 4646, 'b', 5354, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 5195, 'br10', 4805, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 8341, 'br50', 1659, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 9886, 'br90', 114, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 5137, 'br', 4863, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 9963, 'd', 37, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br10', 9953, 'r', 47, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 1537, 'b', 8463, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 1679, 'br10', 8321, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 5050, 'br50', 4949, 'nobody', 1)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 9461, 'br90', 477, 'nobody', 62)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 1811, 'br', 8189, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 9868, 'd', 65, 'nobody', 67)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br50', 9782, 'r', 147, 'nobody', 71)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 98, 'b', 9902, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 121, 'br10', 9879, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 447, 'br50', 9463, 'nobody', 90)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 1760, 'br90', 1738, 'nobody', 6502)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 116, 'br', 9884, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 1907, 'd', 64, 'nobody', 8029)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br90', 1777, 'r', 631, 'nobody', 7592)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 4621, 'b', 5379, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 5152, 'br10', 4848, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 8306, 'br50', 1694, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 9885, 'br90', 115, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 5132, 'br', 4868, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 9970, 'd', 30, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('br', 9964, 'r', 36, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 41, 'b', 9959, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 33, 'br10', 9967, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 47, 'br50', 9867, 'nobody', 86)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 74, 'br90', 1822, 'nobody', 8104)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 25, 'br', 9975, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 80, 'd', 77, 'nobody', 9843)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('d', 60, 'r', 660, 'nobody', 9280)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 41, 'b', 9959, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 46, 'br10', 9954, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 172, 'br50', 9771, 'nobody', 57)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 629, 'br90', 1758, 'nobody', 7613)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 39, 'br', 9961, 'nobody', 0)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 714, 'd', 76, 'nobody', 9210)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b
t=('r', 630, 'r', 667, 'nobody', 8703)
b={'player1': t[0],'wins1': int(t[1]), 'player2': t[2], 'wins2': int(t[3]), 'no_winner': int(t[5])}
benchmarks[(b['player1'],b['player2'])] = b

def get_benchmark(player1:(str), player2:(str)):
    if (player1,player2) in benchmarks:
        return benchmarks[(player1,player2)]
    return None

def get_benchmark_average(player1:(str), player2:(str)):
    b1 = get_benchmark(player1,player2)
    b2 = get_benchmark(player2,player1)
    wins1=0
    wins2=0
    no_winner=0
    if (b1 == None) and (b2 == None):
        return None
    if not (b1 == None):
        wins1 += b1['wins1']
        wins2 += b1['wins2']
        no_winner += b1['no_winner']
    if not (b2 == None):
        wins1 += b2['wins2']
        wins2 += b2['wins1']
        no_winner += b2['no_winner']
    b={'player1': player1,
       'wins1': int(wins1/2), 
       'player2': player2, 
       'wins2': int(wins2/2), 
       'no_winner': int(no_winner/2)}
    return b

def get_wpk_average(player1:(str), player2:(str)):
    ba = get_benchmark_average(player1,player2)
    b={'player1': player1,
       'wpk1': float(ba['wins1']/(NUM_HANDS/1000)), 
       'player2': player2, 
       'wpk2': float(ba['wins2']/(NUM_HANDS/1000)), 
       'no_winner': float(ba['wins2']/(NUM_HANDS/1000))}
    return b

def get_moving_average(player1:(str), player2:(str), window:(int)):
    return get_wpk_average(player1, player2)['wpk1']/(1000/window)

def get_cumulative_wins(player1:(str), player2:(str), hands:(int), max_turns:(int)=1000):
    array_wins=[]
    array_ordinals=[]
    wpk = get_wpk_average(player1, player2)['wpk1']
    hand_length_factor = float(max_turns/BENCHMARK_MAX_TURNS)
    wpk2 = float(wpk/hand_length_factor)
    for i in range(hands):
        array_wins.append(int(i*(wpk2/1000)))
        array_ordinals.append(i)
    return array_wins, array_ordinals
