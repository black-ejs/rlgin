#!/bin/sh
#set -x

zone=us-west1-b
if [[ "$1" == *"east4"* ]]; then
  zone=us-east4-c
fi
if [[ "$1" == *"east4c"* ]]; then
  zone=us-east4-c
fi
if [[ "$1" == *"cent1a"* ]]; then
  zone=us-central1-a
fi
if [[ "$1" == *"learn-a-vm-2"* ]]; then
  zone=us-central1-a
fi
if [[ "$1" == *"1xv100-template-1"* ]]; then
  zone=us-east1-c
fi

echo gcloud compute ssh --zone $zone --project rlgin-342502 edward_schwarz@$1 $2 $3 $4 $5 $6 $7 $8 $9 
gcloud compute ssh --zone $zone --project rlgin-342502 edward_schwarz@$1 $2 $3 $4 $5 $6 $7 $8 $9 
