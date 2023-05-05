#!/usr/bin/bash 
# create a model from scratch and train it, using the supplied params
## this script is usually invoked with "nohup" or the equivalent 
#set -x  
 
SCRATCH_ID=${1:-0}  
CONTROL_DIR=${2:-$PWD}
MODEL_NICKNAME=`basename ${CONTROL_DIR}`
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S` 
echo "#############   ${CURRENT_SCRIPT_NAME}  ####################"
echo RLGIN NEW-MODEL scratch session started at "${TIMESTAMP}" 
 
MODEL_NICKNAME=`basename ${CONTROL_DIR}`
RUN_DIR=${RLGIN_BATCH_LOCAL_REPO}
PARAMS_SOURCE_ROOT=${CONTROL_DIR}
WEIGHTS_DIR=${CONTROL_DIR}/weights
LOGS_DIR=${CONTROL_DIR}/logs
 
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

echo "#### ${CURRENT_SCRIPT_NAME} setting up logging and weights management...."
NAME_SCENARIO="scratchGin_${MODEL_NICKNAME}.${SCRATCH_ID}" 
LOGFILE="${LOGS_DIR}/${NAME_SCENARIO}.${TIMESTAMP}.log" 
OUTPUT_WEIGHTS="${WEIGHTS_DIR}/${NAME_SCENARIO}.${TIMESTAMP}.h5" 
INPUT_WEIGHTS="${WEIGHTS_DIR}/${NAME_SCENARIO}.h5" 
 
echo "-----------------------------" 
echo CONTROL_DIR=${CONTROL_DIR}
echo RUN_DIR=${RUN_DIR}
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo NAME_SCENARIO=${NAME_SCENARIO} 
echo CONTROL_DIR=${CONTROL_DIR}
echo LOGFILE=${LOGFILE}
echo PARAMS_SOURCE_ROOT=${PARAMS_SOURCE_ROOT}
echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
echo OUTPUT_WEIGHTS=${OUTPUT_WEIGHTS} 
echo "-----------------------------" 
  
echo "#### ${CURRENT_SCRIPT_NAME} getting ${MODEL_NICKNAME}-specific params...."
mkdir -p ${RUN_DIR}/params
PARAMS_SOURCE=${PARAMS_SOURCE_ROOT}/{RLGIN_}
FIXUP=`echo ${SCRATCH_ID} | awk '{p=$0; gsub("[.]","_",p); print p;}'`
PARAMS_MODULE=params/ginDQNParameters_${MODEL_NICKNAME}_${FIXUP}
PARAMS_TARGET=${RUN_DIR}/${PARAMS_MODULE}.py
cp ${PARAMS_SOURCE} ${PARAMS_TARGET} 
 
echo "#### ${CURRENT_SCRIPT_NAME} cleaning up fram any previous runs..."
[ -e ${WEIGHTS_PATH_2}.post_training ] && rm ${WEIGHTS_PATH_2}.h5.post_training 
 
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
            --weights_path_2 ${WEIGHTS_DIR}/${NAME_SCENARIO}.h5"

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

echo "#### ${CURRENT_SCRIPT_NAME} launching scratchGin process..."
echo CMD_ARGS="${CMD_ARGS}"
python learningGin.py ${CMD_ARGS}
echo "#### ${CURRENT_SCRIPT_NAME} scratchGin process completed"
 
echo "#### ${CURRENT_SCRIPT_NAME} capturing post-training weights to ${OUTPUT_WEIGHTS}"
[ -e ${WEIGHTS_PATH_2}.post_training ] && mv ${WEIGHTS_PATH_2}.post_training "${OUTPUT_WEIGHTS}" 
 
cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}
ENDTIME=`date -u +%Y-%m-%d_%H-%M-%S` 
echo "############# ${CURRENT_SCRIPT_NAME} completed at ${ENDTIME} ##################"




