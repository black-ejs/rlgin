#!/bin/bash
#set -x  
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"

driver_id=${1:-0} 
DRIVER_START=${2:-1}
DRIVER_END=${3:-10}
CONTROL_DIR=${4:-$PWD}

echo "*** ${CURRENT_SCRIPT_NAME} start ***"
for hh in `seq -s' ' ${DRIVER_START} ${DRIVER_END}`
do 
	echo launching scratchGin.sh ${driver_id}.${hh} at `date` - CONTROL_DIR=${CONTROL_DIR}
	./scratchGin.sh ${driver_id}.${hh} ${CONTROL_DIR} > scratchGin.out.${driver_id}.${hh}
	echo scratchGin.sh ${driver_id}.${hh} completed at `date`
done
echo "*** ${CURRENT_SCRIPT_NAME} start ***"

