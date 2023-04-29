#!/bin/sh
#set -x

HOST=${1}

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"

zp=`${CURRENT_SCRIPT_SOURCE_DIR}/host2zone.sh ${HOST}`
echo zp is $zp
zone=`echo $zp | cut -f1 "-d "`
project=`echo $zp | cut -f2 "-d "`

echo gcloud compute ssh --zone $zone --project $project edward_schwarz@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
gcloud compute ssh --zone $zone --project $project edward_schwarz@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
