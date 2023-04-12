#!/usr/bin/bash 
## this script is usually invoked with "nohup" or the equivalent 
set -x
 
SCRATCH_ID=${1:-0}  

TIMESTAMP=`date -u +%Y-%m-%d_%H%M%S` 
echo '#####################################################' 
echo RLGIN NEW-MODEL scratch session started at "${TIMESTAMP}" 
 
MODEL_NICKNAME=${PWD##*/} 
RUN_DIR=rlgin 
 
echo changing directories to "${RUN_DIR}".... 
cd "${RUN_DIR}" 
echo "current working directory = {$PWD}" 
 
echo setting up logging and weights management.... 
LOGPATH="logs" 
NAME_SCENARIO="scratchGin_${MODEL_NICKNAME}.${SCRATCH_ID}" 
LOGROOT="${NAME_SCENARIO}" 
LOGFILE="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.log" 
CONSOLE_OUTPUT="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.sysout" 
WEIGHTSPATH="weights" 
WEIGHTSROOT="${LOGROOT}" 
WEIGHTS_OUTPUT_FILE="${WEIGHTSPATH}/${WEIGHTSROOT}.${TIMESTAMP}.h5" 
 
echo "-----------------------------" 
echo MODEL_NICKNAME="${MODEL_NICKNAME}" 
echo NAME_SCENARIO="${NAME_SCENARIO}" 
echo LOGFILE="${LOGFILE}" 
echo WEIGHTS_OUTPUT_FILE="${WEIGHTS_OUTPUT_FILE}" 
echo "-----------------------------" 
 
echo updating code base.... 
git pull 
 
echo getting "${MODEL_NICKNAME}"-specific params.... 
cp ../ginDQNParameters.py.${MODEL_NICKNAME} ginDQNParameters.py 
 
echo cleaning up fram any previous runs... 
[ -e weights/weights.*.h5.post_training ] && rm weights/weights.h5.post_training 
 
echo checking python...
which python
python --version

# 4/2023 conda broken in certain sub-shell situations, including ssh/nohup/&
echo confirming conda
which conda
if [[ -e "/opt/conda/etc/profile.d/conda.sh" ]]
then
	source /opt/conda/etc/profile.d/conda.sh
fi
conda activate

echo launching scratchGin process... 
python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}" 
echo scratchGin process completed 
 
echo capturing weights to "${WEIGHTS_OUTPUT_FILE}" ... 
[ -e weights/weights.*.h5.post_training ] && cp weights/weights.*.h5.post_training "${WEIGHTS_OUTPUT_FILE}" 
 
cd .. 
echo '#####################################################'




