#!/bin/bash
#set -x
echo "*** start ***************"

driver_id=${1:-0} 
DRIVER_START=${2:-1}
DRIVER_END=${3:-10}

for hh in `seq -s' ' ${DRIVER_START} ${DRIVER_END}`
do 
	echo launching scratchGin.sh ${driver_id}.${hh} at `date`
	./scratchGin.sh ${driver_id}.${hh} > scratchGin.out.${driver_id}.${hh}
	echo scratchGin.sh ${driver_id}.${hh} completed at `date`
done

echo "*** done ***************"

