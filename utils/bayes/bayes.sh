##!/usr/bin/bash
## run a test cycle, this script is usually invoked with "nohup" or the equivalent

PYTHON_FILEBASE=bayesDqn
TIMESTAMP=`date -u +%Y-%m-%d_%H%M%S`
echo '#####################################################'
echo RLGIN "${PYTHON_FILEBASE}" session started at "${TIMESTAMP}"

MODEL_NICKNAME=${PWD##*/}
RUN_DIR=rlgin

echo changing directories to "${RUN_DIR}"....
cd "${RUN_DIR}"
echo "current working directory = {$PWD}"

LOGFILE="logs/${PYTHON_FILEBASE}_${MODEL_NICKNAME}_${TIMESTAMP}"
WEIGHTS_REPO="weights/${MODEL_NICKNAME}_${TIMESTAMP}"

echo "-----------------------------"
echo MODEL_NICKNAME=${MODEL_NICKNAME}
echo LOGFILE=${LOGFILE}
echo WEIGHTS_REPO=${WEIGHTS_REPO}
echo "-----------------------------"

echo updating code base....
git pull
echo getting "${MODEL_NICKNAME}"-specific params....
cp ../ginDQNParameters.py.${MODEL_NICKNAME} ginDQNParameters.py
echo cleaning up fram any previous runs...
[ -e "weights/weights.*h5.*post_training" ] && rm weights/weights.*h5.*post_training
echo launching bayesian process ${PYTHON_FILEBASE}...
python ${PYTHON_FILEBASE}.py > "${LOGFILE}"
echo bayesian process ${PYTHON_FILEBASE} completed

echo capturing post-training weights...
[ -e "$(WEIGHTS_REPO}"] || mkdir "${WEIGHTS_REPO}"
[ -e "weights/weights.*h5.*post_training" ] && cp weights/weights.*h5.*post_training ${WEIGHTS_REPO}

cd ..
echo '#####################################################'


