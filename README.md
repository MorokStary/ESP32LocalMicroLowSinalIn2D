# ESP32LocalMicroLowSinalIn2D
The system consists of a microphone array connected to an ESP32.

## Simulation Module
`sim_module.py` emulates the ESP32 output while hardware is unavailable. The script
creates weak sinusoidal signals, adds synthetic white and pink noise according
to a chosen SNR, quantizes the result to `float32` and publishes packets over
MQTT using a MessagePack payload. The default topic is `USTYM/LPNU`.

A real‑time mode can be enabled with `--realtime` which transmits data at twice
the normal sampling rate for faster algorithm testing.
