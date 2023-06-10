import re
import sys
import os
from statistics import mean

class Tgt_Processor:
    ID_PATTERN="[A-Za-z]+[0-9]+[.][0-9]+[.][0-9]"
    ID_LOCATE_PATTERN="Gin_"+ID_PATTERN+"[.]202[3456789]"

    def new_logfile(self, logfile:str=""):
        self.logfile=logfile
        if len(logfile)>0:
            self.run_id, self.series_nick = self.parse_run_id(logfile)
        else:
            self.run_id, self.series_nick = ("","")
        self.tot_time = {}
        self.tot_time['train'] = 0
        self.tot_time['test'] = 0
        self.tot_time['pre'] = 0
        self.tot_time['scratch'] = 0
        self.hand_count=0
        self.host =""
        self.phase=""
        self.wins={}
        self.rewards={}

    def process(self, input_file:str, output_file:str):

        self.output_file = output_file
        self.series_nick = ""
        self.series_total_score = 0
        self.series_score_count = 0

        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        with open(input_file, 'r') as tgt_in: 
            lines = tgt_in.readlines()

        match = re.search(self.ID_LOCATE_PATTERN,input_file)
        if not match == None:
            self.new_logfile(input_file)
        else:
            self.new_logfile()

        for line in lines:
            self.process_line(line)

        # final output
        if len(self.phase)>0 and self.tot_time[self.phase]>0:
            self.output()
            if not input_file == self.logfile:
                self.output_series_score(self.series_nick)

    def process_line(self,line:str):
        toks=line.split()
        if line.find("@rb-")>-1:
            if len(self.phase)>0 and self.tot_time[self.phase]>0:
                self.output()

            prev_nick = self.series_nick
            pos=line.find("@rb-")
            logfile = line[:pos-1:]
            self.new_logfile(logfile)
            self.host = line[pos+1:-1]
            if len(prev_nick) > 0 and (not (prev_nick == self.series_nick)):
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
            self.tot_time[self.phase] += float(time)
        elif line.find("ing...")>-1:
            self.phase=toks[0][:-6].lower()
            if self.phase == "pretest":
                self.phase="pre"
            self.tot_time[self.phase]=0
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

    def parse_run_id(self,logfile:str):
        run_id = logfile
        match = re.search(self.ID_PATTERN,logfile)
        if not match == None:
            end=match.span()[1]
            while logfile[end].isdigit():
                end+=1
            run_id = logfile[match.span()[0]:end]

        if "scratchGin" in self.logfile:
            series_nick = run_id[:run_id.find(".")]
        else:
            series_nick = run_id[:-(run_id[::-1].find("."))-1]

        return run_id, series_nick

    def output_series_score(self, nick:str):
        if len(nick)<1:
            return
        
        if self.series_score_count==0:
            self.series_score_count=1
        outline = f"{nick} overall_score={self.series_total_score:.3f}  avg_score={self.series_total_score/self.series_score_count:.3f}"
        print(outline)
        
        with open(self.output_file, 'a') as o: 
            print(outline,file=o)

        self.series_total_score = 0
        self.series_score_count = 0

    def output(self):
        if self.hand_count == 0:
            return
        
        if 'train' in self.rewards:
            outline = self.logfile_summary()
        elif self.hand_count < 5000:
            outline = self.logfile_progress_summary()

        print(outline)
        with open(self.output_file, 'a') as o: 
            print(outline,file=o)

        self.series_total_score += self.score_logfile()
        self.series_score_count += 1

    def logfile_summary(self):
        rewards=""
        wins=""
        avg_time=self.tot_time['train']/self.hand_count

        for phase in self.rewards:
            if phase == "scratch":
                continue
            rewards += f"{phase}:{mean(self.rewards[phase]):.3f}/"

        for phase in self.wins:
            if phase == "scratch":
                continue
            wins += f"{phase}:{mean(self.wins[phase]):3.1f}/"

        summary = f"{self.run_id.ljust(14)} r={rewards[:-1]}, w={wins[:-1]}, score:{self.score_logfile():3.2f}  tavg: {avg_time:3.2f}"
        return summary

    def logfile_progress_summary(self):
        avg_time=self.tot_time[self.phase]/self.hand_count
        secs_to_go = int((5000-self.hand_count) * (avg_time/1000))
        hrs_to_go = secs_to_go/3600
        summary =  (f"{self.run_id.ljust(14)} {self.hand_count} hands, avg time={avg_time:6.2f}, " +
                    f"{secs_to_go}s/{hrs_to_go:.2f}h to turnover @{self.host}")
        return summary

    def score_logfile(self):
        if not 'test' in self.rewards:
            return 0

        if 'pre' in self.rewards:
            base = mean(self.rewards['pre'])
        elif 'train' in self.rewards:
            base = mean(self.rewards['train'])
        else:
            return 0
        
        score = mean(self.rewards['test']) - base

        return score

if __name__ == "__main__":
    if len(sys.argv)>1:
        input_file = sys.argv[1]
    else:
        input_file = "/Users/edward/tgt2.sh.out.1"
        #input_file = "/Users/edward/Documents/dev/projects/BLG/scratch/analysis/BLG22/logs/scratchGin_BLG22.22.5.2023-06-10_05-23-27.log"
    output_file = f"{input_file}.x"
    if len(sys.argv)>2:
        output_file = sys.argv[2]

    Tgt_Processor().process(input_file,output_file)


