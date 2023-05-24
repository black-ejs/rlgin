#!/bin/bash
#set -x

target_folder_name="${1:-CYB1}"
remote_host="${2:-rb-t-s50-vm-11}"
training_ground=dev/projects/training_ground
target_path=${training_ground}/${target_folder_name}/logs/
tmpfile=score_logs.tmp.$$

~/gcmd.sh "for p in \`ls ${target_path} \
			| grep \"Gin_.*${target_folder_name}\" \`; \
	do \
		echo \$p > ~/${tmpfile}; \
		egrep \"total_reward|winMap|ing[.][.][.]\" ${target_path}\$p >> ~/${tmpfile}; \
		cat ~/${tmpfile}; \
	done; rm score_logs.tmp.*" \
	${remote_host} \
      | awk '
	/Gin_.*[.]202[0-9]-/ {
		if (length(fn)>0) {
			print tot_r " " tot "  " fn;
		}
		tot=0; 
		tot_r=0;
		p=split($0,aa,"/"); 
		fn=aa[p]; 
	}
	/Training[.][.][.]/ {phase="train"}
	/Testing[.][.][.]/ {phase="test"}
	/Pretesting[.][.][.]/ {phase="pretest"}
	/total_reward/ {
		if (phase=="test") {
			r=$3
			r=substr(r,1,length(r)-2)
			tot_r+=r
		}
	}
	/winMap/ {
		if (phase=="test") {
			w=$5;
			w=substr(w,1,length(w)-1); 
			tot=tot+w; 
		}
	}
	END {
		if (length(fn)>0) {
			print tot_r " "tot "  " fn;
		}
	}
	'  \
 | sort -n
