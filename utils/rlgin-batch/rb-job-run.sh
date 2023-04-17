#!/bin/bash
set -x

## figure out our job parameters
source ./rb-fetch-job-params.sh
SERIES_NICKNAME="${1:-${RLGIN_BATCH_JP_SERIES_NICKNAME}}"
PARAMS_SPEC="${2:-${RLGIN_BATCH_JP_PARAMS_SPEC}}"
TRAIN_OR_SCRATCH="${3:-${RLGIN_BATCH_JP_SERIES_NICKNAME}}"
SCRATCH_DRIVER_ID=${4:-${RLGIN_BATCH_JP_SCRATCH_DRIVER_ID}}

## report our job parameters
set | egrep "JOB|BATCH_JP|BATCH_TASK_INDEX"
echo "BATCH_TASK_INDEX=${BATCH_TASK_INDEX}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo PARAMS_SPEC="${PARAMS_SPEC}"
echo TRAIN_OR_SCRATCH="${TRAIN_OR_SCRATCH}"
echo SCRATCH_DRIVER_ID="${SCRATCH_DRIVER_ID}"

# make sure this machine is initialized for the work
./rb-bootstrap_series.sh

# get into the cockpit
TARGET_DIRECTORY=${RLGIN_BATCH_SERIES_BASE}/${SERIES_NICKNAME}${SCRATCH_DRIVER_ID}
echo TARGET_DIRECTORY=${TARGET_DIRECTORY}
cd ${TARGET_DIRECTORY}
echo "current directory=`pwd`"

# launch
echo launching scratchDriver.sh...
echo "nohup ./scratchDriver.sh ${SCRATCH_DRIVER_ID} 2>&1 > scratchDriver.sh.out &"
nohup ./scratchDriver.sh ${SCRATCH_DRIVER_ID} 2>&1 > scratchDriver.sh.out &

# wait for the dust to clear
sleep 3

# confirm launch 
ps -ef | grep "river.sh ${SCRATCH_DRIVER_ID}" 




