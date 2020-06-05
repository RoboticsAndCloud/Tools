#!/usr/bin/python
################################################################################ #
# Copyright (c) 2020 ASCC LAB, OSU. All Rights Reserved
# ################################################################################

"""
This module provide tools function.
Authors: fei(fei.liang@okstate.edu)
Date: 2020/05/25 17:23:06
"""

import socket
import subprocess


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

