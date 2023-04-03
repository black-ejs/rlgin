##!/usr/bin/bash
## run a test cycle, this script is usually invoked with "nohup" or the equivalent
## place your desired weights into "${RUN_DIR}/${PROCESS_WEIGHTS_PATH}.0

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S`
echo '#####################################################'
echo RLGIN TRAINING session started at "${TIMESTAMP}"

MODEL_NICKNAME=${PWD##*/}
RUN_DIR=rlgin
PROCESS_WEIGHTS_PATH=weights/weights.h5

echo changing directories to "${RUN_DIR}"....
cd "${RUN_DIR}"
echo "current working directory = {$PWD}"

echo locating latest-generation weights....
INPUT_GENERATION_NUMBER=`ls ${PROCESS_WEIGHTS_PATH}.* | grep "[0-9]$" | cut -d. -f3 | sort -n | tail -1`
INPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${INPUT_GENERATION_NUMBER}"
OUTPUT_GENERATION_NUMBER=$((INPUT_GENERATION_NUMBER+1))
OUTPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${OUTPUT_GENERATION_NUMBER}"
NAME_SCENARIO="trainGin_${MODEL_NICKNAME}.${OUTPUT_GENERATION_NUMBER}"
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
cp "${INPUT_WEIGHTS}" "${PROCESS_WEIGHTS_PATH}"

echo updating code base....
git pull
echo getting "${MODEL_NICKNAME}"-specific params....
cp ../ginDQNParameters.py."${MODEL_NICKNAME}" ginDQNParameters.py
echo cleaning up fram any previous runs...
[ -e "${PROCESS_WEIGHTS_PATH}.post_training" ] && rm ${PROCESS_WEIGHTS_PATH}.post_training

echo launching training process at `date -u +%Y-%m-%d_%H-%M-%S` ...
python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}" --generation "${OUTPUT_GENERATION_NUMBER}"
echo training process completed at `date -u +%Y-%m-%d_%H-%M-%S`

echo capturing post-training weights...
cp ${PROCESS_WEIGHTS_PATH}.post_training "${OUTPUT_WEIGHTS}"

echo comparing output and input weights
if cmp "${INPUT_WEIGHTS}" "${OUTPUT_WEIGHTS}"; then echo "*** WARNING: NO DIFFERENCE BETWEEN ${INPUT_WEIGHTS} and ${OUTPUT_WEIGHTS}"; fi

cd ..
echo '#####################################################'

