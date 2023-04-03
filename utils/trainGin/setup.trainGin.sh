##!/usr/bin/bash

MODEL_NICKNAME=${PWD##*/}

git clone https://github.com/black-ejs/rlgin
mkdir rlgin/logs
mkdir rlgin/weights
cp rlgin/ginDQNParameters.py ginDQNParameters.py.${MODEL_NICKNAME}
cp rlgin/utils/trainGin/trainGin.sh .
chmod a+x ./trainGin.sh
cp rlgin/utils/trainGin/trainDriver.sh .
chmod a+x ./trainDriver.sh

echo "*******************************************************************"
echo "****" get your weights/weights.h5.0, modify your ginDQNParameters.py, and you are ready to go
echo "*******************************************************************"
