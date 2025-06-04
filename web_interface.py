from datetime import timedelta
import random
import time
import eventlet
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    decode_token,
)
from flask_socketio import SocketIO, emit

from data_storage import DataStorage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
app.config['JWT_SECRET_KEY'] = 'change-this-jwt-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)
# use eventlet for async workers
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

storage = DataStorage()


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return redirect(url_for('login_page'))


@app.post('/login')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password:
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({'msg': 'Bad credentials'}), 401


@app.get('/login')
def login_page():
    return render_template('login.html')


@app.get('/')
@jwt_required()
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        return False  # disconnect
    try:
        decode_token(token)
    except Exception:
        return False

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
