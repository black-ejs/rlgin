#!/bin/sh
#set -x

HOST=${1}

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"

zone=`${CURRENT_SCRIPT_SOURCE_DIR}/host2zone.sh ${HOST}`

echo gcloud compute ssh --zone $zone --project rlgin-342502 edward_schwarz@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
gcloud compute ssh --zone $zone --project rlgin-342502 edward_schwarz@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
