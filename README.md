# ESP32LocalMicroLowSinalIn2D
The system consists of a microphone array connected to an ESP32.

## Simulation Module
`sim_full.py` emulates the ESP32 firmware in a single program. It continuously
produces multi-channel measurements containing short impulses on top of pink and
white noise, determines the inter-channel delays, estimates the source position
and energy intensity, forms a spectral vector and sends all fields packed with
MessagePack. Each packet also carries the microphone geometry so the dashboard
can display the array without additional commands.

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
  python sim_full.py --host broker.mqttdashboard.com --port 1883 --topic USTYM/LPNU
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
