#!/bin/bash
#set -x
echo "*** start ***************"

driver_id=${1:-0} 

for hh in {1..10}
do 
	echo launching scratchGin.sh ${driver_id}.${hh} at `date`
	./scratchGin.sh ${driver_id}.${hh} > scratchGin.out.${driver_id}.${hh}
	echo scratchGin.sh ${driver_id}.${hh} completed at `date`
done

echo "*** done ***************"

