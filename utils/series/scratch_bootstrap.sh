#!/bin/bash
#set -x

REMOTE_HOST="${1}"
SERIES_NICKNAME="${2}"
REMOTE_ID="edward_schwarz"
TRAINING_GROUND="~/dev/projects/training_ground"
TARGET_PATH=${TRAINING_GROUND}/${SERIES_NICKNAME}

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

echo "*********** ${CURRENT_SCRIPT_NAME}: execution at `date` ***********"

if [[ "X""${REMOTE_HOST}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER REMOTE_HOST NOT FOUND
    echo "EXITING WITH CODE 33"
    echo "*****************************"
    exit 33
fi
if [[ "X""${SERIES_NICKNAME}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER SERIES_NICKNAME NOT FOUND
    echo "EXITING WITH CODE 22"
    echo "*****************************"
    exit 22
fi

echo REMOTE_HOST="${REMOTE_HOST}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"

echo "  ********* ${CURRENT_SCRIPT_NAME}: vaidating remote host ${REMOTE_HOST} ***********"
remote_home=`~/gcmd.sh "pwd" "${REMOTE_HOST}"`
if [[ X"${remote_home}"X == "XX" ]]
then
	msg="ERROR LOGGING INTO REMOTE HOST ${REMOTE_HOST}"
elif [[ "${remote_home}" == *${REMOTE_ID}* ]] 
then
	msg="ok"
else
	msg="UNEXPECTED RESPONSE ${remote_home} FROM ${REMOTE_HOST}"
fi
if [[ "${msg}" != "ok" ]]
then
    echo "*********** ERROR ***********"
    echo ${msg}
    echo "EXITING WITH CODE 88"
    echo "*****************************"
    exit 88
fi

echo "  ********* ${CURRENT_SCRIPT_NAME}: contacting host and getting code ***********"
~/gssh.sh "${REMOTE_HOST}" < "${CURRENT_SCRIPT_SOURCE_DIR}"/bootstrap_vm.sh 2>/dev/null | awk '{if (p==1) {print $0;}}/permitted by/{p=1;}'

echo "  ********* ${CURRENT_SCRIPT_NAME}: bootstrapping series location for series ${SERIES_NCKNAME} ***********"
~/gcmd.sh  "~/dev/rlgin/utils/series/bootstrap_series.sh ${SERIES_NICKNAME} SCRATCH" "${REMOTE_HOST}"

echo "  ********* ${CURRENT_SCRIPT_NAME}: finished for ${SERIES_NICKNAME} ***********"
~/gcmd.sh "ls -l ${TARGET_PATH}" "${REMOTE_HOST}"




