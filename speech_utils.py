#!/usr/bin/python
################################################################################ #
# Copyright (c) 2020 ASCC LAB, OSU. All Rights Reserved
# ################################################################################
"""
This module provide configure file management service in i18n environment.
Authors: fei(fei.liang@okstate.edu)
Date: 2020/05/25 17:23:06
"""
import locale
import logging
import sys
import os
import time

# from google.cloud import texttospeech

import requests

class TTSTool(object):
    """Text to Speech tool. User can use TTSTool.tts() to Convert text to speech
        Reference: Google SPEECH API
    """

    def __init__(self):
        # rospy.on_shutdown(self.cleanup)
        return

    def tts(input_text):
        """
        Text to Speech, create reminder.mp3 and save into current dir
        :return: reminder.mp3
        """
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.types.SynthesisInput(text=input_text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)
        with open('reminder.mp3', 'wb') as out:
            out.write(response.audio_content)
        os.system('mplayer reminder.mp3')

    def post_data_to_rasa(rasa_api, msg, sender='default'):
        #INSERT WEBHOOK API URL HERE
        rest_rasa_api = rasa_api
        messages = msg

        # Speak message to user and save the response
        # If user doesn't respond, quietly stop, allowing user to resume later
        if messages is None:
            return
        # Else reset messages

        # Send post requests to said endpoint using the below format.
        # "sender" is used to keep track of dialog streams for different users
        try:
            data = requests.post(
                rest_rasa_api, json={"message": messages, "sender": sender}
            )
        except Exception as e:
            print(e)
            return None
        # A JSON Array Object is returned: each element has a user field along
        # with a text, image, or other resource field signifying the output
        # print(json.dumps(data.json(), indent=2))
        print(data)
        messages = []
        try:
            for next_response in data.json():
            # print(next_response)
                if "text" in next_response:
                    messages.append(next_response["text"])
            # Output all but one of the Rasa dialogs
        except Exception as e:
            print("message got error " + str(e))
            return None
        if len(messages) >= 1:
            for rasa_message in messages:
                print(rasa_message)

        # Kills code when Rasa stop responding
        if len(messages) == 0:
            messages = ["no response from rasa"]
            return

        # Allows a stream of user inputs by re-calling query_rasa recursively
        # It will only stop when either user or Rasa stops providing data
        return messages


class HttpTool(object):
    """Text to Speech tool. User can use TTSTool.tts() to Convert text to speech
        Reference: Google SPEECH API
    """

    def __init__(self):
        # rospy.on_shutdown(self.cleanup)
        return

    def tts(input_text):
        """
        Text to Speech, create reminder.mp3 and save into current dir
        :return: reminder.mp3
        """
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.types.SynthesisInput(text=input_text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)
        with open('reminder.mp3', 'wb') as out:
            out.write(response.audio_content)
        os.system('mplayer reminder.mp3')

    def post_data_to_rasa(rasa_api, json_msg, sender='default'):
        #INSERT WEBHOOK API URL HERE
        rest_rasa_api = rasa_api
        messages = json_msg

        # Speak message to user and save the response
        # If user doesn't respond, quietly stop, allowing user to resume later
        if messages is None:
            return
        # Else reset messages

        # Send post requests to said endpoint using the below format.
        # "sender" is used to keep track of dialog streams for different users
        try:
            data = requests.post(
                rest_rasa_api, json=messages
            )
        except Exception as e:
            print(e)
            return None
        # A JSON Array Object is returned: each element has a user field along
        # with a text, image, or other resource field signifying the output
        # print(json.dumps(data.json(), indent=2))
        print(data)
        messages = []
        try:
            for next_response in data.json():
            # print(next_response)
                if "text" in next_response:
                    messages.append(next_response["text"])
            # Output all but one of the Rasa dialogs
        except Exception as e:
            print("message got error " + str(e))
            return None
        if len(messages) >= 1:
            for rasa_message in messages:
                print(rasa_message)

        # Kills code when Rasa stop responding
        if len(messages) == 0:
            messages = ["no response from rasa"]
            return

        # Allows a stream of user inputs by re-calling query_rasa recursively
        # It will only stop when either user or Rasa stops providing data
        return messages

if __name__ == "__main__":
    import log
    log.init_log("./log/my_program")  # ./log/my_program.log./log/my_program.log.wf7
    logging.info("Hello World!!!")
    print("My name is Elsa.")
    # TTSTool.tts("My name is Elsa.")
    # rospy.init_node('ASCCBot_MedicationReminderTimerChecker')

    rasa_api = 'http://localhost:5005/webhooks/rest/webhook'
    rasa_api = 'https://f7388d57f110.ngrok.io/webhooks/rest/webhook'


    msg = 'Hi'
    sender = 'Elsa'
    res = TTSTool.post_data_to_rasa(rasa_api, msg, sender)
    if res == None:
        print(None)

    print("My name is Elsa. over")

