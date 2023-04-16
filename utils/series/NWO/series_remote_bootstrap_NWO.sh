#!/bin/bash
#set -x

source ./vars_NWO.sh

#    CHOOSE setup for remote params 
#REMOTE_ID=edward_schwarz
#PARAMS_SOURCE_MODEL_NICKNAME=HOT.3.5
#PARAMS_SOURCE_VM=r-learn-b-cent1a-vm-1
#PARAMS_FILE=ginDQNParameters.py."${PARAMS_SOURCE_MODEL_NICKNAME}"
#PARAMS_TARGET_PATH="~/dev/projects/training_ground/${PARAMS_SOURCE_MODEL_NICKNAME}"
#PARAMS_RP="${REMOTE_ID}"@"${PARAMS_SOURCE_VM}"
#SERIES_PARAMS_SPEC=${PARAMS_RP}:"${PARAMS_TARGET_PATH}"/"${PARAMS_FILE}"
# OR CHOOSE setup for local params 
SERIES_PARAMS_SPEC=`pwd`/ginDQNParameters.py."${SERIES_NICKNAME}".scratch

# ################################################################
# ################################################################
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`
REMOTE_REPO_URL=https://github.com/black-ejs/rlgin
BOOTSTRAP_LOG=./${CURRENT_SCRIPT_NAME}.bootstrap.log

echo "*********** ${CURRENT_SCRIPT_NAME}: execution at `date` ***********"
echo REMOTE_HOSTS="${REMOTE_HOSTS}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo SERIES_INDEXES="${SERIES_INDEXES}"
echo SERIES_PARAMS_SPEC="${SERIES_PARAMS_SPEC}"

echo "     ****** ${CURRENT_SCRIPT_NAME}: getting scripts ******"
rm -rf ./rlgin
git clone "${REMOTE_REPO_URL}"
SERIES_SCRIPTS_SOURCE_DIR=rlgin/utils/series

echo "     ****** ${CURRENT_SCRIPT_NAME}: getting bootstrapping ${SERIES_NICKNAME} @ ${REMOTE_HOSTS} ******"
echo ${SERIES_SCRIPTS_SOURCE_DIR}/series_remote_bootstrap.sh "${REMOTE_HOSTS}"  "${SERIES_NICKNAME}"  "${SERIES_INDEXES}" "${SERIES_PARAMS_SPEC}"
${SERIES_SCRIPTS_SOURCE_DIR}/series_remote_bootstrap.sh "${REMOTE_HOSTS}"  "${SERIES_NICKNAME}" "${SERIES_INDEXES}" "${SERIES_PARAMS_SPEC}" | tee "${BOOTSTRAP_LOG}"


echo "     ****** ${CURRENT_SCRIPT_NAME}: cleaning up ******"
rm -rf rlgin
