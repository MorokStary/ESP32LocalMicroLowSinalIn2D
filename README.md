# ESP32LocalMicroLowSinalIn2D

This project contains Arduino and Python code for acquiring audio data from four microphones and locating a sound source using Time Difference of Arrival (TDOA).

## Microcontroller simulation

If you do not have the Arduino board connected, you can emulate its serial output using the script `python_codes/mcu_simulator.py`.  The simulator
produces four microphone signals with appropriate inter-channel delays and
sends them over a virtual serial port (by default `COM11`).

1. Run the simulator (change the port if necessary):

   ```bash
   python3 python_codes/mcu_simulator.py COM11
   ```

   Leave the simulator running.

2. In a separate terminal, start the acquisition script using the same port:

   ```bash
   python3 python_codes/arduino_data_acquisiton_main.py COM11
   ```

Stop the simulator with `Ctrl+C` when you are done.

## Graphical interface

The main user interface is implemented in `python_codes/tk_app.py`.  It relies
on Tkinter and provides controls for starting an acquisition and selecting the
signal processing algorithm.  After data are captured the window displays
several plots and the estimated position of the sound source.

### Features

- **Algorithm selection** – choose between `correlation`, `wavelet`, `rpa` and
  `dpe` for the time delay estimation.
- **Start Acquisition** – opens the serial port, waits until a sample exceeds
  `1.75 V` and records additional data for processing.
- **Time Domain tab** – shows the raw waveforms from all four microphones.
- **Spectrogram tab** – displays the spectrogram of each signal.
- **Wavelet tab** – available when the wavelet method is used and shows the
  detection curves.
- **RPA tab** – visualises the recurrence plot analysis detection results.
- **DPE tab** – shows the curves obtained with the discrete pulse energy method.
- **Localization tab** – presents a 3D view of the microphone arrangement and
  the computed coordinates.

### Important functions

- `read_signals(port="COM6", baud=115200, threshold=1.75, iterations=50)` –
  reads values from the serial port until the threshold is exceeded and returns
  the collected samples.
- `start_acquisition()` – handler for the acquisition button. It triggers
  reading the signals, processes them using the selected algorithm, logs the
  event to the SQLite database and updates the plots.
- `process_signals(signals, fs, method)` – splits the raw data into four
  channels, computes the time differences and estimates the source coordinates.
- `update_plots(sigs, fs, method, coords)` – refreshes the graphs on all tabs
  using the latest data and coordinates.
