import re
import sys
import os
from statistics import mean


class Tgt_Processor:
    ID_PATTERN="[A-Za-z]+[0-9]+[.][0-9]+[.][0-9]"
    ID_LOCATE_PATTERN="Gin_"+ID_PATTERN+"[.]202[3456789]"

    def output_series_score(self, nick:str):
        if len(nick)<1:
            return
        
        outline = f"{nick} overall_score={self.series_total_score:.3f}  avg_score={self.series_total_score/self.series_score_count:.3f}"
        print(outline)
        
        with open(self.output_file, 'a') as o: 
            print(outline,file=o)

        self.series_total_score = 0
        self.series_score_count = 0

    def output(self):
        if self.hand_count == 0:
            return
        
        rewards=""
        wins=""
        for phase in self.rewards:
            if phase == "scratch":
                continue
            rewards += f"{phase}:{mean(self.rewards[phase]):.3f}/"
        for phase in self.wins:
            if phase == "scratch":
                continue
            wins += f"{phase}:{mean(self.wins[phase]):3.1f}/"

        avg_time=self.tot_time/self.hand_count;

        if 'train' in self.rewards:
            outline = f"{self.run_id.ljust(14)} rewards={rewards[:-1]}, wins={wins[:-1]}, score:{self.score():3.2f}"
        elif self.hand_count < 5000:
            secs_to_go = int((5000-self.hand_count) * (avg_time/1000))
            hrs_to_go = secs_to_go/3600
            outline =  (f"{self.run_id.ljust(14)} {self.hand_count} hands, avg time={avg_time:6.2f}, " +
                        f"{secs_to_go}s/{hrs_to_go:.2f}h to turnover @{self.host}")
        print(outline)
        with open(self.output_file, 'a') as o: 
            print(outline,file=o)

        self.series_total_score += self.score()
        self.series_score_count += 1

    def score(self):
        if not 'test' in self.rewards:
            return 0

        if 'pretest' in self.rewards:
            base = mean(self.rewards['pretest'])
        elif 'train' in self.rewards:
            base = mean(self.rewards['train'])
        else:
            return 0
        
        score = mean(self.rewards['test']) - base

        return score

    def new_logfile(self):
        self.tot_time=0
        self.hand_count=0
        self.logfile=""
        self.host =""
        self.phase=""
        self.run_id=""
        self.wins={}
        self.rewards={}

    def process(self, input_file:str, output_file:str):

        self.output_file = output_file
        self.series_nick = ""
        self.series_total_score = 0
        self.series_score_count = 0
        self.new_logfile()

        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        with open(input_file, 'r') as tgt_in: 
            lines = tgt_in.readlines()

        for line in lines:
            self.process_line(line)

        # final ourpur
        if self.tot_time>0:
            self.output()
            self.output_series_score(self.series_nick)

    def process_line(self,line:str):
        toks=line.split()
        if line.find("@rb-")>-1:
            if self.tot_time>0:
                self.output()
            self.new_logfile()
            pos=line.find("@rb-")
            self.logfile = line[:pos-1:]
            self.host = line[pos+1:-1]
            self.run_id = self.logfile
            match = re.search(self.ID_PATTERN,line)
            if not match == None:
                end=match.span()[1]
                while line[end].isdigit():
                    end+=1
                self.run_id = line[match.span()[0]:end]
            prev_nick=self.series_nick
            if "scratchGin" in self.logfile:
                self.series_nick = self.run_id[:self.run_id.find(".")]
            else:
                self.series_nick = self.run_id[:-(self.run_id[::-1].find("."))-1]
            if not prev_nick == self.series_nick:
                self.output_series_score(prev_nick)
            # print(f"{self.series_nick}") 
            # print(f"{self.run_id}") 
            # print(line[:-1])
        elif line.find("Game")>-1:
            self.hand_count=int(toks[1])
            if toks[3]=="nobody":  
                time=toks[7]
            else:
                time=toks[12]
            self.tot_time += float(time)
        elif line.find("ing...")>-1:
            self.phase=toks[0][:-6].lower()
            self.tot_time=0
        elif line.find("total_reward")>-1:
            reward=toks[2][:-2]
            if not self.phase in self.rewards:
                self.rewards[self.phase] = []
            self.rewards[self.phase].append(float(reward))
        elif line.find("winMap")>-1:
            wins=toks[4][:-1]
            if not self.phase in self.wins:
                self.wins[self.phase] = []
            self.wins[self.phase].append(int(wins))


if __name__ == "__main__":
    if len(sys.argv)>1:
        input_file = sys.argv[1]
    else:
        input_file = "/Users/edward/tgt2.sh.out.1"
    output_file = f"{input_file}.x"
    if len(sys.argv)>2:
        output_file = sys.argv[2]

    Tgt_Processor().process(input_file,output_file)


