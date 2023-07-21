#!/bin/bash
cd `dirname $0`
cd "../log" || exit 1

#you must place this file in ${module_path}/opbin,and log file in ${module_path}/log
#log file name like ${module}.${hostname}.INFO.work.log.*
#module name ,change this for other module
readonly module="meu-gateway"

readonly hostname="$(hostname | awk -F '.' '{print $1}')"

#log file dest dir, gfs path
#readonly dest_dir="/home/work/log/argus/${module}/"

#find file name like this
filename="${module}*.log"

#if dest dir does not exists,mkdir it
#if [ ! -d "${dest_dir}" ];then
#       mkdir -p "${dest_dir}" || exit 1
#fi

#get the current info,error,warning file
test -L ${module}.info.log  && readonly info_file="$(ls -l  ${module}.INFO |awk -F '->' '{print $2}')"
test -L ${module}.err.log && readonly error_file="$(ls -l  ${module}.ERROR |awk -F '->' '{print $2}')"
test -L ${module}.warn.log && readonly warning_file="$(ls -l  ${module}.WARNING |awk -F '->' '{print $2}')"
test -L ${module}.debug.log && readonly debug_file="$(ls -l  ${module}.FATAL |awk -F '->' '{print $2}')"

info_file=${module}.info.log
error_file=${module}.err.log
warning_file=${module}.warn.log
debug_file=${module}.debug.log
trace_file=${module}.trace.log
access_debug_file=${module}.access.debug.log
access_file=${module}.access.log
#gc_file="iqproxy-gc.log"

grep_str="$info_file $error_file $warning_file $debug_file $tarce_file $access_file $access_debug_file"

grep_str=$(echo $grep_str| sed 's/ /\|/g')

#mv log file to dest dir, exclude current info, error,warning file
find ./ -name "${filename}" -type f -mmin +1440 | grep -Ev "$grep_str" | xargs rm -f

if [ $? -eq 0 ];then
       	echo "logRemove : ok"
else
       	echo "logRemove : error"
fi