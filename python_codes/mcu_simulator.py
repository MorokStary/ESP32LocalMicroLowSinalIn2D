import os
import pty
import random
import time
import sys


def main():
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)
    print(f"Simulated serial port: {slave_name}")
    sys.stdout.flush()

    try:
        while True:
            # Generate four random voltage readings between 0 and 3.3V
            readings = [random.uniform(0, 3.3) for _ in range(4)]
            for value in readings:
                line = f"{value:.2f}\r\n".encode()
                os.write(master, line)
                time.sleep(0.01)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
