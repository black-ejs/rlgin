sudo bash -
export RLGIN_BATCH_JOB_PARAMS_PATH=BLG/mtrain
export BATCH_JOB_ID=rb-job-manual
export BATCH_JOB_UID=rb-job-manual
export BATCH_TASK_COUNT=1
export BATCH_TASK_INDEX=0
git clone https://github.com/black-ejs/rlgin
chmod a+x rlgin/utils/rlgin-batch/gcloud-config/.job-script
nohup rlgin/utils/rlgin-batch/gcloud-config/.job-script
