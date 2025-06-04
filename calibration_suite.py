import argparse
import numpy as np
import msgpack
import paho.mqtt.client as mqtt
import pyroomacoustics as pra


def generate_signals(room_dim, mic_positions, source_pos, amplitudes, fs, tone_freq, duration):
    """Generate multichannel signals using Pyroomacoustics."""
    n_samples = int(duration * fs)
    t = np.arange(n_samples) / fs
    tone = np.sin(2 * np.pi * tone_freq * t)

    mic_array = pra.MicrophoneArray(np.array(mic_positions).T, fs)
    room = pra.ShoeBox(room_dim, fs=fs, max_order=0)
    room.add_microphone_array(mic_array)
    room.add_source(source_pos)
    room.compute_rir()
    rirs = room.rir

    signals = []
    for amp in amplitudes:
        s = amp * tone
        channels = []
        for m in range(len(mic_positions)):
            conv = np.convolve(s, rirs[m][0])[:n_samples]
            channels.append(conv.astype(np.float32))
        signals.append(np.stack(channels))
    return signals


def main():
    parser = argparse.ArgumentParser(description="Calibration signal generator")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default="USTYM/CALIB", help="MQTT topic")
    parser.add_argument("--rate", type=int, default=16000, help="Sampling rate")
    parser.add_argument("--freq", type=float, default=1000.0, help="Tone frequency")
    parser.add_argument("--duration", type=float, default=0.1, help="Tone duration")
    args = parser.parse_args()

    room_dim = [5.0, 4.0, 3.0]
    mic_positions = [
        [1.0, 1.0, 1.5],
        [1.1, 1.0, 1.5],
        [1.0, 1.1, 1.5],
        [1.1, 1.1, 1.5],
    ]
    source_pos = [2.5, 2.0, 1.5]
    amplitudes = [0.1, 0.2, 0.5, 1.0]

    packets = generate_signals(
        room_dim, mic_positions, source_pos, amplitudes, args.rate, args.freq, args.duration
    )

    client = mqtt.Client()
    client.connect(args.host, args.port)

    for seq, data in enumerate(packets):
        payload = msgpack.packb(
            {
                "header": "CALIB_SUITE",
                "seq": seq,
                "coords": source_pos,
                "amplitude": amplitudes[seq],
                "data": data.tolist(),
            }
        )
        client.publish(args.topic, payload)

    client.disconnect()


if __name__ == "__main__":
    main()
