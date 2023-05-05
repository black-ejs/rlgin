#!/bin/bash
#set -x
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"


DRIVER_START="${1:-1}"
DRIVER_END="${2:-10}"
CONTROL_DIR=${3:-$PWD}

echo "*** ${CURRENT_SCRIPT_NAME} start ***"
for ii in `seq -s' ' ${DRIVER_START} ${DRIVER_END}`
do
	echo launching trainGin.sh at `date`
	./trainGin.sh ${CONTROL_DIR} > trainGin.sh.out$ii
	echo trainGin.sh completed at `date`
done
echo "*** ${CURRENT_SCRIPT_NAME} start ***"

