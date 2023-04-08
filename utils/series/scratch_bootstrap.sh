#!/bin/bash
#set -x


CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

echo "*********** ${CURRENT_SCRIPT_NAME}: execution at `date` ***********"
"${CURRENT_SCRIPT_SOURCE_DIR}"/remote_bootstrap.sh SCRATCH $*


