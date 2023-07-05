#!/noah/bin/python3
#coding=utf-8
import os
import traceback
import sys
import json
import logging
import logging.handlers
import subprocess
import datetime
import time

'''
    验证argus-relay账号是否有falcon.noah.all服务单元的监控读权限，覆盖olive
    http://localhost:8557/falcon/access/check?username=argus-relay&type=r&service_list\[\]=falcon.docker.all

    {
    data: true
    message: "OK"
    server: "nj01-noah-fff18.nj01.xx.com"
    success: true
    }
'''

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system('mkdir -p log')

#logger
logger=''

def init_log(log_file):
    global logger
    logger= logging.getLogger()
    logger.setLevel(logging.INFO)

    #handler=logging.FileHandler(log_file)
    handler=logging.handlers.RotatingFileHandler(log_file, maxBytes=1024*1024*1024*1.8, backupCount=2)
    handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s\
[line:%(lineno)d] %(levelname)s %(message)s'))
    logger.addHandler(handler)


def load_json_data(json_str):
    '''
        load json data
    '''
    try:
        json_obj = json.loads(json_str)
        return json_obj
    except Exception:
        exstr = traceback.format_exc()
        logger.error("load json data failed,%s" % (exstr))
        print_status(1)
        sys.exit(0)


def check_user_auth():
    global logger
    '''
        check user auth
    '''
    cmd='curl -s -m 15 "http://localhost:8557/falcon/access/check?username=%s&type=r&\
service_list\[\]=%s"' % (username, service_list)

    dtime = datetime.datetime.now()
    ans_time = time.mktime(dtime.timetuple())
    # time = 1510555963
    print ans_time
    print "\\n"

    postData = '{"data":[{"productName": "fordemo","namespace": "0.first.fordemo","namespaceType": "instance","metrics": [{"name": "thirdparty.thirdTaskName.my_test2_metric","timestamp": %d,"statisticsValue": {"max": 3,"min": 1,"cnt": 3,"sum": 6},"cycle": 10}],"processType": "save"}]}' %(ans_time)

    print postData

    cmd='curl -X POST -H "Content-type: application/json" "http://szth-y02-for-private-cloud-test101.szth.xx.com:8800/v1/_data" -v -d ' + "'" + postData + "'"
    print cmd 

    try:
        return_str=load_json_data(subprocess.check_output(cmd, shell=True, universal_newlines=True))
        logger.info(return_str)
        print_status(0)

        # if 'success' in return_str and 'data' in return_str:
        #     if return_str['success'] and not return_str['data']:
        #         print_status(0)
        #     else:
        #         print_status(1)
        #         logger.error("user auth check failed")
        # else:
        #     logger.error("user auth check failed")
        #     print_status(1)
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        print_status(1)


def print_status(status):
    print("user_auth_status: %d" % (status))


if __name__ == '__main__':
    #日志路径
    log_file = './log/user_auth.log'

    init_log(log_file)

    username = 'argus-relay'
    service_list = 'falcon.docker.all'

    check_user_auth()