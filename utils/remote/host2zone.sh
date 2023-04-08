#!/bin/sh
#set -x

HOST=${1}
zone=`gcloud compute instances list --project=rlgin-342502 | grep ${HOST} | awk '{print $2}'`
echo $zone
