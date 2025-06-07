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
