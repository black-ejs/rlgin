# set -x

echo ${1} | ~/gssh.sh $2 2>/dev/null | awk '{if (p==1) {print $0;}}/permitted by/{p=1;}'
# echo ${1} | ~/gssh.sh $2 

