import argparse
import time
import numpy as np
import msgpack
import paho.mqtt.client as mqtt


def pink_noise(n):
    # Simple pink noise using Voss-McCartney algorithm
    num_rows = 16
    array = np.random.randn(num_rows, n)
    array = np.cumsum(array, axis=1)
    weights = 2 ** np.arange(num_rows)[:, None]
    return np.sum(array / weights, axis=0)


def generate_packet(size, snr_db, sample_rate):
    t = np.arange(size) / sample_rate
    signal = 0.1 * np.sin(2 * np.pi * 1000 * t)  # 1 kHz weak sine

    white = np.random.randn(size)
    pink = pink_noise(size)

    # Combine white and pink noise equally
    noise = white + pink

    # Normalize noise and apply SNR
    signal_power = np.mean(signal**2)
    noise_power = np.mean(noise**2)
    target_noise_power = signal_power / (10 ** (snr_db / 10))
    noise *= np.sqrt(target_noise_power / noise_power)

    data = signal + noise
    return data.astype(np.float32)


def main():
    parser = argparse.ArgumentParser(description="ESP32 signal simulator")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default="USTYM/LPNU", help="MQTT topic")
    parser.add_argument(
        "--snr", type=float, default=10.0, help="Signal-to-noise ratio (dB)"
    )
    parser.add_argument("--rate", type=int, default=16000, help="Sampling rate")
    parser.add_argument("--size", type=int, default=1024, help="Packet size")
    parser.add_argument("--packets", type=int, default=100, help="Number of packets")
    parser.add_argument(
        "--realtime", action="store_true", help="Run at 2x real-time speed"
    )
    args = parser.parse_args()

    client = mqtt.Client()
    client.connect(args.host, args.port)

    for seq in range(args.packets):
        samples = generate_packet(args.size, args.snr, args.rate)
        payload = msgpack.packb(
            {"header": "ESP32_SIM", "seq": seq, "data": samples.tolist()}
        )
        client.publish(args.topic, payload)
        if args.realtime:
            time.sleep(args.size / (2 * args.rate))

    client.disconnect()


if __name__ == "__main__":
    main()
