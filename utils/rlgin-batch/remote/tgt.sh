#set -x

CURRENT_SCRIPT_NAME="`basename ${0}`"
CURRENT_SCRIPT_DIR="`dirname ${0}`"

FINAL_OUTPUT="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out
OUTPUT1="${CURRENT_SCRIPT_DIR}"/"${CURRENT_SCRIPT_NAME}".out.1
rm ${FINAL_OUTPUT}
rm ${OUTPUT1}

TRAINING_GROUND_TARGETS=${1:-~/training_ground_targets.txt}
REMOTE_USERID="edward_schwarz_tonigooddog_com"

echo "checking targets from ${TRAINING_GROUND_TARGETS}"

for PROJECT in `grep -v "^[#]" ${TRAINING_GROUND_TARGETS}`
do
	LEARNDIR=`echo "${PROJECT}" | cut -d@ -f1`
	HOST=`echo "${PROJECT}" | cut -d@ -f2`
	echo ----XXX---- ${LEARNDIR} " " @${HOST}
	DRIVER_DIR=/home/${REMOTE_USERID}/dev/projects/training_ground/${LEARNDIR}
	LOGS=${DRIVER_DIR}/logs

	# this will find the currently-being-worked-on guys
	~/gcmd.sh \
	"DD=\`ps -ef | grep learningGin | grep -v grep | awk \"{print \\\\\\\$13}\"\`; \
	for logfile in \${DD}; \
	do \
		echo \${logfile} @${HOST}; \
		egrep -v ' turn | bench ' \${logfile}; \
	done"  \
		${HOST} >> "${OUTPUT1}"

	# this will find the already-done guys
	if [[ "${ALREADY_DONE}"} == *" ${LEARNDIR} "* ]]
	then
		# already processed this guy
		echo "skipping ${LEARNDIR} @${HOST}"
	else
		ALREADY_DONE="${ALREADY_DONE} ${LEARNDIR} "	
		~/gcmd.sh \
		"DD=\`grep -c \" took \" ${LOGS}/* | grep -v \":0\$\" | cut -f1 -d: \`; \
		for logfile in \${DD}; \
		do \
			echo \${logfile} @${HOST}; \
			egrep -v ' turn | bench ' \${logfile}; \
		done"  \
		${HOST} >> "${OUTPUT1}"
	fi
done

cat "${OUTPUT1}" | awk '	
	/Game/ { 
		hand_count=$2; 
		hand_time=$8; if (index($0,"nobody")==0){hand_time=$13;} 
		total_time=total_time+hand_time; } 
	/ing[.][.]/ { 
		phase=$0;} 
	/r.*[34]-vm|r.*plate-| [@]rb-job-.*/ { 
		if (total_time>0 && hands_done==0 && hand_count>0) { 
			avg=int(total_time/hand_count); 
			tdo=int((5000-hand_count)*avg/36000)/100;  
			too=""; 
			if (tdo>0) {
				too="" tdo " hrs to turnover";} 
			print hand_count " hands " int(total_time/hand_count) "ms avg  " too " " lpath;} 
		ppath=substr($0,34); 
		print ppath; 
		lpath=substr(ppath,index(ppath,"logs/")+5); 
		hands_done = 0; total_time=0;} 
	/winMap/{ 
		if (hand_count>0 && hands_done ==0) {print hand_count " hands  " int(total_time/hand_count) " ms avg";} 
		print $0 " " phase; 
		hands_done = 1} 
	END { 
		if (total_time>0 && hand_count>0 && hands_done==0) { 
			avg=total_time/hand_count; 
			tdo=int((5000-hand_count)*avg/36000)/100; 
			too=""; 
			if (tdo>0) {
				too="" tdo " hrs to turnover";} 
			print hand_count " hands " int(total_time/hand_count) "ms avg  " too " " lpath;
			}
		} 
	' \
	>> "${FINAL_OUTPUT}"
cat "${FINAL_OUTPUT}"

cat "${FINAL_OUTPUT}" |  awk '
	/winMap/{  
		wins=$5; 
		wins=substr(wins,1,index(wins,",")-1); 
		phase=$8; 
		if (phase=="Training...") {
			train=wins; 
			if (ptrain>-1) {
				generation_gain=train-ptrain;
				tgen = tgen + generation_gain
				igen = igen + 1
				basegen += train
			} else {
				generation_gain="";
			}
			ptrain=train;
		} else { 
			twins = wins;
			ii=ii+1; 
			delta=delta+twins-train; 
			base=base+train; 
			print ii " train:" train " test:" twins " gen-gain:" generation_gain "  id:" id; 
			if (twins>4) { 
				iii=iii+1; 
				deltai=deltai+twins-train; 
				basei=basei+train; 
				# print iii " train:" train " test:" twins " gen-gain:" generation_gain "  id:" id ; 
			} else {ptrain=-1} 
		} 
	} 
	/logs\/.*[0-9]*[.][0-9]*[.][0-9]*[.]2023-.*log/ { 
		log_name_regex="[0-9]*[.][0-9]*[.][0-9]*[.]2023-"
		idpos = match($0,log_name_regex)
		front=substr($0,1,idpos-1)
		split(front,cc,"_")
		series_nick=cc[length(cc)]
		id=substr($0,idpos);
		id=substr(id,1,index(id,"2023-")-2);
		id=series_nick id
		split(id,marks,".")
		model=marks[1] "." marks[2]
		if (model!=prev_model) {
			ptrain=-1;
			print "- - - - - - - - " model} 
		prev_model = model;  
	} 
	END{ 
	if (ii >0 && igen>0 && base<0 && basegen >0) {
		print "runs=" ii "  delta=" delta  \
			"  avg=" delta/ii " on " base/ii " =" (((delta+base)/base)-1)*100"%" \
			"  gen=" tgen/igen " on " basegen/igen " =" (((tgen+basegen)/basegen)-1)*100"%" 
		if (iii > 0) {
			print "     runsi=" iii "  deltai=" deltai  "  avg=" deltai/iii  \
				" on " basei/iii " =" (((deltai+basei)/basei)-1)*100"%" 
			}
		}
	} 
	'

