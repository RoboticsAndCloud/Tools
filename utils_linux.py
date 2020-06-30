#!/usr/bin/python
################################################################################ #
# Copyright (c) 2020 ASCC LAB, OSU. All Rights Reserved
# ################################################################################

"""
This module provide tools function.
Authors: fei(fei.liang@okstate.edu)
Date: 2020/05/25 17:23:06
"""

import datetime
import socket
import subprocess
import os

"""
Brief: get file count of a director

Raises:
     NotImplementedError
     FileNotFoundError
"""
def get_file_count_of_dir(dir, prefix=''):
    path = dir
    count = 0
    for fn in os.listdir(path):
        if os.path.isfile(dir + '/' + fn):
            if prefix != '':
                if prefix in fn:
                    count = count + 1
            else:
                count = count + 1
        else:
            print('fn:', fn)
    # count = sum([len(files) for root, dirs, files in os.walk(dir)])
    return count

"""
Brief: get file list of a director

Raises:
     NotImplementedError
     FileNotFoundError
"""
def get_file_list_of_dir(dir, prefix=''):
    path = dir
    count = 0
    file_list = []
    for fn in os.listdir(path):
        file_path = dir + '/' + fn
        if os.path.isfile(file_path):
            if prefix != '':
                if prefix in fn:
                    file_list.append(file_path)
            else:
                file_list.append(file_path)
        else:
            print('fn:', fn)

    return file_list


def getCurrentTimestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def isRunning(process_name):
    try:
        process = len(os.popen(
            'ps aux | grep "' + process_name + '" | grep -v grep | grep -v tail | grep -v keepH5ssAlive').readlines())
        if process >= 1:
            return True
        else:
            return False
    except:
        print("Check process ERROR!!!")
        return False

def get_process_id(name):
    child = subprocess.Popen(["pgrep", "-f", name], stdout=subprocess.PIPE, shell=False)
    response = child.communicate()[0]
    return response


def IsUp(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((ip,int(port)))
        s.close()
        s.shutdown(2)
        print '%d is open' % port
        return True
    except:
        print '%d is down' % port
        return False

if __name__ == '__main__':
    if not IsUp('127.0.0.1', 7777):
        print("port is down")

    pid = get_process_id("python")

