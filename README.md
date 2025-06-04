# ESP32LocalMicroLowSinalIn2D
The system consists of a microphone array connected to an ESP32.

## Simulation Module
`sim_module.py` emulates the ESP32 output while hardware is unavailable. The script
creates weak sinusoidal signals, adds synthetic white and pink noise according
to a chosen SNR, quantizes the result to `float32` and publishes packets over
MQTT using a MessagePack payload. The default broker is the public HiveMQ instance
`broker.mqttdashboard.com` and the default topic is `USTYM/LPNU`.

A real‑time mode can be enabled with `--realtime` which transmits data at twice
the normal sampling rate for faster algorithm testing.

`sim_realtime.py` publishes JSON frames with random coordinates, intensity and a
simple spectrum at a configurable frame rate. The first message also contains the
microphone geometry so that the browser can display it. Geometry can be requested
again by sending `get_mics` to the `<topic>/cmd` MQTT topic.

## Calibration Suite
`calibration_suite.py` generates multichannel test signals using synthetic room
impulse responses produced by [Pyroomacoustics](https://github.com/LCAV/pyroomacoustics).
The script sends packets to an MQTT broker with the true source coordinates and
varying tone amplitudes. This data can be collected by `HostCollector` to evaluate
localization accuracy and tune classification thresholds.

## Web Interface
`web_interface.py` launches a Flask application that subscribes to the simulator
MQTT topic and forwards JSON frames to the browser via SocketIO. The dashboard
plots microphone positions, the detected source and its spectrum in real time using Plotly.

## Data Storage
`data_storage.py` implements asynchronous writes to a SQLite database. Event samples
and filter parameters are kept in separate tables indexed by timestamp for quick
statistical queries.

## Setup

1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running

- **Signal simulator**:
  ```bash
  python sim_module.py --host broker.mqttdashboard.com --port 1883 --topic USTYM/LPNU
  ```
  Add `--realtime` to double the output speed.

- **Real-time JSON simulator**:
  ```bash
  python sim_realtime.py --host broker.mqttdashboard.com --port 1883 --topic USTYM/LPNU
  ```

- **Calibration suite**:
  ```bash
  python calibration_suite.py --host broker.mqttdashboard.com --port 1883 --topic USTYM/CALIB
  ```

- **Web interface**:
  ```bash
  python web_interface.py
  ```
  Then open `http://localhost:5000/` in a browser.
