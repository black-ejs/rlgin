##!/usr/bin/bash

MODEL_NICKNAME=${PWD##*/}

git clone https://github.com/black-ejs/rlgin
mkdir rlgin/logs
mkdir rlgin/weights
cp rlgin/ginDQNParameters.py ginDQNParameters.py.${MODEL_NICKNAME}
cp rlgin/utils/trainGin.sh .
chmod a+x ./trainGin.sh
