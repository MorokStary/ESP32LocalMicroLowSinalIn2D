import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import serial



from compute_correlation import corelatia
from tdoa import tdoa
from db_logger import log_event
from data_visualization import plot_3d_coordinates
from wavelet_analysis import wavelet_detection
from rpa import rpa_detection
from dpe import dpe_detection
from compute_spectogram import spectrogram


def read_signals(port="COM6", baud=115200, threshold=1.75, iterations=50):
    """Read data from the serial port until a threshold is exceeded."""

    ser = serial.Serial(port, baudrate=baud)
    data = []
    try:
        while True:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if not line:
                continue
            data.append(float(line))
            if line.replace(".", "", 1).isdigit() and float(line) > threshold:
                for _ in range(iterations):
                    line = ser.readline().decode("ascii", errors="ignore").strip()

                    if line:
                        data.append(float(line))
                break
    finally:
        ser.close()
    return data


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Sound Source Localization")

        ctrl = ttk.Frame(master)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Algorithm:").pack(side=tk.LEFT, padx=5)

        self.algorithm_var = tk.StringVar(value="correlation")
        options = ["correlation", "wavelet", "rpa", "dpe"]
        ttk.OptionMenu(ctrl, self.algorithm_var, options[0], *options).pack(side=tk.LEFT)

        ttk.Button(ctrl, text="Start Acquisition", command=self.start_acquisition).pack(side=tk.LEFT, padx=10)

        self.nb = ttk.Notebook(master)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.time_tab = ttk.Frame(self.nb)
        self.spec_tab = ttk.Frame(self.nb)
        self.wavelet_tab = ttk.Frame(self.nb)
        self.rpa_tab = ttk.Frame(self.nb)
        self.dpe_tab = ttk.Frame(self.nb)
        self.loc_tab = ttk.Frame(self.nb)

        self.nb.add(self.time_tab, text="Time Domain")
        self.nb.add(self.spec_tab, text="Spectrogram")
        self.nb.add(self.wavelet_tab, text="Wavelet")
        self.nb.add(self.rpa_tab, text="RPA")
        self.nb.add(self.dpe_tab, text="DPE")
        self.nb.add(self.loc_tab, text="Localization")

        self.fig_time, self.ax_time = plt.subplots(4, 1, figsize=(5, 4))
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=self.time_tab)
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_spec, self.ax_spec = plt.subplots(2, 2, figsize=(5, 4))
        self.canvas_spec = FigureCanvasTkAgg(self.fig_spec, master=self.spec_tab)
        self.canvas_spec.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_wave, self.ax_wave = plt.subplots(2, 2, figsize=(5, 4))
        self.canvas_wave = FigureCanvasTkAgg(self.fig_wave, master=self.wavelet_tab)
        self.canvas_wave.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_rpa, self.ax_rpa = plt.subplots(2, 2, figsize=(5, 4))
        self.canvas_rpa = FigureCanvasTkAgg(self.fig_rpa, master=self.rpa_tab)
        self.canvas_rpa.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_dpe, self.ax_dpe = plt.subplots(2, 2, figsize=(5, 4))
        self.canvas_dpe = FigureCanvasTkAgg(self.fig_dpe, master=self.dpe_tab)
        self.canvas_dpe.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_loc = plt.figure(figsize=(5, 4))
        self.ax_loc = self.fig_loc.add_subplot(111, projection="3d")
        self.canvas_loc = FigureCanvasTkAgg(self.fig_loc, master=self.loc_tab)
        self.canvas_loc.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_acquisition(self):
        try:
            data = read_signals()
            fs = 1000  # sampling frequency placeholder
            method = self.algorithm_var.get()
            amp, xs, ys, zs, sigs = self.process_signals(data, fs, method)
            log_event(amp, xs, ys, zs)
            self.update_plots(sigs, fs, method, (xs, ys, zs))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def process_signals(self, signals, fs, method):
        s1, s2, s3, s4 = [], [], [], []
        for i in range(len(signals) - 3):
            s4.append(signals[i])
            s1.append(signals[i + 1])
            s2.append(signals[i + 2])
            s3.append(signals[i + 3])
        if method == "correlation":
            td1, td2, td3 = corelatia(s1, s2, s3, s4, fs)
        elif method == "wavelet":
            td1, td2, td3, _ = wavelet_detection(s1, s2, s3, s4, fs, show=False, axes=self.ax_wave)
        elif method == "rpa":
            td1, td2, td3, _ = rpa_detection(s1, s2, s3, s4, fs, axes=self.ax_rpa)
        elif method == "dpe":
            td1, td2, td3 = dpe_detection(s1, s2, s3, s4, fs)
        else:
            raise ValueError(f"Unknown method: {method}")
        xs, ys, zs = tdoa(td1, td2, td3, [0, 0.17, 0.17, 0.72], [0, 0, 0.85, 0.61], [0, 0, 0, 0.13])
        return float(signals[-1]), xs, ys, zs, (s1, s2, s3, s4)

    def update_plots(self, sigs, fs, method, coords):
        s1, s2, s3, s4 = sigs
        for ax, sig in zip(self.ax_time, [s1, s2, s3, s4]):
            ax.clear()
            ax.plot(sig)
        self.canvas_time.draw()

        spectrogram(s1, s2, s3, s4, fs, axes=self.ax_spec, show=False)
        self.canvas_spec.draw()

        if method == "wavelet":
            self.canvas_wave.draw()
        elif method == "rpa":
            self.canvas_rpa.draw()

        x, y, z = coords
        self.ax_loc.clear()
        plot_3d_coordinates(x, y, z)
        self.canvas_loc.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

