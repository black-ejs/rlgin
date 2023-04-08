SS##!/usr/bin/bash
## run a test cycle, once for each of the weights in "weights/" subdir

TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S`
echo '#####################################################'
echo RLGIN WEIGHTS-TEST session started at "${TIMESTAMP}"

MODEL_NICKNAME=${PWD##*/}
RUN_DIR=rlgin
INPUT_WEIGHTS_PATH=weights/test
PROCESS_WEIGHTS_FILE=weights/weights.h5

echo changing directories to "${RUN_DIR}"....
cd "${RUN_DIR}"
echo "current working directory = ${PWD}"

if [[ -d "${INPUT_WEIGHTS_PATH}" ]]
then
	echo "   #### ""${INPUT_WEIGHTS_PATH}" already exists
else
	echo "   #### CREATING ""${INPUT_WEIGHTS_PATH}" 
	mkdir -p "${INPUT_WEIGHTS_PATH}" 
	cp weights/scratchGin*.h5  "${INPUT_WEIGHTS_PATH}"/
fi

for input_weights_file in `ls "${INPUT_WEIGHTS_PATH}"`
do
	echo processing weights "${input_weights_file}"
	NAME_SCENARIO="weightsTest_${MODEL_NICKNAME}.${input_weights_file}"
	LOGFILE="logs/${NAME_SCENARIO}.${TIMESTAMP}.log"
	INPUT_WEIGHTS="${INPUT_WEIGHTS_PATH}"/"${input_weights_file}"

	echo "-----------------------------"
	echo MODEL_NICKNAME=${MODEL_NICKNAME}
	echo NAME_SCENARIO=${NAME_SCENARIO}
	echo INPUT_WEIGHTS=${INPUT_WEIGHTS}
	echo LOGFILE=${LOGFILE}
	echo "     ------------------------"

	echo updating code base...
	git pull

	echo getting "${MODEL_NICKNAME}"-specific params....
	cp ../ginDQNParameters.py."${MODEL_NICKNAME}" ginDQNParameters.py

	echo cleaning up fram any previous runs...
	[ -e "${PROCESS_WEIGHTS_FILE}" ] && rm "${PROCESS_WEIGHTS_FILE}"

	echo copying input weights....
	cp "${INPUT_WEIGHTS}" "${PROCESS_WEIGHTS_FILE}"

	TSSS=`date -u +%Y-%m-%d_%H-%M-%S`
	echo launching weights testing processi at $TSSS...
	python learningGin.py --name_scenario "${NAME_SCENARIO}" --logfile "${LOGFILE}" 
	TSSS=`date -u +%Y-%m-%d_%H-%M-%S`
	echo weights testing  process completed at $TSSS

done

cd ..
echo '#####################################################'


