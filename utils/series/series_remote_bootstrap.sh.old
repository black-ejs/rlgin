#!/bin/bash
#set -x

REMOTE_HOSTS=${1}
SERIES_NICKNAME=${2}
SERIES_INDEXES=${3}
SERIES_PARAMS_SPEC=${4}

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"
CURRENT_SCRIPT_ORIGINAL_EXECUTION_DIR=`pwd`

missing=""
if [[ X"${REMOTE_HOSTS}"X == "XX" ]]
then
	missing="REMOTE_HOSTS"
elif [[ X"${SERIES_NICKNAME}"X == "XX" ]]
then
	missing="SERIES_NICKNAME"
elif [[ X"${SERIES_PARAMS_SPEC}"X == "XX" ]]
then
	missing="SERIES_INDEXES"
elif [[ X"${SERIES_PARAMS_SPEC}"X == "XX" ]]
then
	missing="SERIES_INDEXES"
fi	

if [[ X"${missing}"X == "XX" ]]
then
	echo "    #### params ok"
else
    echo "*********** ERROR ***********"
    echo REQUIRED PARAMETER "${missing}" NOT FOUND
    echo "EXITING WITH CODE 9"
    echo "*****************************"
    exit 9
fi

echo "*********** ${CURRENT_SCRIPT_NAME}: execution at `date` ***********"
echo REMOTE_HOSTS="${REMOTE_HOSTS}"
echo SERIES_NICKNAME="${SERIES_NICKNAME}"
echo SERIES_INDEXES="${SERIES_INDEXES}"
echo SERIES_PARAMS_SPEC="${SERIES_PARAMS_SPEC}"

for REMOTE_HOST in ${REMOTE_HOSTS}
do
	echo "    ******* ${CURRENT_SCRIPT_NAME}: vaidating remote host ${REMOTE_HOST} ***********"
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
done

echo "    ****** mapping remote hosts *****"
REMOTE_HOST_COUNT=`echo ${REMOTE_HOSTS} | wc -w`
RHSEQ=`seq -s' ' 1 ${REMOTE_HOST_COUNT}`
for ii in ${RHSEQ}
do
	RH=`echo ${REMOTE_HOSTS} | cut -f${ii} -d' '`
	export RH${ii}=${RH}
	echo `set | grep RH${ii} | grep -v "_[=]"`
done

for jj in ${SERIES_INDEXES}
do
   	echo "    ***********************************"
	echo "    ****** bootstrapping series ${SERIES_NICKNAME} index $jj *****"
	rh_index=`expr ${jj} % ${REMOTE_HOST_COUNT} + 1`
	RH=`set | grep RH${rh_index} | grep -v "_[=]" | awk '{split($0,aa,"="); print aa[2];}'`
	MY_SERIES_NICK="${SERIES_NICKNAME}${jj}"
	echo ${CURRENT_SCRIPT_SOURCE_DIR}/scratch_bootstrap.sh "${RH}" "${MY_SERIES_NICK}" "${SERIES_PARAMS_SPEC}"
	${CURRENT_SCRIPT_SOURCE_DIR}/scratch_bootstrap.sh "${RH}" "${MY_SERIES_NICK}" "${SERIES_PARAMS_SPEC}"
done


echo "    ****** ${CURRENT_SCRIPT_NAME}: execution completed at `date` for  ${SERIES_NICKNAME}  ***********"
for REMOTE_HOST in ${REMOTE_HOSTS}
do
	~/gcmd.sh "echo '~/dev/projects/training_ground:'@"${REMOTE_HOST}"; ls -l ~/dev/projects/training_ground/" "${REMOTE_HOST}" 
done
