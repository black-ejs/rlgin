#!/bin/bash
#set -x

JOB_PARAMS_PATH=${RLGIN_BATCH_PARAMS}/job-params.txt
let LINE_NUMBER=${BATCH_TASK_INDEX}+1
export JOB_PARAMS=`head -"${LINE_NUMBER}" "${JOB_PARAMS_PATH}" | tail -1`
TMPFILE=${RLGIN_BATCH_TMPDIR}/$(date +%n)_job_params
echo ${JOB_PARAMS} | awk '{split($0,params,":"); 
                        for (i in params) {
                            print "export RLGIN_BATCH_JP_"params[i]}}' > ${TMPFILE}
export JOB_PARAMS_SCRIPT=${TMPFILE}
source ${JOB_PARAMS_SCRIPT}

