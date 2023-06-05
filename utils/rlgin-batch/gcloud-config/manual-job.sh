sudo bash -
export RLGIN_BATCH_JOB_PARAMS_PATH=BLG/mtrain
export BATCH_JOB_ID=rb-job-manual
export BATCH_JOB_UID=rb-job-manual
export BATCH_TASK_COUNT=1
export BATCH_TASK_INDEX=0
cd ~
git clone https://github.com/black-ejs/rlgin
chmod a+x rlgin/utils/rlgin-batch/gcloud-config/.job-script
TIMESTAMP=`date -u +%Y-%m-%d_%H-%M-%S` 
nohup rlgin/utils/rlgin-batch/gcloud-config/.job-script 2>&1 > mtrain.out.${TIMESTAMP} &
