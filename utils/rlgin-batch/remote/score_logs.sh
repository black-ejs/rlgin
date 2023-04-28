#!/bin/bash

target_folder_name="${1:-CYB1}"
remote_host="${2:-rb-t-s50-vm-11}"
training_ground=dev/projects/training_ground
target_path=${training_ground}/${target_folder_name}/logs/
tmpfile=score_logs.tmp.$$

~/gcmd.sh "set -x;for p in \`ls ${target_path} \
			| grep \"Gin_.*${target_folder_name}\" \`; \
	do \
		echo \$p > ~/${tmpfile}; \
		grep winMap ${target_path}\$p >> ~/${tmpfile}; \
		cat ~/${tmpfile}; \
	done" \
	${remote_host} \
      | awk '
	/Gin_.*[.]202[0-9]-/ {
		tot=0; 
		cc=0; 
		p=split($0,aa,"/"); 
		fn=aa[p]; 
	}
	/winMap/ {
		w=$5;
		w=substr(w,1,length(w)-1); 
		tot=tot+w; 
		if (cc==1) {
			print tot " " fn;
		}
		cc=1;
	}
	'  \
 | sort -n
