#!/bin/bash
#for i in {1..5}
#do
#   echo "Welcome $i times"
#done


now=`date '+%Y-%m-%d %H:%M:%S'` # 
grepFlag='rl_adl_main' # process name
thisLog='./watchlog' # 
trainLog='./rl_0404_new_acc_privacy_0.45_energy_0.25_acc_0.3motion1.txt'

baseDir="."
sleepTime=300s # 

#if [ ! -f "$baseDir/run.sh" ]; then
#    echo "$baseDir/run.sh missing, check again" >> "$thisLog"
#    exit
#fi

source ~/LF_Workspace/venv3.8_rl_pytorch/bin/activate
cd /home/ascc/LF_Workspace/Bayes_model/IROS23/ADL_HMM_BAYES/RL_model
#python rl_adl_main.py >> $trainLog &

while [ 0 -lt 1 ]
do
    now=`date '+%Y-%m-%d %H:%M:%S'`
    ret=`ps aux | grep "$grepFlag" | grep -v grep | wc -l`
    if [ $ret -eq 0 ]; then # ps
        echo "$now process not exists ,restart process now... " >> "$thisLog"
        #./run.sh
	#source ~/LF_Workspace/venv3.8_rl_pytorch/bin/activate
        cd /home/ascc/LF_Workspace/Bayes_model/IROS23/ADL_HMM_BAYES/RL_model
	python rl_adl_main_0.1.py >> $trainLog &
        echo "$now restart done ..... "  >> "$thisLog"
    else
        echo "$now process exists , sleep $sleepTime seconds " >> "$thisLog"
	grep epi $trainLog >> "$thisLog"

    fi
    sleep $sleepTime
done
