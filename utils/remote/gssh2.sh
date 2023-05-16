#!/bin/sh
set -x

HOST=${1}

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_SOURCE_DIR="`dirname ${0}`"

zp=`${CURRENT_SCRIPT_SOURCE_DIR}/host2zone.sh ${HOST}`
zone=`echo $zp | cut -f1 "-d "`
project=`echo $zp | cut -f2 "-d "`
#project=`echo $zp | awk '{print $2}'

echo gcloud compute ssh --zone $zone --project $project edward_schwarz_tonigooddog_com@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
gcloud compute ssh --zone $zone --project $project edward_schwarz_tonigooddog_com@${HOST} $2 $3 $4 $5 $6 $7 $8 $9 
