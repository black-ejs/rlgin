##!/usr/bin/bash
## run a test cycle, this script is usually invoked with "nohup" or the equivalent

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S`
echo '#####################################################'
echo RLGIN TRAINING session started at "${TIMESTAMP}"

MODEL_NICKNAME=${PWD##*/}
RUN_DIR=rlgin

echo changing directories to "${RUN_DIR}"....
cd "${RUN_DIR}"
echo "current working directory = {$PWD}"

echo locating latest-generation weights....
INPUT_GENERATION_NUMBER=`ls weights/weights.h5.* | grep "[0-9]$" | cut -d. -f3 | sort -n | tail -1`
INPUT_WEIGHTS="weights/weights.h5.${INPUT_GENERATION_NUMBER}"
OUTPUT_GENERATION_NUMBER=$((INPUT_GENERATION_NUMBER+1))
OUTPUT_WEIGHTS="weights/weights.h5.${OUTPUT_GENERATION_NUMBER}"
NAME_SCENARIO="learningGin_${MODEL_NICKNAME}.${OUTPUT_GENERATION_NUMBER}"
LOGFILE="logs/${NAME_SCENARIO}.${TIMESTAMP}.log"

echo "-----------------------------"
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo NAME_SCENARIO=${NAME_SCENARIO}
echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
echo INPUT_GENERATION_NUMBER=${INPUT_GENERATION_NUMBER}
echo OUTPUT_GENERATION_NUMBER=${OUTPUT_GENERATION_NUMBER}
echo OUTPUT_WEIGHTS=${OUTPUT_WEIGHTS}
echo LOGFILE=${LOGFILE}
echo "-----------------------------"

echo copying input weights....
cp "${INPUT_WEIGHTS}" weights/weights.h5

echo updating code base....
git pull
echo getting "${MODEL_NICKNAME}"-specific params....
cp ../ginDQNParameters.py."${MODEL_NICKNAME}" ginDQNParameters.py
echo cleaning up fram any previous runs...
[ -e "weights/weights.h5.post_training" ] && rm weights/weights.h5.post_training
echo launching learning process...
python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}" 
echo learning process completed

echo capturing post-training weights...
cp weights/weights.h5.post_training "${OUTPUT_WEIGHTS}"

echo comparing output and input weights
if cmp "${INPUT_WEIGHTS}" "${OUTPUT_WEIGHTS}"; then echo "*** WARNING: NO DIFFERENCE BETWEEN ${INPUT_WEIGHTS} and ${OUTPUT_WEIGHTS}"; fi

cd ..
echo '#####################################################'

