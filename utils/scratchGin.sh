##!/usr/bin/bash
## this script is usually invoked with "nohup" or the equivalent

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
NAME_SCENARIO="scratchGin_${MODEL_NICKNAME}.0"
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
[ -e "weights/weights.h5.post_training" ] && rm weights/weights.h5.post_training

echo launching learning process...
python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}"
echo learning process completed

echo capturing weights to "${WEIGHTS_OUTPUT_FILE}" ...
[ -e "weights/weights.h5.post_training" ] && cp weights/weights.h5.post_training "${WEIGHTS_OUTPUT_FILE}"

cd ..
echo '#####################################################'


