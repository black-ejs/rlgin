#!/bin/sh
#set -x

HOST=${1}
PROJECT=rlgin-342502
zone=`gcloud compute instances list --project=${PROJECT} | grep ${HOST} | awk '{print $2}'`
if [[ X"${zone}"X = "XX" ]] 
then
	PROJECT=rlgin-batch
	zone=`gcloud compute instances list --project=${PROJECT} | grep ${HOST} | awk '{print $2}'`
fi
echo $zone $PROJECT

