#!/bin/bash

TARGET_SPEC=${@:$#} # last parameter
SOURCE_SPEC=${*%${!#}} # all parameters except the last

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"

if [[ "${SOURCE_SPEC}" == *@* ]]
then
	HOST=`echo ${SOURCE_SPEC} | cut -f2 -d'@' | cut -f1 -d':'`
else
	HOST=`echo ${TARGET_SPEC} | cut -f2 -d'@' | cut -f1 -d':'`
fi

zone=""
if [[ XX${HOST}XX == "XXXX" ]]
then
	echo no remote host
else
	echo remote host is: ${HOST}
	zp=`${CURRENT_SCRIPT_SOURCE_DIR}/host2zone.sh ${HOST}`
	zone=`echo $zp | cut -f1 "-d "`
	project=`echo $zp | cut -f2 "-d "`
fi 

echo gcloud compute scp --project=${project} --zone=${zone} ${SOURCE_SPEC} "${TARGET_SPEC}"gcloud compute scp --project=rlgin-342502 --zone=${zone} ${SOURCE_SPEC} "${TARGET_SPEC}"
gcloud compute scp --project=${project} --zone=${zone} ${SOURCE_SPEC} "${TARGET_SPEC}"
