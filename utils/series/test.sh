#!/bin/bash
#set -x

REMOTE_HOST=r-learn-c-east1b-vm-1
SERIES_NICKNAME=bHot4

WEIGHTS_SOURCE_VM=r-learn-b-cent1a-vm-1
WEIGHTS_SOURCE_MODEL_NICKNAME=HOT.3.5
WEIGHTS_FILE=scratchGin_HandOut.3.5.2023-03-22_055755.h5

PARAMS_SOURCE_VM=${WEIGHTS_SOURCE_VM}
PARAMS_SOURCE_MODEL_NICKNAME=${WEIGHTS_SOURCE_MODEL_NICKNAME}

# ####################################################
# ####################################################
# ####################################################
REMOTE_ID=edward_schwarz
WEIGHTS_TARGET_PATH="~/dev/projects/training_ground/${WEIGHTS_SOURCE_MODEL_NICKNAME}"
WEIGHTS_RP="${REMOTE_ID}"@"${WEIGHTS_SOURCE_VM}"
WEIGHTS_SPEC=${WEIGHTS_RP}:"${WEIGHTS_TARGET_PATH}"/rlgin/weights/"${WEIGHTS_FILE}"

PARAMS_FILE=ginDQNParameters.py."${PARAMS_SOURCE_MODEL_NICKNAME}"
PARAMS_TARGET_PATH="~/dev/projects/training_ground/${PARAMS_SOURCE_MODEL_NICKNAME}"
PARAMS_RP="${REMOTE_ID}"@"${PARAMS_SOURCE_VM}"
PARAMS_SPEC=${PARAMS_RP}:"${PARAMS_TARGET_PATH}"/"${PARAMS_FILE}"

#BSCRIPT=./scratch_bootstrap.sh
BSCRIPT=./train_bootstrap.sh

##################################

${BSCRIPT} "${REMOTE_HOST}" \
	"${SERIES_NICKNAME}" \
	"${PARAMS_SPEC}" \
	"${WEIGHTS_SPEC}"



