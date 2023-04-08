#!/bin/bash
CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"

DRIVER_START="${1:-1}"
DRIVER_END="${2:-10}"

for ii in `seq -s' ' ${DRIVER_START} ${DRIVER_END}`
do
	echo INVOKING ./trainGin.sh $ii in directory `pwd`
	./trainGin.sh > trainGin.sh.out$ii
done

