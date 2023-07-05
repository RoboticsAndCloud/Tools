# This files contains your custom actions which can be used to run
# custom Python code.
#
#https://pypi.org/project/openmeteo-py/
#https://open-meteo.com/en/docs#daily=weathercode

import requests

def post_http_request(api, json_msg, sender='default'):
    #INSERT WEBHOOK API URL HERE
    rest_api = api
    messages = json_msg

    try:
        data = requests.get(
            rest_api
        )
    except Exception as e:
        print(e)
        return None
    # A JSON Array Object is returned: each element has a user field along
    # with a text, image, or other resource field signifying the output
    # print(json.dumps(data.json(), indent=2))
    messages = []
    res_dict = data.json()
    try:
        for next_response in res_dict:
            if "current_weather" in next_response:
                messages = res_dict[next_response]
        # Output all but one of the Rasa dialogs
    except Exception as e:
        print("message got error " + str(e))
        return None

    if len(messages) == 0:
        messages = ["no response from api"]
        return ''

    return messages

weather_map = {
        '0': 'clear sky',
        '1': 'cloudy',
        '2': 'cloudy',
        '3': 'cloudy',
        }

class ActionGetWeather(object):
    def name(self):
        return 'action_get_weather'


    def run(self):

        # Stillwater, OK, USA
        city = 'Stillwater'
        country = 'USA'
        latitude = 36.11560710
        longitude = -97.05836810

        #curl "https://api.open-meteo.com/v1/forecast?latitude=36.11560710&longitude=-97.05836810&current_weather=true"
        res = self.post_request(latitude, longitude)
        weatherRes = ''

        if res:
            weatherRes = 'It\'s ' + weather_map['3'] + ' and ' + str(res['temperature']) \
                          + '°C in ' + city + ', ' + country + '.'
        return weatherRes


    def post_request(self, latitude, longitude):

	# send a message
        request_api = 'https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current_weather=true'.format(latitude, longitude)

        json_data = {
	#        "chat_id": chat_id,
	#        "text": message
        }
        return post_http_request(request_api, json_data)

#******************* Main function ********************************************
if __name__=="__main__":
	w = ActionGetWeather()
	print(w.run())
