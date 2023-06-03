#!/bin/bash
#set -x
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"


DRIVER_START="${1:-1}"
DRIVER_END="${2:-10}"
CONTROL_DIR=${3:-$PWD}
JOB_ID=${4:-J$$}

echo "*** ${CURRENT_SCRIPT_NAME} start ***"
for ii in `seq -s' ' ${DRIVER_START} ${DRIVER_END}`
do
	echo launching trainGin.sh at `date` - CONTROL_DIR=${CONTROL_DIR}
	./trainGin.sh ${CONTROL_DIR} 2>&1 > ${CONTROL_DIR/}/trainGin.sh.out$ii.${JOB_ID}
	echo trainGin.sh completed at `date`
done
echo "*** ${CURRENT_SCRIPT_NAME} start ***"

