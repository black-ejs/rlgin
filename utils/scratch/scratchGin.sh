#!/usr/bin/bash 
## this script is usually invoked with "nohup" or the equivalent 
set -x
 
SCRATCH_ID=${1:-0}  

TIMESTAMP=`date -u +%Y-%m-%d_%H%M%S` 
echo '#####################################################' 
echo RLGIN NEW-MODEL scratch session started at "${TIMESTAMP}" 
 
MODEL_NICKNAME=${PWD##*/} 
RUN_DIR=rlgin 
LOCAL_REPO=rlgin
 
echo changing directories to "${RUN_DIR}".... 
if [ ! -d ${RUN_DIR} ]
then
	mkdir -p ${RUN_DIR}
fi
cd "${RUN_DIR}" 
echo "current working directory = {$PWD}" 
 
echo setting up logging and weights management.... 
LOGPATH="logs" 
NAME_SCENARIO="scratchGin_${MODEL_NICKNAME}.${SCRATCH_ID}" 
LOGROOT="${NAME_SCENARIO}" 
LOGFILE="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.log" 
CONSOLE_OUTPUT="${LOGPATH}/${LOGROOT}.${TIMESTAMP}.sysout" 
WEIGHTSPATH="weights" 
WEIGHTSROOT="${LOGROOT}" 
WEIGHTS_OUTPUT_FILE="${WEIGHTSPATH}/${WEIGHTSROOT}.${TIMESTAMP}.h5" 
 
echo "-----------------------------" 
echo MODEL_NICKNAME="${MODEL_NICKNAME}" 
echo NAME_SCENARIO="${NAME_SCENARIO}" 
echo LOGFILE="${LOGFILE}" 
echo WEIGHTS_OUTPUT_FILE="${WEIGHTS_OUTPUT_FILE}" 
echo "-----------------------------" 
 
#git pull 
if [[ -d ${RLGIN_BATCH_LOCAL_REPO} ]]
then
	echo updating code base.... 
	repoback=`pwd`
	TMPREPO=${RLGIN_BATCH_TMPDIR}/rb-repo.zip
	cd ${RLGIN_BATCH_LOCAL_REPO}
	git archive --format zip HEAD >  ${TMPREPO}
	cd "${repoback}"
	echo updating code base.... 
	unzip -o ${TMPREPO}
	echo waiting for the unzip to finish.... 
	while [ ! X`ps -ef | grep unzip | grep -v grep`X == XX ]
	do
		sleep 3
	done
	cd "${repoback}"
else
	echo ${RLGIN_BATCH_LOCAL_REPO} not fouund, skipping update of code base.... 
fi
 
echo getting "${MODEL_NICKNAME}"-specific params.... 
cp ../ginDQNParameters.py.${MODEL_NICKNAME} ginDQNParameters.py 
 
echo cleaning up fram any previous runs... 
[ -e weights/weights.*.h5.post_training ] && rm weights/weights.h5.post_training 
 
echo checking python...
which python
python --version

# 4/2023 conda broken in certain sub-shell situations, including ssh/nohup/&
echo confirming conda
which conda
if [[ -e "/opt/conda/etc/profile.d/conda.sh" ]]
then
	source /opt/conda/etc/profile.d/conda.sh
fi
conda activate

echo launching scratchGin process... 
python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}" 
echo scratchGin process completed 
 
echo capturing weights to "${WEIGHTS_OUTPUT_FILE}" ... 
[ -e weights/weights.*.h5.post_training ] && cp weights/weights.*.h5.post_training "${WEIGHTS_OUTPUT_FILE}" 
 
cd .. 
echo '#####################################################'




