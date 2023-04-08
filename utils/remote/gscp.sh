#!/bin/bash

TARGET_SPEC=${@:$#} # last parameter
SOURCE_SPEC=${*%${!#}} # all parameters except the last

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
	zone=`~/host2zone.sh ${HOST}`
fi 

echo gcloud compute scp --project=rlgin-342502 --zone=${zone} ${SOURCE_SPEC} "${TARGET_SPEC}"
gcloud compute scp --project=rlgin-342502 --zone=${zone} ${SOURCE_SPEC} "${TARGET_SPEC}"

