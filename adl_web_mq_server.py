"""
@Brief: Mq server, for get the notice when received files from WMU and Send the notice to the CNN model for recognition
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request



DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME = 'DATA_FILE_RECEIVED_FROM_WMU'
DATA_RECOGNITION_FROM_WMU_EVENT_NAME = 'DATA_RECOGNITION_FROM_WMU'

DATA_RECOGNITION_FINAL_TO_ADL_EVENT_NAME = 'DATA_RECOGNITION_TO_ADL'

STOP_ADL_SERVER = 'stop_adl_server'

DATA_TYPE = 'type'
DATA_CURRENT = 'current_time'
DATA_FILE = 'file'
DATA_TYPE_IMAGE = 'image'
DATA_TYPE_SOUND = 'audio'
DATA_TYPE_MOTION = 'motion'



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')

name_space = ''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stop', methods=['GET', 'POST'])
def push_stop():
    print('data')
    event_name = STOP_ADL_SERVER
    broadcasted_data = {'data': "stop"}
    socketio.emit(event_name, broadcasted_data, namespace=name_space)
    return 'done!'

@app.route('/push', methods=['GET', 'POST'])
def push_once():
    print('data')
    event_name = DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME
    broadcasted_data = {'data': "test message!"}
    socketio.emit(event_name, broadcasted_data, namespace=name_space)
    return 'done!'

@app.route('/notice_files', methods=['GET', 'POST'])
def notice():
    data = request.json
    print('data:', data)
    
    event_name = DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME
    broadcasted_data = data
    socketio.emit(event_name, broadcasted_data, namespace=name_space)
    return 'done!'

@app.route('/notice_recognition', methods=['GET', 'POST'])
def notice_recognition():
    data = request.json
    print('data:', data)
    
    event_name = DATA_RECOGNITION_FINAL_TO_ADL_EVENT_NAME
    broadcasted_data = data
    socketio.emit(event_name, broadcasted_data, namespace=name_space)
    return 'done!'

@socketio.on(DATA_RECOGNITION_FROM_WMU_EVENT_NAME, namespace=name_space)
def on_msg_recognition_result(data):
    # send the notice to the main to get the recognition results
    event_name = DATA_RECOGNITION_FINAL_TO_ADL_EVENT_NAME
    broadcasted_data = data
    socketio.emit(event_name, broadcasted_data, namespace=name_space)
    print('Got recognition result:', data)
    return 'done!'


# @socketio.on(DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME, namespace=name_space)
# def on_msg_recognition_result(data):
#     # send the notice to the main to get the recognition results
#     event_name = DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME
#     broadcasted_data = data
#     socketio.emit(event_name, broadcasted_data, namespace=name_space)
#     print('Got file from wmu, redirect result:', data)
#     return 'done!'


    # event_name = DATA_FILE_RECEIVED_FROM_WMU_EVENT_NAME
    # broadcasted_data = {DATA_TYPE : DATA_TYPE_IMAGE, DATA_FILE:file, DATA_CURRENT: cur_time }
    # socketio.emit(event_name, broadcasted_data, namespace=name_space)


@socketio.on('connect', namespace=name_space)
def connected_msg():
    print('client connected.')

@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    print('client disconnected.')

@socketio.on('my_event', namespace=name_space)
def mtest_message(message):
    print(message)
    emit('my_response',
         {'data': message['data'], 'count': 1})


if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

