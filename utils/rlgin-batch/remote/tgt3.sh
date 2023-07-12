#set -x

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"

RLGIN_BATCH_REPO_URL='https://github.com/black-ejs/rlgin'
MYTMP=${TMPDIR}tmp$$
mkdir -p ${MYTMP}
cd ${MYTMP}

git clone -q ${RLGIN_BATCH_REPO_URL} 

FINAL_OUTPUT="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out
OUTPUT1="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out.1
rm ${FINAL_OUTPUT}
rm ${OUTPUT1}

TRAINING_GROUND_TARGETS=${1:-~/training_ground_targets.txt}
REMOTE_USERID="edward_schwarz_tonigooddog_com"

echo "${CURRENT_SCRIPT_NAME}: checking targets from ${TRAINING_GROUND_TARGETS} at `date`"

for PROJECT in `grep -v "^[#]" ${TRAINING_GROUND_TARGETS}`
do
	LEARNDIR=`echo "${PROJECT}" | cut -d@ -f1`
	HOST=`echo "${PROJECT}" | cut -d@ -f2`
	echo ----XXX---- ${LEARNDIR} " " @${HOST}
	DRIVER_DIR=/home/${REMOTE_USERID}/dev/projects/training_ground/${LEARNDIR}
	LOGS=${DRIVER_DIR}/logs

	# this will find the currently-being-worked-on guys
	~/gscp.sh ${MYTMP}/rlgin/utils/rlgin-batch/remote/tgt.py ${REMOTE_USERID}@${HOST}:~/tgt.py
	~/gcmd.sh \
	"DD=\`ps -ef | grep learningGin | grep -v grep | awk \"{print \\\\\\\$13}\"\`; \
	for logfile in \${DD}; \
	do \
		echo \${logfile} @${HOST}; \
		egrep -v ' turn | bench | future_rewards=| entire list' \${logfile} ; \
	done > ~/tgt3.tmp; python ~/tgt.py ~/tgt3.tmp | sort -V"  \
		${HOST} >> "${OUTPUT1}"

	# this will find the already-done guys
	if [[ "X${ALREADY_DONE}X" == *" ${LEARNDIR} "* ]]
	then
		# already processed this guy
		echo "skipping completed for ${LEARNDIR} @${HOST}"
		dummy=dummy
	else
		echo "checking completed for ${LEARNDIR} @${HOST}"
		ALREADY_DONE="${ALREADY_DONE} ${LEARNDIR} "	
		~/gcmd.sh \
		"DD=\`grep -c \" took \" ${LOGS}/* | grep -v \":0\$\" | cut -f1 -d: \`; \
		for logfile in \${DD}; \
		do \
			echo \${logfile} @${HOST}; \
			egrep -v ' turn | bench | future_rewards=| entire list ' \${logfile}; \
		done > ~/tgt3.tmp; python ~/tgt.py ~/tgt3.tmp | sort -V "  \
		${HOST} >> "${OUTPUT1}"
	fi
done

# #####################################
# #####################################

cp "${OUTPUT1}" ${FINAL_OUTPUT} 
cat ${FINAL_OUTPUT}

echo "${CURRENT_SCRIPT_NAME} completed at `date`"

