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
        "for logfile in \`ls -tr ${LOGS}\`; \
         do \
             logfile=${LOGS}/\${logfile}; \
             echo \${logfile} @${HOST}; \
             egrep -v ' turn | bench ' \${logfile}; \
         done;"  \
         ${HOST} >> "${OUTPUT1}"
done

cat "${OUTPUT1}" | awk '	\
			/Game/ { \
				hand_count=$2; \
				hand_time=$8; if (index($0,"nobody")==0){hand_time=$13;} \
				total_time=total_time+hand_time; } \
			/ing[.][.]/ { \
				phase=$0;} \
			/[3a4]-vm|plate-1/ { \
				if (total_time>0 && hands_done ==0) { \
					avg=int(total_time/hand_count); tdo=int((5000-hand_count)*avg/36000); tdo=tdo/100;  \
					too=""; if (tdo>0) {too="" tdo " hrs to turnover";} \
					print hand_count " hands " int(total_time/hand_count) "ms avg  " too " " lpath;} \
				ppath=substr($0,34); print ppath; lpath=substr(ppath,index(ppath,"rlgin/logs/")+11); \
				hands_done = 0; total_time=0;} \
			/winMap/{ \
				if (hand_count>0 && hands_done ==0) {print hand_count " hands  " int(total_time/hand_count) " ms avg";} 
				print $0 " " phase; \
				hands_done = 1} \
			END { \
                                if (total_time>0 && hands_done ==0) { \
                                        avg=total_time/hand_count; tdo=int((5000-hand_count)*avg/36000); tdo=tdo/100; \
                                        too=""; if (tdo>0) {too="" tdo " hrs to turnover";} \
                                        print hand_count " hands " int(total_time/hand_count) "ms avg  " too " " lpath;}} \
			' \
	>> "${FINAL_OUTPUT}"
cat "${FINAL_OUTPUT}"

cat "${FINAL_OUTPUT}" |  awk '/winMap/{  \
			twins=$5; twins=substr(twins,1,index(twins,",")-1); \
			phase=$8; if (phase=="Training...") {train=twins;} else { \
				ii=ii+1; delta=delta+twins-train; base=base+train; \
				print "train:" train " twins:" twins " twins-train:" twins-train  " delta:" delta "  ii:" ii "  avg:" delta/ii "  id:" id ; \
				if (twins>4) { \
                                	iii=iii+1; deltai=deltai+twins-train; basei=basei+train; \
                                	# print "     train:" train " twins:" twins " twins-train:" twins-train  " deltai:" deltai "  iii:" iii "  avg:" deltai/iii "  id:" id;  \
					} \
				} \
			} \
		     /[.][0-9][.][0-9][0-9.][.2]/ { \
				id=substr($0,index($0,"HOT")+3,5);  \
			} \
		     END{ \
				print "runs=" ii "  delta=" delta "  avg=" delta/ii " on " base/ii " =" (((delta+base)/base)-1)*100"%"; \
				print "     runsi=" iii "  deltai=" deltai "  avg=" deltai/iii " on " basei/iii " =" (((deltai+basei)/basei)-1)*100"%"; \
			} \
		'

