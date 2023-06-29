from datetime import datetime
import socket
from timeit import default_timer as timer
import struct
import time
import requests


import adl_type_constants

STATE_ACTIVITY_TRIGGER_NAME = 9

IPSEND = "192.168.1.131" # white box
PORT = 59100 # wearable server

BASE_URL_NOTICE_RECOGNITION_RES = 'http://127.0.0.1:5000/notice_recognition'
BASE_URL_NOTICE_FILES_RECEIVED = 'http://127.0.0.1:5000/notice_files'
BASE_URL_PUSH = 'http://127.0.0.1:5000/push'


state = -1
activeTime = 1

Headers = {

'Content-Type': 'application/json',

'Client_ID': 'YXBpLmVmcGVyZmVjdA==',

'Client_Secret': 'aVNmVzh3Vk9kM3cxQTh1OQ=='
}


def notice_request_handler(url):
    try:
        r = requests.get(url, verify = False)
        #print(r)
    except Exception as e:
        print("request url error:", e)
    return 0

def notice_post_handler(url, data):
    try:
        r = requests.post(url, headers=Headers, json=data, verify = False)
        #print(r)
    except Exception as e:
        print("post url error:", e)
        return -1
    return 0


def cmd_mode_sending_handler(IP, PORT, var):
    port = PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s.connect((IP, PORT))

    values = (var)
    packer = struct.Struct('I')
    packed_data = packer.pack(values)
    s.send(packed_data)

    s.close()

def audio_sending_handler(ipsend, port, file, type):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ipsend, port))

    values = (type)
    packer = struct.Struct('I')
    packed_data = packer.pack(values)
    s.send(packed_data)

    now = datetime.now()
    dt_string = now.strftime(adl_type_constants.DATE_TIME_FORMAT)
    print("Date and time =", dt_string)

    current_time = dt_string

    values = (current_time.encode())
    packer = struct.Struct('14s')
    packed_data = packer.pack(values)
    s.send(packed_data)

    with open(file, 'rb') as f:
        for l in f: s.sendall(l)
    print('Audio sent:', file)

    s.close()

    return 0



if __name__ == "__main__":

    #IPSEND = "192.168.1.135"
    IPSEND = "192.168.1.131" # white box
    PORT = 59100 # wearable server

    while (True):
        # default event
        file = ''
        if activeTime % 3 == 0: 
            cmd_mode_sending_handler(adl_type_constants.WMU_IPRECEIVE, adl_type_constants.WMU_RECEIVE_PORT,
                                                            adl_type_constants.STATE_ENV_ACTIVITY_CMD_TAKING_MOTION)
            # audio_sending_handler(IPSEND, PORT, file, adl_type_constants.STATE_MEDICATION_ACTIVITY_CMD_PLAY_AUDIO)

        activeTime = activeTime + 1
        print("Active Time:", activeTime)
        time.sleep(1)


