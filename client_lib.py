import socket
from timeit import default_timer as timer
import struct
import time

STATE_ACTIVITY_TRIGGER_NAME = 9

IPSEND = "10.227.96.41"
PORT = 49000

state = -1
activeTime = 1


def names_sending_handler(ipsend, port, group_name, student_name):
    PORT = port
    IP = ipsend
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))

    values = (STATE_ACTIVITY_TRIGGER_NAME)
    packer = struct.Struct('I')
    packed_data = packer.pack(values)
    s.send(packed_data)

    values = (group_name.encode('utf-8'), student_name.encode('utf-8'))
    packer = struct.Struct('10s 20s')
    packed_data = packer.pack(*values)
    s.send(packed_data)

    s.close()

    return ''

if __name__ == "__main__":

    while (True):
        # default event
        if activeTime % 3 == 0: 
            names_sending_handler(IPSEND, PORT, 'group1', 'Frank')

        activeTime = activeTime + 1
        print("Active Time:", activeTime)
        time.sleep(1)


