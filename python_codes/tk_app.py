import tkinter as tk
from tkinter import messagebox
import serial
import time

import numpy as np

from compute_correlation import corelatia
from tdoa import tdoa
from db_logger import log_event
from data_visualization import plot_3d_coordinates
from wavelet_analysis import wavelet_detection
from rpa import rpa_detection
from dpe import dpe_detection


def read_signals(port='COM6', baud=115200, threshold=1.75, iterations=50):
    ser = serial.Serial(port, baudrate=baud)
    data = []
    try:
        while True:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            data.append(float(line))
            if len(line) and line.replace('.', '', 1).isdigit() and float(line) > threshold:
                for _ in range(iterations):
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if line:
                        data.append(float(line))
                break
    finally:
        ser.close()
    return data


def process_signals(signals, fs, method="correlation"):
    s1, s2, s3, s4 = [], [], [], []
    for i in range(len(signals) - 3):
        s4.append(signals[i])
        s1.append(signals[i + 1])
        s2.append(signals[i + 2])
        s3.append(signals[i + 3])
    if method == "correlation":
        td1, td2, td3 = corelatia(s1, s2, s3, s4, fs)
    elif method == "wavelet":
        td1, td2, td3 = wavelet_detection(s1, s2, s3, s4, fs, show=False)
    elif method == "rpa":
        td1, td2, td3 = rpa_detection(s1, s2, s3, s4, fs)
    elif method == "dpe":
        td1, td2, td3 = dpe_detection(s1, s2, s3, s4, fs)
    else:
        raise ValueError(f"Unknown method: {method}")
    xs, ys, zs = tdoa(td1, td2, td3, [0, 0.17, 0.17, 0.72], [0, 0, 0.85, 0.61], [0, 0, 0, 0.13])
    return float(signals[-1]), xs, ys, zs


def start_acquisition():
    try:
        data = read_signals()
        fs = 1000  # placeholder sampling rate
        method = algorithm_var.get()
        amplitude, xs, ys, zs = process_signals(data, fs, method)
        log_event(amplitude, xs, ys, zs)
        messagebox.showinfo(
            'Result',
            f'Method: {method}\nLast amplitude: {amplitude}\nSource at ({xs:.2f}, {ys:.2f}, {zs:.2f})'
        )
        plot_3d_coordinates(xs, ys, zs)
    except Exception as e:
        messagebox.showerror('Error', str(e))


root = tk.Tk()
root.title('Sound Source Localization')

algorithm_var = tk.StringVar(value="correlation")
options = ["correlation", "wavelet", "rpa", "dpe"]
option_menu = tk.OptionMenu(root, algorithm_var, *options)
option_menu.pack(padx=20, pady=10)

start_btn = tk.Button(root, text='Start Acquisition', command=start_acquisition)
start_btn.pack(padx=20, pady=10)

root.mainloop()

