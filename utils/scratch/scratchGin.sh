#!/usr/bin/bash 
## this script is usually invoked with "nohup" or the equivalent 
set -x
 
SCRATCH_ID=${1:-0}  
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

TIMESTAMP=`date -u +%Y-%m-%d_%H%M%S` 
echo "#############   ${CURRENT_SCRIPT_NAME}  ####################"
echo RLGIN NEW-MODEL scratch session started at "${TIMESTAMP}" 
 
MODEL_NICKNAME=${PWD##*/} 
RUN_DIR=${RLGIN_BATCH_LOCAL_REPO}
LOCAL_REPO=${RLGIN_BATCH_LOCAL_REPO}
PARAMS_LOC=$(pwd)
 
echo "#### ${CURRENT_SCRIPT_NAME} setting up logging and weights management...."
LOGPATH="$(pwd)/logs" 
NAME_SCENARIO="scratchGin_${MODEL_NICKNAME}.${SCRATCH_ID}" 
LOGROOT="${NAME_SCENARIO}" 
LOGFILE="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.log" 
CONSOLE_OUTPUT="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.sysout" 
WEIGHTSPATH="$(pwd)/weights" 
WEIGHTSROOT="${LOGROOT}" 
WEIGHTS_OUTPUT_FILE="${WEIGHTSPATH}/${WEIGHTSROOT}.${TIMESTAMP}.h5" 
 
echo "-----------------------------" 
echo MODEL_NICKNAME="${MODEL_NICKNAME}" 
echo NAME_SCENARIO="${NAME_SCENARIO}" 
echo LOGFILE="${LOGFILE}" 
echo WEIGHTS_OUTPUT_FILE="${WEIGHTS_OUTPUT_FILE}" 
echo PARAMS_LOC="${PARAMS_LOC}" 
echo "-----------------------------" 
  
echo "#### ${CURRENT_SCRIPT_NAME} getting ${MODEL_NICKNAME}-specific params...."
if [ ! -d ${RUN_DIR}/params ]
then
	mkdir -p ${RUN_DIR}/params
fi
PARAMS_SOURCE=${PARAMS_LOC}/ginDQNParameters.py.${MODEL_NICKNAME}
FIXUP=`echo ${SCRATCH_ID} | awk '{p=$0; gsub("[.]","_",p); print p;}'`
PARAMS_MODULE=params/ginDQNParameters_${MODEL_NICKNAME}_${FIXUP}
PARAMS_TARGET=${LOCAL_REPO}/${PARAMS_MODULE}.py
if [[ -d ${RLGIN_BATCH_LOCAL_REPO} ]]
then
	cp ${PARAMS_LOC}/ginDQNParameters.py.${MODEL_NICKNAME} ${PARAMS_TARGET} 
else
	echo "#### ${CURRENT_SCRIPT_NAME} ${RLGIN_BATCH_LOCAL_REPO} not fouund, this could be a problem...."
fi
 
echo "#### ${CURRENT_SCRIPT_NAME} cleaning up fram any previous runs..."
[ -e ${WEIGHTSPATH}/weights.*.h5.post_training ] && rm ${WEIGHTSPATH}/weights.h5.post_training 
 
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

echo "#### ${CURRENT_SCRIPT_NAME} switching to execution directory ..."
cd ${RUN_DIR}
pwd
ls -latr
ls -latr params

echo "#### ${CURRENT_SCRIPT_NAME} launching scratchGin process..."
python learningGin.py  \
	--name_scenario "${NAME_SCENARIO}" \
	--logfile "${LOGFILE}" \
	--params_module ${PARAMS_MODULE} 
echo "#### ${CURRENT_SCRIPT_NAME} scratchGin process completed"
 
echo "#### ${CURRENT_SCRIPT_NAME} capturing weights to ${WEIGHTS_OUTPUT_FILE} ..."
[ -e weights/weights.*.h5.post_training ] && cp weights/weights.*.h5.post_training "${WEIGHTS_OUTPUT_FILE}" 
 
cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}

TIMESTAMP=`date -u +%Y-%m-%d_%H%M%S` 

echo "#############  ${CURRENT_SCRIPT_NAME} complete at ${TIMESTAMP} ##############"




