import socket
import time
from datetime import datetime
import requests
import sys
import os
import random
import struct

STATE_ACTIVITY_TRIGGER_NAME = 9

RESULT_FILE = './result.txt'


IPRECEIVE = "10.227.96.41"
PORT = 49000

BREAK_TIME = 30
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

state =-1

res_list = []

def handler_service(conn):

    unpacker = struct.Struct('I')
    data = conn.recv(unpacker.size)
    unpacked_data = unpacker.unpack(data)
    state = unpacked_data[0]
    #print('Got state:', state)

    if (state == STATE_ACTIVITY_TRIGGER_NAME):
        socket_name_handler(conn)


    return 0

def socket_name_handler(conn):
    global res_list

    unpacker = struct.Struct('10s 20s')
    data = conn.recv(unpacker.size)
    unpacked_data = unpacker.unpack(data)
    data = unpacked_data

    #print("socket image handlerdata:", data)
    group = data[0].decode('utf-8')
    student = data[1].decode('utf-8')
    res_list.append((group, student))

    res_file = RESULT_FILE
    res_str = str(group) + '__' + str(student)
    res_str = group + '__' + student

    now = datetime.now()
    dt_string = now.strftime(DATE_TIME_FORMAT)
    print("Date and time =", dt_string)
    current_time = dt_string + '   '

    with open(res_file, 'a+') as f:
        f.write(current_time)
        f.write(res_str)
        f.write('\n')
    if len(res_list) >= 3:
        display()
        time.sleep(BREAK_TIME)

    return 0

def display():
    global res_list

    group = res_list[0][0]
    student = res_list[0][1]
    print("Congradulations!")
    print("Group:", group, " Student:", student)

    res_list = []

def server():
    global PORT
    PORT = PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    IP = IPRECEIVE
    s.bind((IP, PORT))
    print("Server established! IP:", IP)
    print("PORT:",PORT)
    s.listen(20)
    while True:
        conn, addr = s.accept()

        handler_service(conn)

        conn.close()

    return 0


if __name__ == "__main__":
    server()

