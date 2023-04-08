#!/bin/bash
set -x

REMOTE_HOST=r-learn-c-east1b-vm-1
SERIES_NICKNAME=10

WEIGHTS_SOURCE_VM=r-learn-b-cent1a-vm-1
WEIGHTS_SOURCE_MODEL_NICKNAME=HOT.3.5
WEIGHTS_FILE=scratchGin_HandOut.3.5.2023-03-22_055755.h5

PARAMS_SOURCE_VM=${WEIGHTS_SOURCE_VM}
PARAMS_SOURCE_MODEL_NICKNAME=${WEIGHTS_SOURCE_MODEL_NICKNAME}

##################################

./remote_bootstrap.sh "${REMOTE_HOST}" \
	"${SERIES_NICKNAME}" \
	"edward_schwarz@${WEIGHTS_SOURCE_VM}:~/dev/projects/training_ground/${WEIGHTS_SOURCE_MODEL_NICKNAME}/rlgin/weights/${WEIGHTS_FILE}" \
	"edward_schwarz@${PARAMS_SOURCE_VM}:~/dev/projects/training_ground/${PARAMS_SOURCE_MODEL_NICKNAME}/ginDQNParameters.py.${PARAMS_SOURCE_MODEL_NICKNAME}"



