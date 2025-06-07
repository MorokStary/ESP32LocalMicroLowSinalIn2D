# ESP32LocalMicroLowSinalIn2D

This project contains Arduino and Python code for acquiring audio data from four microphones and locating a sound source using Time Difference of Arrival (TDOA).

## Microcontroller simulation

If you do not have the Arduino board connected, you can emulate its serial output using the script `python_codes/mcu_simulator.py`.

1. Run the simulator:

   ```bash
   python3 python_codes/mcu_simulator.py
   ```

   The script prints the path of a virtual serial device (for example `/dev/pts/3`).
   Leave the simulator running.

2. In a separate terminal, start the acquisition script using that port:

   ```bash
   python3 python_codes/arduino_data_acquisiton_main.py /dev/pts/3
   ```

   Replace `/dev/pts/3` with the path displayed by the simulator.

Stop the simulator with `Ctrl+C` when you are done.
