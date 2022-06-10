"""
Brief: This code is used to send the request to the game server, do not change the code.

Author: ASCC Lab
Date: 06/01/2022

"""
import requests

# Update the IP Address according the target server
BASE_URL = 'http://10.227.100.46:3000/api/actions/answer/'

def answer_request(group):
    url = BASE_URL + str(group)
    buzzer_handler(url)

def buzzer_handler(url):
    try:
        r = requests.get(url, verify = False)
        #print(r)
    except Exception as e:
        print("buzzer url error:", e)
    return 0
