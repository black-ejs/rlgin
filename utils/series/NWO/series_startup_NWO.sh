#!/bin/bash
#set -x

source ./vars_NWO.sh

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

echo "*********** ${CURRENT_SCRIPT_NAME}: execution at `date` ***********"
echo REMOTE_HOSTS="${REMOTE_HOSTS}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo SERIES_INDEXES="${SERIES_INDEXES}"

echo "     ****** ${CURRENT_SCRIPT_NAME}: fetching targets ******"
DIRS=""
ALLDIRS=""
for REMOTE_HOST in ${REMOTE_HOSTS}
do
	DIRS=`~/gcmd.sh "find ~/dev/projects/training_ground -name \"${SERIES_NICKNAME}*\" -type d " "${REMOTE_HOST}"`
	for DIR in ${DIRS}
	do
		ALLDIRS="${ALLDIRS} ${DIR}@${REMOTE_HOST}"
	done
done
# echo ALLDIRS=${ALLDIRS}

for TARGET in ${ALLDIRS}
do
	echo "     ****** ${CURRENT_SCRIPT_NAME}: starting up ${TARGET} ******"
	RTARGETDIR=`echo "${TARGET}" | cut -d@ -f1`
        RHOST=`echo "${TARGET}" | cut -d@ -f2`
	DRIVER_INDEX=`echo ${RTARGETDIR} | awk '{print substr($0,length($0),1)}'`
	ARG1=" cd ${RTARGETDIR}; echo launching; nohup ./scratchDriver.sh ${DRIVER_INDEX} > ./scratchDriver.sh.out &  echo launched ; sleep 3; echo exiting"

	~/gcmd2.sh "${ARG1}" "${RHOST}"	
done


	

