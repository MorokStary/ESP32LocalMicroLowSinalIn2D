import argparse
import asyncio
import json
import random
import time
from typing import List

import numpy as np
import paho.mqtt.client as mqtt


async def publish_loop(host: str, port: int, topic: str, fps: float, mics: List[List[float]]):
    """Publish random coordinates with spectrum at the given rate."""
    client = mqtt.Client()
    connected = asyncio.Event()

    def on_connect(client, userdata, flags, rc):  # noqa: D401
        if rc == 0:
            connected.set()
            client.subscribe(topic + "/cmd")

    def on_disconnect(client, userdata, rc):  # noqa: D401
        connected.clear()

    def on_message(client, userdata, msg):  # noqa: D401
        if msg.topic.endswith("/cmd") and msg.payload.decode() == "get_mics":
            payload = json.dumps({"mics": mics})
            client.publish(topic, payload)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=5)
    client.connect_async(host, port)
    client.loop_start()
    await connected.wait()

    interval = 1.0 / fps
    send_mics = True
    try:
        while True:
            ts = time.time()
            x = random.uniform(0, 10)
            y = random.uniform(0, 10)
            intensity = random.random()
            spectrum = (
                np.abs(np.fft.rfft(np.random.randn(128))) / 64
            ).tolist()

            payload = {
                "timestamp": ts,
                "coords": [x, y],
                "intensity": intensity,
                "spectrum": spectrum,
            }
            if send_mics:
                payload["mics"] = mics
                send_mics = False
            client.publish(topic, json.dumps(payload))
            await asyncio.sleep(interval)
    finally:
        client.loop_stop()
        client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Real-time JSON simulator")
    parser.add_argument("--host", default="broker.mqttdashboard.com")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="USTYM/LPNU")
    parser.add_argument("--fps", type=float, default=15.0, help="Frames per second")
    args = parser.parse_args()

    mics = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

    asyncio.run(publish_loop(args.host, args.port, args.topic, args.fps, mics))


if __name__ == "__main__":
    main()
