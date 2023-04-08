##!/usr/bin/bash

MODEL_NICKNAME=${PWD##*/}

cp rlgin/utils/trainGin/trainGin.sh .
chmod a+x ./trainGin.sh
cp rlgin/utils/trainGin/trainDriver.sh .
chmod a+x ./trainDriver.sh

