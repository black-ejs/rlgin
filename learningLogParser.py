from collections.abc import Iterable
import sys
import math
import time
import re
import distutils.util

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from learningGin import NO_WIN_NAME

import regressionPlotter
import benchmarks
import gin

MA_SIZE = 200

## #############################################
## #############################################
## ###################################################
class LearningLogParser:
    def __init__(self):

        self.scenario_players = {}
        self.nn_players = {}
        self.statsList = []
        self.cumulative_averages = []
        self.cumulative_average = []
        self.score_stats = {}

    def get_default_name_scenario(self):
        return self.filepath + '.learning_' + str(self.session_count)

    def save_training_session(self):
        self.stats['hands'] = self.hands
        self.stats['scenario_players'] = self.scenario_players
        self.stats['nn_players'] = self.nn_players
        ma_arrays = {}
        for p in self.nn_players.values():
            if 'mode' in self.stats:
                if p[self.stats['mode']]:  # e.g. p['train']==True
                    p['mode']=self.stats['mode']
                else:
                    p['mode']="idle" 
            else:
                p['mode']="idle" 

            if len(p['ma_array']) == 0:
                # we never made it to the window
                # dummy something up to avoid problems
                for hand in self.hands:
                    p['ma_array'].append(1)
            ma_arrays[p['name']] = p['ma_array']
        self.stats['ma_arrays'] = ma_arrays
        if len(self.stats['name_scenario']) == 0: # some kind of error in the input
            self.stats['name_scenario'] = "unknown"
        i=1
        root = self.stats['name_scenario']
        dupe = True
        while dupe:
            dupe = False
            for st in self.statsList:
                if self.stats['name_scenario'] == st['name_scenario']:
                    self.stats['name_scenario'] = root + f"_{i}"
                    i+=1
                    dupe=True
                    break

        self.extract_generation()

        self.stats['st_id']=self.session_count
        self.statsList.append(self.stats)
        self.session_count += 1

    def init_training_session(self):
        self.scenario_players = {}
        self.nn_players = {}
        self.hands = []
        self.stats = {}
        self.stats['name_scenario'] = self.get_default_name_scenario()
        self.ma_count = 0
        # self.stats['generation'] = 0

    ## ##############################
    def extract_generation(self):
        generation_match = re.search("[.][0-9]*[.]", self.stats['name_scenario'])
        if generation_match:
            self.stats['generation'] = int(
                self.stats['name_scenario'][generation_match.start()+1:generation_match.end()-1]
                )
        else:
            generation_match = re.search("[.][0-9]*[.]", self.stats['params']['log_path'])
            if generation_match:
                self.stats['generation'] = int(
                    self.stats['params']['log_path'][generation_match.start()+1:generation_match.end()-1]
                    )
        if ('generation' in self.stats) and (self.stats['generation'] > 999):  # old, pre-convention name
            ## print(f"generation={self.stats['generation']}   name_scenario={self.stats['name_scenario']}    log_path={self.stats['params']['log_path']}")
            self.stats.pop('generation')

    ## ##############################
    def extract_param(self, key, params):
        if key in params:
            self.stats[key] = params[key]

    ## ##############################
    def is_session_start(line):
        return (("INPUT" in line) or ("learningGin execution at" in line) or ("Testing." in line))

    ## ##############################
    def parse_player_params(self, params):
        player_params = []
        for pid in (1,2):
            key = 'player' + str(pid)
            if key in params:
                pparams = params[key]
                pparams['pid'] = pid
                pparams['params_key'] = key
                player_params.append(pparams)

        if len(self.scenario_players) == 0:
            for pparams in player_params:
                if pparams['name'] in self.scenario_players:
                    print(f" ** WARNING: duplicate player name '{pparams['name']}'")
                else:
                    self.scenario_players[pparams['name']] = pparams
                self.scenario_players[pparams['name']]['wins'] = 0

        if len(self.nn_players) == 0:
            for pparams in self.scenario_players.values():
                if 'nn' in pparams:
                    dqn_params = pparams['nn']
                    for ppk in pparams.keys():
                        if ppk != 'nn':
                            dqn_params[ppk] = pparams[ppk]
                    if "layer_sizes" in dqn_params:
                        ls = dqn_params["layer_sizes"]
                        for lndx in range(len(ls)):
                            key = 'l' + str(lndx+1)
                            dqn_params[key] = int(ls[lndx])
                    dqn_params['total_reward'] = 0
                    dqn_params['ma_array'] = []
                    dqn_params['ma_window'] = []
                    for i in range(MA_SIZE):
                        dqn_params['ma_window'].append(0)   
                    self.nn_players[pparams['name']] = dqn_params

    ## ##############################
    def parse_params(self, line:(str)):
        params = eval(line[line.find('{'):])

        self.parse_player_params(params)

        self.extract_param('name_scenario', params)
        self.extract_param('timestamp', params)
        self.stats['params'] = params

    ## ##############################
    def parse_win_line(self, line):
            ## end of hand
            toks = line.split()
            hand_index = int(toks[1])
            winner = toks[3]
            tok_pad = 0
            if not winner == NO_WIN_NAME:
                tok_pad = gin.HAND_SIZE+1  # Hand: + cards
            if (len(toks)>9+tok_pad):
                ginscore1_owner = toks[9+tok_pad]
                ginscore1 = toks[10+tok_pad]
            else:
                ginscore1 = 0
            if (len(toks)>11+tok_pad):
                ginscore2_owner = toks[11+tok_pad]
                ginscore2 = toks[12+tok_pad]
            else:
                ginscore2 = 0
            total_reward1_owner = ""
            if (len(toks)>16+tok_pad):
                total_reward1_owner = toks[16+tok_pad]
                total_reward1   = toks[17+tok_pad]
            total_reward2_owner = ""
            if (len(toks)>18+tok_pad):
                total_reward2_owner = toks[18+tok_pad]
                total_reward2   = toks[19+tok_pad]
            tot_rew = []
            if len(total_reward1_owner)>0:
                tot_rew.append((total_reward1_owner,total_reward1))
            if len(total_reward2_owner)>0:
                tot_rew.append((total_reward2_owner,total_reward2))
            if not winner == NO_WIN_NAME:
                self.scenario_players[winner]['wins'] += 1
            hand_summary = {'hand_index': hand_index, 
                            'winner': winner, 
                            'ginscores': (ginscore1, ginscore2),
                            'total_reward': tot_rew,
                            'wins': (self.scenario_players[ginscore1_owner]['wins'],
                                     self.scenario_players[ginscore2_owner]['wins'])
                            }
            self.hands.append(hand_summary) 
                            
            ## moving average wins
            self.ma_count += 1
            for p in self.nn_players.values():
                if p['name'] == winner:
                    w = 1
                else:   
                    w = 0
                p['ma_window'][self.ma_count%MA_SIZE] = w
                if self.ma_count>MA_SIZE:
                    p['ma_array'].append(sum(p['ma_window']))                            

    ## ##############################
    def processLine(self, line:(str), include_partials:(bool)=False):
        
        if LearningLogParser.is_session_start(line) and len(self.stats)>0:
            if 'wins2' in self.stats or include_partials:
                self.save_training_session()
            self.init_training_session()
        if "Training.." in line:
            self.stats['mode']="train"
            self.stats['name_scenario'] += '.' + self.stats['mode']
        if "Testing.." in line:
            self.stats['mode']='test'
            self.stats['name_scenario'] += '.' + self.stats['mode']
        if "{'episodes':" in line:
            self.parse_params(line)
        if "Winner: " in line:
            ## end of hand
            self.parse_win_line(line)
        if "total_reward: [(" in line:
            self.stats['total_reward'] = eval(line[14:])
            for tw in self.stats['total_reward']:
                playerName = tw[0]
                playerTotal = tw[1]
                self.nn_players[playerName]['total_reward'] = playerTotal
        if "winMap: " in line:
            cpos = line.find(",")
            x = cpos-1
            while not line[x] == ' ':
                x-=1        
            self.stats['wins1'] = int(line[x:cpos])
            cpos +=1
            cpos = line[cpos:].find(",")+cpos
            x = cpos-1
            while not line[x] == ' ':
                x-=1        
            self.stats['wins2'] = int(line[x:cpos])
            if len(self.hands)>0:
                for p in self.nn_players.values():
                    p['wins_per_1000_hands'] = self.scenario_players[p['name']]['wins']*1000/len(self.hands)
                self.stats['wins_per_1000_hands_1'] = self.stats['wins1']*1000/len(self.hands)
                self.stats['wins_per_1000_hands_2'] = self.stats['wins2']*1000/len(self.hands)
            else:
                self.stats['wins_per_1000_hands_1'] = -1
                self.stats['wins_per_1000_hands_2'] = -1

    ## ##############################
    def parseLogs(self, filepath:(str), include_partials:(bool)=False): 

        start_time = time.time()
        self.filepath = filepath
        self.session_count = 0
        self.init_training_session()

        with open(filepath, 'r') as f:
            count_lines = 0
            for line in f:
                self.processLine(line)
                count_lines += 1
                if count_lines%10000 == 0:
                    sys.stdout.write(f"\rparsed {count_lines} lines in {time.time()-start_time:3.3f}s")
            sys.stdout.write("\n")
        
        # last (or only) stats
        if 'wins2' in self.stats or include_partials:
            self.save_training_session()

        self.score_stats = self.create_score_stats()

    ## ##############################
    def create_score_stats(self):
        score_stats={}
        count_scenarios = 0
        count_hands = 0
        tot1 = 0
        tot2 = 0
        totwpk1 = 0
        totwpk2 = 0
        min1 = 100000
        min2 = 100000
        max1 = -1
        max2 = -1
        minr = 100000
        maxr = -1
        for st in self.statsList:
            if 'wins2' in st:
                count_scenarios+=1
                count_hands += len(st['hands'])
                w1 = st['wins1']
                w2 = st['wins2']
                tot1+= w1
                tot2+= w2
                totwpk1 += st['wins_per_1000_hands_1']
                totwpk2 += st['wins_per_1000_hands_2']
                max1=max(max1,w1)
                max2=max(max2,w2)
                min1=min(min1,w1)
                min2=min(min2,w2)
                if w2 > 0:
                    ratio = w1/w2
                else: 
                    ratio = w1
                maxr = max(ratio, maxr)
                minr = min(ratio, minr)

                self.capture_cumulative_averages(st)

        score_stats['count_scenarios']=count_scenarios
        if count_scenarios == 0:
            return score_stats
        mean_wins_1 = tot1/count_scenarios
        mean_wins_2 = tot2/count_scenarios 
        score_stats['mean_wins_per_1000_hands_1']=totwpk1/count_scenarios
        score_stats['mean_wins_per_1000_hands_2']=totwpk2/count_scenarios
        score_stats['mean_wins_1']=mean_wins_1
        score_stats['mean_wins_2']=mean_wins_2
        score_stats['max_wins_1']=max1
        score_stats['max_wins_2']=max2
        score_stats['min_wins_1']=min1
        score_stats['min_wins_2']=min2
        score_stats['max_ratio']=maxr
        score_stats['min_ratio']=minr
        score_stats['count_hands']=count_hands
        for st in self.statsList:
            if 'wins2' in st:
                tot1 += (st['wins1']-mean_wins_1)**2
                tot2 += (st['wins2']-mean_wins_2)**2
        score_stats['std_wins_1']=math.sqrt(tot1/count_scenarios)
        score_stats['cv_wins_1']=math.sqrt(tot1/count_scenarios)/mean_wins_1
        score_stats['std_wins_2']=math.sqrt(tot2/count_scenarios)
        score_stats['cv_wins_2']=math.sqrt(tot2/count_scenarios)/mean_wins_2
        max_cum_len = 0
        for ca in self.cumulative_averages:
            max_cum_len = max(max_cum_len,len(ca))

        cumulative_average = []
        for i in range(max_cum_len):
            contributors = 0.0
            cumulative_average.append(0.0)
            for ca in self.cumulative_averages:
                if i < len(ca):
                    cumulative_average[i]+=ca[i]
                    contributors+=1
            if contributors>0:
                cumulative_average[i]/=contributors

        self.cumulative_average = cumulative_average
        score_stats['cumulative_average_slope']=(
                    cumulative_average[-1] - cumulative_average[0]
                                    )/len(cumulative_average)
        return score_stats

    def capture_cumulative_averages(self,st):
        cumu_nn_dict = {}
        for nnp in self.nn_players.values():
            cumu_nn_dict[nnp['name']+'_count'] = 0
            cumu_nn_dict[nnp['name']] = []
        for hand in st['hands']:
            ndx = int(hand['hand_index'])
            if hand['winner'] in cumu_nn_dict:
                cumu_nn_dict[hand['winner']+'_count']+=1
            for nnp in self.nn_players.values():
                cumu_nn_dict[nnp['name']].append(cumu_nn_dict[nnp['name']+'_count'])

        for nnp in self.nn_players.values():
            self.cumulative_averages.append(cumu_nn_dict[nnp['name']])                    

    def format_stats(stats):
        rez=""
        for key in stats.keys():
            if not key == "hands":
                rez+= f"{key}={stats[key]}\n"
        return rez

    def format_score_stats(score_stats):
        rez=""
        for key in score_stats.keys():
            rez += f"{key}={score_stats[key]}\n"
        return rez

## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
## ##############################
