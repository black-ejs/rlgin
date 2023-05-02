#!/bin/bash
#set -x

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

## figure out our job parameters
echo "########## ${CURRENT_SCRIPT_NAME}: fetching Job parameters"
source ./rb-fetch-job-params.sh
SERIES_NICKNAME="${1:-${RLGIN_BATCH_JP_SERIES_NICKNAME}}"
PARAMS_SPEC="${2:-${RLGIN_BATCH_JP_PARAMS_SPEC}}"
TRAIN_OR_SCRATCH="${3:-${RLGIN_BATCH_JP_TRAIN_OR_SCRATCH}}"
SCRATCH_DRIVER_ID=${4:-${RLGIN_BATCH_JP_SCRATCH_DRIVER_ID}}
WEIGHTS_SPEC=${5:-${RLGIN_BATCH_JP_WEIGHTS_SPEC}}
TRAIN_GENERATIONS=${6:-${RLGIN_BATCH_JP_TRAIN_GENERATIONS}}
SCRATCH_DRIVER_START=${7:-${RLGIN_BATCH_JP_SCRATCH_DRIVER_START}}
SCRATCH_DRIVER_END=${8:-${RLGIN_BATCH_JP_SCRATCH_DRIVER_END}}

## report our job parameters
echo "########## ${CURRENT_SCRIPT_NAME}: parameter review"
set | egrep "JOB|RLGIN_JP|TASK"
echo BATCH_TASK_INDEX="${BATCH_TASK_INDEX}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo PARAMS_SPEC="${PARAMS_SPEC}"
echo TRAIN_OR_SCRATCH="${TRAIN_OR_SCRATCH}"
echo SCRATCH_DRIVER_ID="${SCRATCH_DRIVER_ID}"
echo WEIGHTS_SPEC="${WEIGHTS_SPEC}"
echo TRAIN_GENERATIONS="${TRAIN_GENERATIONS}"
echo SCRATCH_DRIVER_START="${SCRATCH_DRIVER_START}"
echo SCRATCH_DRIVER_END="${SCRATCH_DRIVER_END}"

# make sure this machine is initialized for the work
if [[ -d ${RLGIN_BATCH_LOCAL_REPO} ]]
then
    echo "########## ${CURRENT_SCRIPT_NAME}: local code repo found"
else
    echo "########## ${CURRENT_SCRIPT_NAME}: establishing local code repo at ${RLGIN_BATCH_LOCAL_REPO}"
    git clone -q ${RLGIN_BATCH_REPO_URL} ${RLGIN_BATCH_LOCAL_REPO}
fi
echo "########## ${CURRENT_SCRIPT_NAME}: validating local code repo"
if [[ "`ls -la ${RLGIN_BATCH_LOCAL_REPO}`" == *.git* ]]
then
    echo "########## ${CURRENT_SCRIPT_NAME}: local code repo OK"
else
    echo "########## ${CURRENT_SCRIPT_NAME}: local code repo NOT OK"
    echo "########## ${CURRENT_SCRIPT_NAME}: local code repo contents"
    ls -latr ${RLGIN_BATCH_LOCAL_REPO}
fi

echo "########## ${CURRENT_SCRIPT_NAME}: bootrapping for series ${SERIES_NICKNAME}" 
./rb-bootstrap_series.sh

# get into the cockpit
echo "########## ${CURRENT_SCRIPT_NAME}: preflight check ${SERIES_NICKNAME}"
TARGET_DIRECTORY=${RLGIN_BATCH_SERIES_BASE}/${SERIES_NICKNAME}${SCRATCH_DRIVER_ID}
echo TARGET_DIRECTORY=${TARGET_DIRECTORY}
cd ${TARGET_DIRECTORY}
echo "current directory=`pwd`"
echo "contents of ${TARGET_DIRECTORY}:"
ls -latr 

# launch
if [[ ${TRAIN_OR_SCRATCH} == "SCRATCH" ]]
then
    echo "########## ${CURRENT_SCRIPT_NAME}: launching scratchDriver.sh"
    echo "nohup ./scratchDriver.sh ${SCRATCH_DRIVER_ID} 2>&1 > scratchDriver.sh.out &"
    nohup ./scratchDriver.sh ${SCRATCH_DRIVER_ID} ${SCRATCH_DRIVER_START} ${SCRATCH_DRIVER_END} 2>&1 > scratchDriver.sh.out.${BATCH_TASK_INDEX} &
elif [[ ${TRAIN_OR_SCRATCH} == "TRAIN" ]]
then
    echo "########## ${CURRENT_SCRIPT_NAME}: launching trainDriver.sh"
    echo "nohup ./trainDriver.sh 1 ${TRAIN_GENERATIONS} 2>&1 > trainDriver.sh.out &"
    nohup ./trainDriver.sh 1 ${TRAIN_GENERATIONS} 2>&1 > trainDriver.sh.out &
else
    echo "########## ${CURRENT_SCRIPT_NAME}: ERROR - TRAIN_OR_SCRATCH=\"${TRAIN_OR_SCRATCH}\", no driver launched"
    echo "########## ${CURRENT_SCRIPT_NAME}: task will clean up and exit"
fi


# wait for the dust to clear
SECS_TO_WAIT=3
echo "########## ${CURRENT_SCRIPT_NAME}: waiting ${SECS_TO_WAIT} for the dust to clear"
sleep ${SECS_TO_WAIT}

# confirm launch 
echo "########## ${CURRENT_SCRIPT_NAME}: confirming launch"
ps -ef | grep "river.sh [0-9]" 



