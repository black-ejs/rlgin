#!/usr/bin/bash
# run a training cycle with the supplied params and weights
## this script is usually invoked with "nohup" or the equivalent 
#set -x


CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S`
echo "############# ${CURRENT_SCRIPT_NAME} #################"
echo RLGIN TRAINING session started at "${TIMESTAMP}"

CONTROL_DIR=${1:-$PWD}
MODEL_NICKNAME=`basename ${CONTROL_DIR}`
RUN_DIR=${RLGIN_BATCH_LOCAL_REPO}
PARAMS_SOURCE_ROOT=${CONTROL_DIR}
WEIGHTS_DIR=${CONTROL_DIR}/weights
LOGS_DIR=${CONTROL_DIR}/logs
PROCESS_WEIGHTS_PATH=${WEIGHTS_DIR}/weights.h5

echo "############# ${CURRENT_SCRIPT_NAME} changing directories to ${RUN_DIR}...."
if [[ -d ${RUN_DIR} ]]
then
    cd "${RUN_DIR}"
    echo "current working directory = {$PWD}"
else
	echo "#### ${CURRENT_SCRIPT_NAME} code repo \"${RUN_DIR}\" not found"
	echo "#### ${CURRENT_SCRIPT_NAME} exiting code 9"
    ## should just make one -- TBD
    exit 9
fi

echo "############# ${CURRENT_SCRIPT_NAME} locating latest-generation weights...."
INPUT_GENERATION_NUMBER=`ls ${PROCESS_WEIGHTS_PATH}.* | grep "[.][0-9]*$" \
            | awk '{p=split($0,aa,"[.]"); print aa[p]}' | sort -n | tail -1`
OUTPUT_GENERATION_NUMBER=$((INPUT_GENERATION_NUMBER+1))

echo "#### ${CURRENT_SCRIPT_NAME} setting up logging and weights management...."
NAME_SCENARIO="trainGin_${MODEL_NICKNAME}.${OUTPUT_GENERATION_NUMBER}"
LOGFILE="${LOGS_DIR}/${NAME_SCENARIO}.${TIMESTAMP}.log"
OUTPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${OUTPUT_GENERATION_NUMBER}"
INPUT_WEIGHTS="${PROCESS_WEIGHTS_PATH}.${INPUT_GENERATION_NUMBER}"

echo "-----------------------------"
echo CONTROL_DIR=${CONTROL_DIR}
echo RUN_DIR=${RUN_DIR}
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo NAME_SCENARIO=${NAME_SCENARIO}
echo LOGFILE=${LOGFILE}
echo PARAMS_SOURCE_ROOT={$PARAMS_SOURCE_ROOT}
echo INPUT_GENERATION_NUMBER=${INPUT_GENERATION_NUMBER}
echo OUTPUT_GENERATION_NUMBER=${OUTPUT_GENERATION_NUMBER}
echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
echo OUTPUT_WEIGHTS=${OUTPUT_WEIGHTS}
echo "-----------------------------"

echo "############# ${CURRENT_SCRIPT_NAME} copying input weights...."
cp "${INPUT_WEIGHTS}" "${PROCESS_WEIGHTS_PATH}"

echo "############# ${CURRENT_SCRIPT_NAME} getting "${MODEL_NICKNAME}"-specific params...."
mkdir -p ${RUN_DIR}/params
PARAMS_SOURCE=${PARAMS_SOURCE_ROOT}/ginDQNParameters.py.${MODEL_NICKNAME}
FIXUP=`echo ${MODEL_NICKNAME} | awk '{p=$0; gsub("[.]","_",p); print p;}'`
PARAMS_MODULE=params/ginDQNParameters_${FIXUP}
PARAMS_TARGET=${RUN_DIR}/${PARAMS_MODULE}.py
cp ${PARAMS_SOURCE} ${PARAMS_TARGET} 

echo "#### ${CURRENT_SCRIPT_NAME} checking python..."
which python
python --version

# 4/2023 conda broken in certain sub-shell situations, including ssh/nohup/&
echo "#### ${CURRENT_SCRIPT_NAME} confirming conda"
which conda
if [[ -e "/opt/conda/etc/profile.d/conda.sh" ]]
then
	source /opt/conda/etc/profile.d/conda.sh
fi
conda activate

echo 

CMD_ARGS="--name_scenario ${NAME_SCENARIO} \
            --logfile ${LOGFILE}  \
        	--params_module ${PARAMS_MODULE} \
            --weights_path_2 ${PROCESS_WEIGHTS_PATH} \
            --generation ${OUTPUT_GENERATION_NUMBER}"

echo "############# ${CURRENT_SCRIPT_NAME} checking for parameter overrides...."
echo RLGIN_BATCH_JP_LEARNING_RATE=${RLGIN_BATCH_JP_LEARNING_RATE}
echo RLGIN_BATCH_JP_GAMMA=${RLGIN_BATCH_JP_GAMMA}
if [[ X${RLGIN_BATCH_JP_LEARNING_RATE}X != XX ]]
then
    CMD_ARGS="${CMD_ARGS}""  --learning_rate_2 ${RLGIN_BATCH_JP_LEARNING_RATE}"
fi
if [[ X${RLGIN_BATCH_JP_GAMMA}X != XX ]]
then
    CMD_ARGS="${CMD_ARGS}""  --gamma_2 ${RLGIN_BATCH_JP_GAMMA}"
fi

echo "############# ${CURRENT_SCRIPT_NAME} launching training process at `date -u +%Y-%m-%d_%H-%M-%S` ..."
echo CMD_ARGS="${CMD_ARGS}"
python learningGin.py ${CMD_ARGS}
echo "############# ${CURRENT_SCRIPT_NAME} training process completed at `date -u +%Y-%m-%d_%H-%M-%S`"

echo "############# ${CURRENT_SCRIPT_NAME} capturing post-training weights to ${OUTPUT_WEIGHTS}"
cp ${PROCESS_WEIGHTS_PATH}.post_training "${OUTPUT_WEIGHTS}"

echo "############# ${CURRENT_SCRIPT_NAME} comparing output and input weights..."
if cmp "${INPUT_WEIGHTS}" "${OUTPUT_WEIGHTS}"; then echo "*** WARNING: NO DIFFERENCE BETWEEN ${INPUT_WEIGHTS} and ${OUTPUT_WEIGHTS}"; fi

cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}
ENDTIME=`date -u +%Y-%m-%d_%H-%M-%S`
echo "############# ${CURRENT_SCRIPT_NAME} completed at ${ENDTIME} ##################"

