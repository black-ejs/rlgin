#!/bin/bash
set -x

SERIES_NICKNAME="${1}"

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`
REMOTE_REPO_URL="https://github.com/black-ejs/rlgin"

if [[ "X""${SERIES_NICKNAME}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER SERIES NICKNAME NOT FOUND
    echo "EXITING WITH CODE 22"
    echo "*****************************"
    exit 22
fi

TRAINING_GROUND=~/dev/projects/training_ground
TARGET_PATH="${TRAINING_GROUND}"/"${SERIES_NICKNAME}"
if [[ -e "${TARGET_PATH}" ]]
then
    echo "*********** ERROR ***********"
    echo TARGET PATH ${TARGET_PATH} ALREADY EXISTS:
    ls -l ~/dev/projects/training_ground/${SERIES_NICKNAME}
    echo "EXITING WITH CODE 44"
    echo "*****************************"
    exit 44
fi

echo "**** CREATING TARGET DIRECTORY ${TARGET_PATH}"
mkdir -p "${TARGET_PATH}"
cd "${TARGET_PATH}"

echo "**** OBTAINING rlgin EXECUTION CODE"
git clone "${REMOTE_REPO_URL}"

echo "**** CREATING LOGS DIRECTORY"
mkdir rlgin/logs

echo "**** CREATING WEIGHTS DIRECTORY"
mkdir rlgin/weights

echo "**** COPYING PARAMETER TEMPLATE"
cp rlgin/ginDQNParameters.py ginDQNParameters.py.${SERIES_NICKNAME}

echo "**** COPYING TRAINING SCRIPTS"
cp rlgin/utils/trainGin/trainGin.sh .
chmod a+x ./trainGin.sh
cp rlgin/utils/trainGin/trainDriver.sh .
chmod a+x ./trainDriver.sh

echo "**** returning to original path: ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}"
cd ${CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR}

