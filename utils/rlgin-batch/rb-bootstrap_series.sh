#!/bin/bash
set -x

export SERIES_NICKNAME="${1:-${RLGIN_BATCH_JP_SERIES_NICKNAME}}"
export PARAMS_SPEC="${2:-${RLGIN_BATCH_JP_PARAMS_SPEC}}"
export TRAIN_OR_SCRATCH="${3:-${RLGIN_BATCH_JP_TRAIN_OR_SCRATCH}}"
export SCRATCH_DRIVER_ID="${4:-${RLGIN_BATCH_JP_SCRATCH_DRIVER_ID}}"
export WEIGHTS_SPEC="${5:-${RLGIN_BATCH_JP_WEIGHTS_SPEC}}"
export TRAIN_GENERATIONS="${6:-${RLGIN_BATCH_JP_TRAIN_GENERATIONS}}"

echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo PARAMS_SPEC="${PARAMS_SPEC}"
echo TRAIN_OR_SCRATCH="${TRAIN_OR_SCRATCH}"
echo SCRATCH_DRIVER_ID="${SCRATCH_DRIVER_ID}"
echo WEIGHTS_SPEC="${WEIGHTS_SPEC}"
echo TRAIN_GENERATIONS="${TRAIN_GENERATIONS}"

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`
UPDATING="FALSE"

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

TARGET_PATH="${TRAINING_GROUND}"/"${SERIES_NICKNAME}${SCRATCH_DRIVER_ID}"
if [[ -e "${TARGET_PATH}" ]]
then
    echo "*********** WARNING ***********"
    echo TARGET PATH ${TARGET_PATH} ALREADY EXISTS:
    ls -l ${TARGET_PATH}
    echo "WILL UPDATE CODE ELEMENTS"
    echo "*****************************"
    UPDATING="TRUE"
fi
echo "UPDATING=${UPDATING}"

PARAMS_FILE="${RLGIN_BATCH_PARAMS}/${RLGIN_BATCH_JOB_PARAMS_PATH}/${PARAMS_SPEC}"
if [ ! -e ${PARAMS_FILE} ]
then
    echo "*********** ERROR ***********"
    echo INPUT PARAMS FILE ${PARAMS_FILE} NOT FOUND
    echo "EXITING WITH CODE 23"
    echo "*****************************"
    exit 23
fi

if [[ ${UPDATING} == "FALSE" ]]
then
    echo "**** CREATING TARGET DIRECTORY ${TARGET_PATH}"
    mkdir -p "${TARGET_PATH}"
    cd "${TARGET_PATH}"
    
    echo "**** CREATING LOGS DIRECTORY"
    mkdir -p ${LOG_LOC}

    echo "**** CREATING WEIGHTS DIRECTORY"
    mkdir -p ${WEIGHTS_LOC}
fi

echo "**** copying in git repo "
repoback=`pwd`
TMPREPO=${RLGIN_BATCH_TMPDIR}/rb-repo.zip
rm -rf ${TMPREPO}
cd ${RLGIN_BATCH_LOCAL_REPO}
git archive --format zip HEAD >  ${TMPREPO}
cd "${repoback}"
mkdir -p ${LOCAL_REPO}
cd ${LOCAL_REPO}
unzip ${TMPREPO}
cd "${TARGET_PATH}"

echo "**** COPYING PARAMETER TEMPLATE"
TARGET_PARAMETERS_FILENAME=ginDQNParameters.py.${SERIES_NICKNAME}${SCRATCH_DRIVER_ID}
cp ${LOCAL_REPO}/ginDQNParameters.py ${TARGET_PARAMETERS_FILENAME}

echo "**** COPYING TRAINING SCRIPTS"
cp ${SCRIPTS_LOC}/trainGin/trainGin.sh .
chmod a+x ./trainGin.sh
cp ${SCRIPTS_LOC}/trainGin/trainDriver.sh .
chmod a+x ./trainDriver.sh

echo "**** COPYING SCRATCH SCRIPTS"
cp ${SCRIPTS_LOC}/scratch/scratchGin.sh .
chmod a+x ./scratchGin.sh
cp ${SCRIPTS_LOC}/scratch/scratchDriver.sh .
chmod a+x ./scratchDriver.sh
cp ${SCRIPTS_LOC}/scratch/testWeights.sh .
chmod a+x ./testWeights.sh

echo "  ********* ${CURRENT_SCRIPT_NAME}: obtaining PARAMS for ${SERIES_NICKNAME} ***********"
cp ${PARAMS_FILE} ${TARGET_PARAMETERS_FILENAME}

if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    WEIGHTS_SPEC_FILENAME=`basename ${WEIGHTS_SPEC}`
    TARGET_WEIGHTS_PATH=${WEIGHTS_LOC}/${WEIGHTS_SPEC_FILENAME}
    WEIGHTS_FILE="${RLGIN_BATCH_PARAMS}/${RLGIN_BATCH_JOB_PARAMS_PATH}/${WEIGHTS_SPEC}"
    echo "  ********* ${CURRENT_SCRIPT_NAME}: obtaining WEIGHTS from ${WEIGHTS_SPEC} ***********"
    cp ${WEIGHTS_FILE} ${TARGET_WEIGHTS_PATH}
    cp ${WEIGHTS_FILE} ${WEIGHTS_LOC}/weights.h5.0
fi

echo "**** returning to original path: ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}"
cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}

