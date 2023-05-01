#!/bin/bash
#set -x

echo "### ### ### assuring parameter access..."
~/.assure-mounts.sh verbose
pp=/home/edward_schwarz_tonigooddog_com/dev/projects/rlgin-batch/job-params/CYB/job-params.txt
echo "pp=" ${pp}
echo ls -l ${pp}
ls -l ${pp}
echo cat ${pp}
cat ${pp}

# LOCATE PARAMS
if [[ X"${RLGIN_BATCH_JOB_PARAMS_PATH}"X == XX ]]
then
    JOB_PARAMS_PATH=${RLGIN_BATCH_PARAMS}/job-params.txt
else
    JOB_PARAMS_PATH=${RLGIN_BATCH_PARAMS}/${RLGIN_BATCH_JOB_PARAMS_PATH}/job-params.txt
fi

# CALCULATE TASK OFFSET
let LINE_NUMBER=${BATCH_TASK_INDEX}+1

# PULL THE PARAMS LINE
export JOB_PARAMS=`head -"${LINE_NUMBER}" "${JOB_PARAMS_PATH}" | tail -1`

# PARSE AND LOAD INTO ENVIRONMENT
TMPFILE=${RLGIN_BATCH_TMPDIR}/$(date +%n)_job_params
echo ${JOB_PARAMS} | awk '{split($0,params,":"); 
                        for (i in params) {
                            print "export RLGIN_BATCH_JP_"params[i]}}' > ${TMPFILE}
export JOB_PARAMS_SCRIPT=${TMPFILE}
source ${JOB_PARAMS_SCRIPT}

