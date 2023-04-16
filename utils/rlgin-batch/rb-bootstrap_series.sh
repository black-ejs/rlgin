#!/bin/bash
#set -x

export SERIES_NICKNAME="${1:-${RLGIN_BATCH_JP_SERIES_NICKNAME}}"
export PARAMS_SPEC="${2:-${RLGIN_BATCH_JP_PARAMS_SPEC}}"
export TRAIN_OR_SCRATCH="${3:-${RLGIN_BATCH_JP_TRAIN_OR_SCRATCH}}"

echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo PARAMS_SPEC="${PARAMS_SPEC}"
echo TRAIN_OR_SCRATCH="${TRAIN_OR_SCRATCH}"

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

REMOTE_REPO_URL=${RLGIN_BATCH_REPO_URL}
TRAINING_GROUND=${RLGIN_BATCH_SERIES_BASE}
EXECUTION_DIR=rlgin
LOCAL_REPO=${EXECUTION_DIR}
LOG_LOC=${EXECUTION_DIR}/logs 
WEIGHTS_LOC=${EXECUTION_DIR}/weights
SCRIPTS_LOC=${LOCAL_REPO}/utils

source ${CURRENT_SCRIPT_SOURCE_DIR}/rb-fetch-job-params.sh
echo $JOB_PARAMETERS

if [[ "X""${SERIES_NICKNAME}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER SERIES NICKNAME NOT FOUND
    echo "EXITING WITH CODE 22"
    echo "*****************************"
    exit 22
fi

TARGET_PATH="${TRAINING_GROUND}"/"${SERIES_NICKNAME}"
if [[ -e "${TARGET_PATH}" ]]
then
    echo "*********** WARNING ***********"
    echo TARGET PATH ${TARGET_PATH} ALREADY EXISTS:
    ls -l ${TARGET_PATH}
    echo "EXITING"
    echo "*****************************"
    exit 0
fi

PARAMS_FILE="${RLGIN_BATCH_PARAMS}/${PARAMS_SPEC}"
if [ ! -e ${LOCAL_PARAMS_FILE} ]
then
    echo "*********** ERROR ***********"
    echo INPUT PARAMS FILE ${PARAMS_FILE} NOT FOUND
    echo "EXITING WITH CODE 23"
    echo "*****************************"
    exit 23
fi

echo "**** CREATING TARGET DIRECTORY ${TARGET_PATH}"
mkdir -p "${TARGET_PATH}"
cd "${TARGET_PATH}"

echo "**** copying in git repo "
cp -r ${RLGIN_BATCH_LOCAL_REPO} ${LOCAL_REPO#}

echo "**** CREATING LOGS DIRECTORY"
mkdir -p ${LOG_LOC}

echo "**** CREATING WEIGHTS DIRECTORY"
mkdir -p ${WEIGHTS_LOC}

echo "**** COPYING PARAMETER TEMPLATE"
TARGET_PARAMETERS_FILENAME=ginDQNParameters.py.${SERIES_NICKNAME}
cp ${LOCAL_REPO}/ginDQNParameters.py ${TARGET_PARAMETERS_FILENAME}

if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
	echo "**** COPYING TRAINING SCRIPTS"
	cp ${SCRIPTS_LOC}/trainGin/trainGin.sh .
	chmod a+x ./trainGin.sh
	cp ${SCRIPTS_LOC}/trainGin/trainDriver.sh .
	chmod a+x ./trainDriver.sh
elif [[ "${TRAIN_OR_SCRATCH}" == "SCRATCH" ]]
then
	echo "**** COPYING SCRATCH SCRIPTS"
	cp ${SCRIPTS_LOC}/scratch/scratchGin.sh .
	chmod a+x ./scratchGin.sh
	cp ${SCRIPTS_LOC}/scratch/scratchDriver.sh .
	chmod a+x ./scratchDriver.sh
	cp ${SCRIPTS_LOC}/scratch/testWeights.sh .
	chmod a+x ./testWeights.sh
fi

echo "  ********* ${CURRENT_SCRIPT_NAME}: obtaining PARAMS for ${SERIES_NICKNAME} ***********"
cp ${PARAMS_FILE} ${TARGET_PARAMETERS_FILENAME}

echo "**** returning to original path: ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}"
cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}

