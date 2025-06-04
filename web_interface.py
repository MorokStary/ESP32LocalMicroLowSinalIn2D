import random
import time
import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from data_storage import DataStorage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
# use eventlet for async workers
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

storage = DataStorage()

@app.get('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():

    def send_coords():
        while True:
            socketio.sleep(1)
            data = {
                'x': random.randint(0, 9),
                'y': random.randint(0, 9),
                'intensity': random.random(),
            }
            storage.insert_event(time.time(), data['x'], data['y'], data['intensity'])
            emit('coords', data)

    eventlet.spawn(send_coords)


def main():
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        storage.close()


if __name__ == '__main__':
    main()
