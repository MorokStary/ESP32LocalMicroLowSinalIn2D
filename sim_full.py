import argparse
import asyncio
import random
import time
from typing import List

import numpy as np
import msgpack
import paho.mqtt.client as mqtt


C = 343.0  # speed of sound m/s


def pink_noise(n: int) -> np.ndarray:
    """Generate pink noise using Voss-McCartney algorithm."""
    num_rows = 16
    array = np.random.randn(num_rows, n)
    array = np.cumsum(array, axis=1)
    weights = 2 ** np.arange(num_rows)[:, None]
    return np.sum(array / weights, axis=0)


def generate_event(
    mics: List[List[float]],
    sample_rate: int,
    max_delay: float = 0.02,
    pulse_len: int = 64,
    amp: float | None = None,
) -> tuple[np.ndarray, float, float, float]:
    """Create multichannel signals with a single short pulse."""
    duration = max_delay + 0.05
    n_samples = int(duration * sample_rate)

    # random source position within 0..10 m square
    x = random.uniform(0, 10)
    y = random.uniform(0, 10)
    if amp is None:
        amp = random.uniform(0.1, 1.0)

    signals = 0.01 * (np.random.randn(len(mics), n_samples) + pink_noise(n_samples))

    pulse = amp * np.hanning(pulse_len)
    for ch, (mx, my) in enumerate(mics):
        dist = ((x - mx) ** 2 + (y - my) ** 2) ** 0.5
        delay = dist / C
        idx = int(delay * sample_rate)
        if idx + pulse_len < n_samples:
            signals[ch, idx : idx + pulse_len] += pulse

    return signals.astype(np.float32), x, y, amp


def estimate_delays(signals: np.ndarray, sr: int) -> List[float]:
    base = signals[0]
    delays = [0.0]
    for ch in range(1, signals.shape[0]):
        corr = np.correlate(signals[ch], base, mode="full")
        idx = np.argmax(corr) - (len(base) - 1)
        delays.append(idx / sr)
    return delays


def estimate_position(delays: List[float], mics: List[List[float]]) -> List[float]:
    m0 = mics[0]
    A = []
    b = []
    for d, (mx, my) in zip(delays[1:], mics[1:]):
        A.append([2 * (mx - m0[0]), 2 * (my - m0[1])])
        b.append((d * C) ** 2 - mx ** 2 - my ** 2 + m0[0] ** 2 + m0[1] ** 2)
    A = np.array(A)
    b = np.array(b)
    pos, *_ = np.linalg.lstsq(A, b, rcond=None)
    return pos.tolist()


def event_intensity(signals: np.ndarray) -> float:
    return float(np.mean(signals**2))


def event_spectrum(signals: np.ndarray) -> List[float]:
    spec = np.abs(np.fft.rfft(signals[0]))
    return (spec / np.max(spec)).tolist()


async def publish_loop(host: str, port: int, topic: str, sr: int, events: int) -> None:
    mics = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
    client = mqtt.Client()
    connected = asyncio.Event()

    def on_connect(client, userdata, flags, rc):  # noqa: D401
        if rc == 0:
            connected.set()

    client.on_connect = on_connect
    client.reconnect_delay_set(min_delay=1, max_delay=5)
    client.connect_async(host, port)
    client.loop_start()
    await connected.wait()

    try:
        for i in range(events):
            amp = 0.2 * (i + 1)
            signals, x, y, _ = generate_event(mics, sr, amp=amp)
            delays = estimate_delays(signals, sr)
            coords = estimate_position(delays, mics)
            intensity = event_intensity(signals)
            spectrum = event_spectrum(signals)
            payload = msgpack.packb(
                {
                    "timestamp": time.time(),
                    "coords": coords,
                    "intensity": intensity,
                    "spectrum": spectrum,
                    "amp": amp,
                    "mics": mics,
                },
                use_bin_type=True,
            )
            client.publish(topic, payload)
            await asyncio.sleep(random.uniform(0.2, 1.0))
    finally:
        client.loop_stop()
        client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Full ESP32 simulator")
    parser.add_argument("--host", default="broker.mqttdashboard.com")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="USTYM/LPNU")
    parser.add_argument("--rate", type=int, default=16000)
    parser.add_argument("--events", type=int, default=5, help="number of events")
    args = parser.parse_args()
    asyncio.run(publish_loop(args.host, args.port, args.topic, args.rate, args.events))


if __name__ == "__main__":
    main()
