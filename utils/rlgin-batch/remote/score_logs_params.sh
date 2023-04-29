#!/bin/bash

`dirname $0`/score_logs.sh $1 $2 $3 | sort -rn | awk '

{
	print "----- " $0
	wins = $1
	logfile = $2
	nick=substr(logfile,index(logfile,"Gin_")+4,3)
	params_spec="ginDQNParameters.py." nick ".train"
	train_or_scratch = "TRAIN"
	id=substr($0, index(logfile,"_" nick)+1)
	split(id,segs,"[.]")
	id=segs[1] "." segs[2] "." segs[3]
	scratch_driver_id = segs[1] "." segs[2] # TRAIN only
	weights_spec=substr(logfile,1,length(logfile)-4) ".h5"
	train_generations = 10
	
	job_param = "WEIGHTS_WINS=" wins
	job_param = job_param ":SERIES_NICKNAME=" nick ":PARAMS_SPEC=" params_spec ":TRAIN_OR_SCRATCH=" train_or_scratch 
	job_param = job_param ":SCRATCH_DRIVER_ID=" scratch_driver_id ":WEIGHTS_SPEC=" weights_spec 
	job_param = job_param ":TRAIN_GENERATIONS=" train_generations 
	print job_param
}
'

