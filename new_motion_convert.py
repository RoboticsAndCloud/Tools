"""
@Brief: Process the data collected from ASCC environment.
@Author: Fei L
@Data: 03/14/2022
"""

from datetime import datetime
from datetime import timedelta

import os

DAY_FORMAT_STR = '%Y-%m-%d'
DATE_HOUR_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DATE_HOUR_TIME_FORMAT_DIR = '%Y-%m-%d-%H-%M-%S'


ASCC_DATE_HOUR_TIME_FORMAT = '%Y%m%d%H%M%S'


TRAIN_RUNNING_TIME_FORMAT = "%H:%M:%S"


def convertMotionFiles(copy_flag=False):
    path = '/home/ascc/LF_Workspace/Bayes_model/IROS23/ADL_HMM_BAYES/Data_Apartment/ASCC_OFFLINE_0708_Final/Watch/Motion'
    count = 0
    dir = path
    for fn in os.listdir(path):
        if os.path.isdir(dir + '/' + fn):
            print(fn)
          

            source_dir = dir + '/' + fn + '/*_motion.txt'

            new_dir = dir + '/' + fn + '/motion.txt'

            cp_cmd = 'cp -r ' + source_dir + ' ' + new_dir 

            print(cp_cmd)
            try:
                if copy_flag:
                    os.system(cp_cmd)
            except Exception as e:
                print(e)
                pass
            

            count = count +1

        else:
            print('fn:', fn)
    
    print('cnt:', count)

convertMotionFiles(copy_flag=True)