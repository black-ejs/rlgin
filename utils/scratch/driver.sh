#!/bin/bash
echo "*** start ***************"

driver_id=${1:-0} 

for hh in {1..10}
do 
#	echo $hh hh
	./scratchGin.sh ${driver_id}.${hh} > scratchGin.out.${driver_id}.${hh}
done

echo "*** done ***************"

