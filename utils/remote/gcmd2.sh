#set -x

echo arg1=${1}
echo arg2=${2}
echo arg3=${3}
echo arg4=${4}
echo ${1} | ~/gssh2.sh ${2} 
#echo ${1} | ~/gssh.sh ${2} 2>/dev/null | awk '{if (p==1) {print $0;}}/permitted by/{p=1;}'

