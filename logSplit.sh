#!/bin/sh
cd `dirname $0`
cd ".." || exit 1
readonly WORK_DIR=`pwd`
log_dir=$WORK_DIR/log/access

monitor_file=$log_dir/meu-gateway.access.debug.log
if [ $# == 1 ] ; then
       		monitor_file=$1 #log文件的绝对路径
fi

file_size=`du  -m $monitor_file | awk '{print $1}'`
if [ $file_size -ge  100 ]
then
        if [ ! -d $log_dir ]
        then
                mkdir $log_dir   #创建保存切割文件目录,这个路径可以自行修改，保存到你想要的目录
        fi
        cp $monitor_file $monitor_file-`date +%Y%m%d%H%M%S`   #保存日志文件
        echo `date +%Y-%m-%d-%H:%M:%S`"$monitor_file:文件切割"  >>$log_dir/split.log  #记录切割日志
        echo "" > $monitor_file    #清空件内容
fi