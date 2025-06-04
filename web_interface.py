import argparse
import json
import time
import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

from data_storage import DataStorage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
# use eventlet for async workers
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

storage = DataStorage()


def create_mqtt_client(host: str, port: int, topic: str) -> mqtt.Client:
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):  # noqa: D401
        if rc == 0:
            client.subscribe(topic)
            client.subscribe(topic + "/cmd")

    def on_message(client, userdata, msg):  # noqa: D401
        if msg.topic.endswith("/cmd"):
            if msg.payload.decode() == "get_mics":
                client.publish(topic + "/cmd", "ack")
            return
        data = json.loads(msg.payload.decode())
        coords = data.get("coords", [0, 0])
        storage.insert_event(time.time(), coords[0], coords[1], data.get("intensity", 0))
        socketio.emit("coords", data)

    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=5)
    client.connect_async(host, port)
    client.loop_start()
    return client


@app.get('/')
def index():
    return render_template('index.html')


def main() -> None:
    parser = argparse.ArgumentParser(description="Web dashboard")
    parser.add_argument("--host", default="broker.mqttdashboard.com")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="USTYM/LPNU")
    parser.add_argument("--listen", default="0.0.0.0")
    parser.add_argument("--web-port", type=int, default=5000)
    args = parser.parse_args()

    mqtt_client = create_mqtt_client(args.host, args.port, args.topic)

    try:
        socketio.run(app, host=args.listen, port=args.web_port)
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        storage.close()


if __name__ == '__main__':
    main()
