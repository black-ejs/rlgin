# set -x

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"

FINAL_OUTPUT="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out
ALL_OUTPUT_FILES="${FINAL_OUTPUT}*"
rm ${ALL_OUTPUT_FILES}

OUTPUT1="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out.1

TRAINING_GROUND_TARGETS=`~/training_ground_targets.sh`

for PROJECT in ${TRAINING_GROUND_TARGETS}
do
        LEARNDIR=`echo "${PROJECT}" | cut -d@ -f1`
        HOST=`echo "${PROJECT}" | cut -d@ -f2`
        echo --------- ${LEARNDIR} " " @${HOST}
        DRIVER_DIR=/home/edward_schwarz/dev/projects/training_ground/${LEARNDIR}
        LOGS=${DRIVER_DIR}/rlgin/logs

        ~/gcmd.sh \
       	 "echo --------- ${LEARNDIR} ' ' @${HOST}; \
	  for logfile in \`ls -tr ${LOGS}\`; \
          do \
             logfile=${LOGS}/\${logfile}; \
             echo \${logfile} @${HOST}; \
             grep ' took ' \${logfile}; \
          done;"  \
         ${HOST} >> "${FINAL_OUTPUT}"
done

cat "${FINAL_OUTPUT}" | awk '  \
		/^--/  {rr=$2; host=$3;} \
		/^[*]/ {took=$5; hsecs=(took-took%3600); h=hsecs/3600; msecs=(took-hsecs)-(took-hsecs)%60; m=msecs/60; \
		print took "secs   avg@500=" (took/5000)*1000 "  run=" rr "  host=" host "  time=" h ":" m} \
	' \
	| sort -n


