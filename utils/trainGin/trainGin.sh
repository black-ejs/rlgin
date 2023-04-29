#!/usr/bin/bash
# run a training cycle, this script is usually invoked with "nohup" or the equivalent
# place your desired weights into "${RUN_DIR}/${PROCESS_WEIGHTS_PATH}.0

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S`
echo "############# ${CURRENT_SCRIPT_NAME} #################"
echo RLGIN TRAINING session started at "${TIMESTAMP}"

MODEL_NICKNAME=${PWD##*/}
CONTROL_DIR=${PWD}
RUN_DIR=${RLGIN_BATCH_LOCAL_REPO}
PARAMS_LOC=${CONTROL_DIR}
WEIGHTS_DIR=${CONTROL_DIR}/weights
LOGS_DIR=${CONTROL_DIR}/logs
PROCESS_WEIGHTS_PATH=${WEIGHTS_DIR}/weights.h5

echo "############# ${CURRENT_SCRIPT_NAME} changing directories to ${RUN_DIR}...."
cd "${RUN_DIR}"
echo "current working directory = {$PWD}"

echo "############# ${CURRENT_SCRIPT_NAME} locating latest-generation weights...."
INPUT_GENERATION_NUMBER=`ls ${PROCESS_WEIGHTS_PATH}.* | grep "[.][0-9]*$" | cut -d. -f3 | sort -n | tail -1`
INPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${INPUT_GENERATION_NUMBER}"
OUTPUT_GENERATION_NUMBER=$((INPUT_GENERATION_NUMBER+1))
OUTPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${OUTPUT_GENERATION_NUMBER}"
NAME_SCENARIO="trainGin_${MODEL_NICKNAME}.${OUTPUT_GENERATION_NUMBER}"
LOGFILE="${LOGS_DIR}/${NAME_SCENARIO}.${TIMESTAMP}.log"

echo "-----------------------------"
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo NAME_SCENARIO=${NAME_SCENARIO}
echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
echo INPUT_GENERATION_NUMBER=${INPUT_GENERATION_NUMBER}
echo OUTPUT_GENERATION_NUMBER=${OUTPUT_GENERATION_NUMBER}
echo OUTPUT_WEIGHTS=${OUTPUT_WEIGHTS}
echo LOGFILE=${LOGFILE}
echo "-----------------------------"

echo "############# ${CURRENT_SCRIPT_NAME} copying input weights...."
cp "${INPUT_WEIGHTS}" "${PROCESS_WEIGHTS_PATH}"

echo "############# ${CURRENT_SCRIPT_NAME} getting "${MODEL_NICKNAME}"-specific params...."
mkdir -p ${RUN_DIR}/params
echo "HELLO" > ${RUN_DIR}/params/HELLO
PARAMS_SOURCE=${PARAMS_LOC}/ginDQNParameters.py.${MODEL_NICKNAME}
FIXUP=`echo ${MODEL_NICKNAME} | awk '{p=$0; gsub("[.]","_",p); print p;}'`
PARAMS_MODULE=params/ginDQNParameters_${FIXUP}
PARAMS_TARGET=${RUN_DIR}/${PARAMS_MODULE}.py
if [[ -d ${RUN_DIR} ]]
then
    echo ls ${PARAMS_SOURCE}
    ls ${PARAMS_SOURCE}
    echo "cp ${PARAMS_SOURCE} ${PARAMS_TARGET}"
	cp ${PARAMS_SOURCE} ${PARAMS_TARGET} 
    echo "ls -latr ${RUN_DIR}"
    ls -latr ${RUN_DIR}
    echo ls -latr ${RUN_DIR}/params
    ls -latr ${RUN_DIR}/params
    echo ls ${PARAMS_TARGET}
    ls ${PARAMS_TARGET}
else
	echo "#### ${CURRENT_SCRIPT_NAME} ${RUN_DIR} not found, this could be a problem...."
fi

echo "############# ${CURRENT_SCRIPT_NAME} launching training process at `date -u +%Y-%m-%d_%H-%M-%S` ..."
python learningGin.py \
            --name_scenario "${NAME_SCENARIO}" \
            --logfile "${LOGFILE}" \
        	--params_module ${PARAMS_MODULE} \
            --weightsfile_2 "${PROCESS_WEIGHTS_PATH}" \
            --generation "${OUTPUT_GENERATION_NUMBER}"
echo training process completed at `date -u +%Y-%m-%d_%H-%M-%S`

echo "############# ${CURRENT_SCRIPT_NAME} capturing post-training weights..."
cp ${PROCESS_WEIGHTS_PATH}.post_training "${OUTPUT_WEIGHTS}"

echo "############# ${CURRENT_SCRIPT_NAME} comparing output and input weights..."
if cmp "${INPUT_WEIGHTS}" "${OUTPUT_WEIGHTS}"; then echo "*** WARNING: NO DIFFERENCE BETWEEN ${INPUT_WEIGHTS} and ${OUTPUT_WEIGHTS}"; fi

cd ${CONTROL_DIR}
echo '############# ${CURRENT_SCRIPT_NAME} completed at `date -u +%Y-%m-%d %H:%M:%S` ##################'

