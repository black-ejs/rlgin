#!/bin/bash
#set -x

TRAIN_OR_SCRATCH="${1}"
if [[ "X""${TRAIN_OR_SCRATCH}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER "TRAIN" OR "SCRATCH" NOT FOUND
    echo "EXITING WITH CODE 33"
    echo "*****************************"
    exit 33
fi
if [[ "${TRAIN_OR_SCRATCH}" == *TRAIN* || "${TRAIN_OR_SCRATCH}" == *SCRATCH* ]]
then
    echo BOOTSTRAPPING FOR "${TRAIN_OR_SCRATCH}"
else
    echo "*********** ERROR ***********"
    echo FIRST PARAMETER MUST BE "TRAIN" OR "SCRATCH" 
    echo "EXITING WITH CODE 11"
    echo "*****************************"
    exit 11
fi

REMOTE_HOST="${2}"
SERIES_NICKNAME="${3}"
PARAMS_SPEC="${4}"
if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    WEIGHTS_SPEC="${5}"
fi
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
if [[ "X""${PARAMS_SPEC}""X" == "XX" ]]
then
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER PARAMS_SPEC NOT FOUND
    echo "EXITING WITH CODE 66"
    echo "*****************************"
    exit 66
fi
if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    if [[ "X""${WEIGHTS_SPEC}""X" == "XX" ]]
    then
        echo "*********** ERROR ***********"
        echo REQUIRED PARAMETER WEIGHTS_SPEC NOT FOUND
        echo "EXITING WITH CODE 55"
        echo "*****************************"
        exit 55
    fi
fi

echo REMOTE_HOST="${REMOTE_HOST}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo PARAMS_SPEC="${PARAMS_SPEC}"
if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    echo WEIGHTS_SPEC="${WEIGHTS_SPEC}"
fi

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

echo "  ********* ${CURRENT_SCRIPT_NAME}: obtaining PARAMS for ${SERIES_NICKNAME} ***********"
PARAMS_FILE="`basename ${PARAMS_SPEC}`"
LOCAL_PARAMS_FILE=/tmp/${PARAMS_FILE}
~/gscp.sh "${PARAMS_SPEC}" "${LOCAL_PARAMS_FILE}"
if [[ -e ${LOCAL_PARAMS_FILE} ]]
then
    echo "      ****** PARAMS copied to ${LOCAL_PARAMS_FILE} *******"
else
    echo "*********** ERROR ***********"
    echo UNABLE TO SCP PARAMS FROM ${PARAMS_SPEC} TO ${LOCAL_PARAMS_FILE}
    echo "EXITING WITH CODE 99"
    echo "*****************************"
    exit 99
fi

if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    echo "  ********* ${CURRENT_SCRIPT_NAME}: obtaining weights for ${SERIES_NICKNAME} ***********"
    WEIGHTS_FILE="`basename ${WEIGHTS_SPEC}`"
    LOCAL_WEIGHTS_FILE=/tmp/${WEIGHTS_FILE}

    ~/gscp.sh "${WEIGHTS_SPEC}" "${LOCAL_WEIGHTS_FILE}"
    if [[ -e ${LOCAL_WEIGHTS_FILE} ]]
    then
        echo "      ****** weights copied to ${LOCAL_WEIGHTS_FILE} *******"
    else
        echo "*********** ERROR ***********"
        echo UNABLE TO SCP WEIGHTS FROM ${WEIGHTS_SPEC} TO ${LOCAL_WEIGHTS_FILE}
        echo "EXITING WITH CODE 77"
        echo "*****************************"
        exit 77
    fi
fi

echo "  ********* ${CURRENT_SCRIPT_NAME}: contacting host and getting code ***********"
~/gssh.sh "${REMOTE_HOST}" < "${CURRENT_SCRIPT_SOURCE_DIR}"/bootstrap_vm.sh 2>/dev/null | awk '{if (p==1) {print $0;}}/permitted by/{p=1;}'

echo "  ********* ${CURRENT_SCRIPT_NAME}: bootstrapping series location for series ${SERIES_NCKNAME} ***********"
LOC_OUT=/tmp/"${CURRENT_SCRIPT_NAME}".LOC_OUT
~/gcmd.sh  "~/dev/rlgin/utils/series/bootstrap_series.sh ${SERIES_NICKNAME} ${TRAIN_OR_SCRATCH}" "${REMOTE_HOST}" > "${LOC_OUT}"
cat "${LOC_OUT}"
if [[ `grep "[*] ERROR [*]" "${LOC_OUT}"` == *" ERROR "* ]]
then
    exit 44
fi

echo "  ********* ${CURRENT_SCRIPT_NAME}: copying parameters for ${SERIES_NICKNAME} ***********"
~/gscp.sh "${LOCAL_PARAMS_FILE}" "${REMOTE_ID}"@"${REMOTE_HOST}":"${TARGET_PATH}"/ginDQNParameters.py."${SERIES_NICKNAME}"

if [[ "${TRAIN_OR_SCRATCH}" == "TRAIN" ]]
then
    echo "  ********* ${CURRENT_SCRIPT_NAME}: copying weights for ${SERIES_NICKNAME} ***********"
    ~/gscp.sh "${LOCAL_WEIGHTS_FILE}" "${REMOTE_ID}"@"${REMOTE_HOST}":"${TARGET_PATH}"/rlgin/weights/${WEIGHTS_FILE}
    ~/gcmd.sh "cp ${TARGET_PATH}/rlgin/weights/${WEIGHTS_FILE} ${TARGET_PATH}/rlgin/weights/weights.h5.0" "${REMOTE_HOST}"
fi

echo "  ********* ${CURRENT_SCRIPT_NAME}: finished for ${SERIES_NICKNAME} ***********"
~/gcmd.sh "ls -l ${TARGET_PATH}" "${REMOTE_HOST}"




