#!/bin/bash
#set -x

verbose=0
if [[ "X$1X" == "XverboseX" ]]
then
    verbose=1
fi

## must see the mount
BAD_MOUNT=0
rbsr_basename=`basename ${RLGIN_BATCH_SERIES_ROOT}`
ls_rbsr=`ls -l ~ 2>/dev/null | grep ${rbsr_basename}`
if [[ "'${ls_rbsr}'" == *?* ]]
then 
    BAD_MOUNT=1
fi	
if [[ ! -d ${RLGIN_BATCH_SERIES_ROOT} || ${BAD_MOUNT} == 1 ]]
then
    if [[ $verbose == 1 ]] 
    then 
	    echo "${RLGIN_BATCH_SERIES_ROOT} is not a valid directory"
    fi

    ## perhaps something else is in the way, or a busted mount
    if [[ -e ${RLGIN_BATCH_SERIES_ROOT} || ${BAD_MOUNT} == 1 ]]
    then
        if [[ $verbose == 1 ]] 
        then 
            echo "${RLGIN_BATCH_SERIES_ROOT} exists, but is not a directory, ls returns"
            echo "    ${ls_rbsr}"
            echo "dismounting...."
            fusermount -u "${RLGIN_BATCH_SERIES_ROOT}" 
	else
            fusermount -u "${RLGIN_BATCH_SERIES_ROOT}" 2>/dev/null
        fi
        
        ## after a dismount, we should see the "local" directory for the mount point
        if [ ! -d ${RLGIN_BATCH_SERIES_ROOT} ]
        then
            if [[ $verbose == 1 ]] 
            then 
                echo "${RLGIN_BATCH_SERIES_ROOT} is STILL not a valid directory"
            fi
            if [[ -e ${RLGIN_BATCH_SERIES_ROOT} ]]
	    then
                if [[ $verbose == 1 ]] 
                then 
                    echo "${RLGIN_BATCH_SERIES_ROOT} STILL exists, but is not a directory, ls returned "
                    echo "    `ls -latr ${RLGIN_BATCH_SERIES_ROOT} 2>&1`"
                    echo "removing it"
                fi
                rm -rf ${RLGIN_BATCH_SERIES_ROOT}
            fi
        fi
    fi
    if [[ $verbose == 1 ]] 
    then 
        echo re-creating ${RLGIN_BATCH_SERIES_ROOT}
    fi
    mkdir -p ${RLGIN_BATCH_SERIES_ROOT}
fi

rbsr_contents=`ls ${RLGIN_BATCH_SERIES_ROOT}`
if [[ "X${rbsr_contents}X" == XX ]]
then
    if [[ $verbose == 1 ]] 
    then 
        echo "${RLGIN_BATCH_SERIES_ROOT} is empty"
        echo "mounting shared bucket"
    	gcsfuse --debug_fuse --debug_fs --debug_gcs --file-mode 744 ${RLGIN_BATCH_EXECUTION_BUCKET} ${RLGIN_BATCH_SERIES_ROOT}
    else
    	gcsfuse --debug_fuse --debug_fs --debug_gcs --file-mode 744 ${RLGIN_BATCH_EXECUTION_BUCKET} ${RLGIN_BATCH_SERIES_ROOT} 2>&1 > /dev/null
        #### --stat-cache-ttl 0 --type-cache-ttl 0 
        # unmount with  
        #     fusermount -u "${RLGIN_BATCH_SERIES_ROOT}"
    fi
else
    ## something is there, make sure it is what we seek
    if [ ! -d ${RLGIN_BATCH_PARAMS} ]
    then
        if [[ $verbose == 1 ]] 
        then
            echo "${RLGIN_BATCH_SERIES_ROOT} is not empty, but "
	    echo "it does not a contain ${RLGIN_BATCH_PARAMS},"
            echo "ls returned:"
            echo "    `ls -latr ${RLGIN_BATCH_SERIES_ROOT}`"
            echo "more than I can handle, exiting with code 44"
        fi
        exit 44
    fi
fi

