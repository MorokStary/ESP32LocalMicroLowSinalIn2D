"""Simulated microcontroller sending deterministic data over a serial port."""

import time
import sys
from typing import Sequence

import numpy as np
import serial


def main():
    """Send pre-generated signals with delays to the specified serial port."""

    port = sys.argv[1] if len(sys.argv) > 1 else "COM11"
    baud = 115200

    def generate_signals(
        fs: int = 1000,
        duration: float = 2.0,
        freq: float = 40.0,
        delays: Sequence[float] = (0.0, 0.0005, 0.001, 0.0015),
    ) -> np.ndarray:
        """Create a set of sine waves with different delays."""

        t = np.arange(0.0, duration, 1.0 / fs)
        base = np.sin(2 * np.pi * freq * t)
        signals = []
        for d in delays:
            shift = int(round(d * fs))
            sig = np.roll(base, shift)
            voltage = np.clip(1.65 + 1.65 * sig, 0, 3.3)
            signals.append(voltage)
        return np.array(signals)

    fs = 1000
    sigs = generate_signals(fs=fs)
    samples = sigs.shape[1]

    ser = serial.Serial(port, baudrate=baud)
    print(f"Sending data on {port} at {baud} baud")
    sys.stdout.flush()

    try:
        while True:
            for i in range(samples):
                for ch in range(sigs.shape[0]):
                    line = f"{sigs[ch, i]:.2f}\r\n".encode()
                    ser.write(line)
                    # distribute the sampling interval across channels
                    time.sleep(1 / (sigs.shape[0] * fs))
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()


if __name__ == "__main__":
    main()
