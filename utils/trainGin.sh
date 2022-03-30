##!/usr/bin/bash
## run a test cycle, this script is usually invoked with "nohup" or the equivalent

MODEL_NICKNAME=${PWD##*/}
RUN_DIR=rlgin

INPUT_WEIGHTS=`ls $RUN_DIR/weights/weights.h5.* | grep '[0-9]$' | tail -1`
INPUT_GENERATION_NUMBER=${INPUT_WEIGHTS##*.}
OUTPUT_GENERATION_NUMBER=$((INPUT_GENERATION_NUMBER+1))
OUTPUT_WEIGHTS="weights/weights.h5.${OUTPUT_GENERATION_NUMBER}"

echo '#####################################################'
echo RLGIN TRAINING session started at `date -u +%Y-%m-%d_%H:%M:%S`
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
echo INPUT_GENERATION_NUMBER=${INPUT_GENERATION_NUMBER}
echo OUTPUT_GENERATION_NUMBER=${OUTPUT_GENERATION_NUMBER}
echo OUTPUT_WEIGHTS=${OUTPUT_WEIGHTS}

echo copying weights....
cp $INPUT_WEIGHTS $RUN_DIR/weights/weights.h5
echo changing directories to $RUN_DIR....
cd $RUN_DIR
echo "current working directory = {$PWD}"

echo updating code base....
git pull
echo getting ${MODEL_NICKNAME}-specific params....
cp ../ginDQNParameters.py.${MODEL_NICKNAME} ginDQNParameters.py
echo cleaning up fram any previous runs...
[ -e "weights/weights.h5.post_training" ] && rm weights/weights.h5.post_training
echo launching learning process...
python learningGin.py > logs/learning_${MODEL_NICKNAME}_`date -u +%Y-%m-%d_%H:%M:%S`
echo learning process, capturing weights...
cp weights/weights.h5.post_training $OUTPUT_WEIGHTS

cd ..
echo '#####################################################'
