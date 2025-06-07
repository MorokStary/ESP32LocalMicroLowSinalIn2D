"""Compute and display spectrograms for four signals."""

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


def spectrogram(s1, s2, s3, s4, fs, axes=None, show=True):
    """Plot spectrograms for the four microphone signals."""

    f1, t1, Sxx1 = signal.spectrogram(s1, fs)
    f2, t2, Sxx2 = signal.spectrogram(s2, fs)
    f3, t3, Sxx3 = signal.spectrogram(s3, fs)
    f4, t4, Sxx4 = signal.spectrogram(s4, fs)

    if axes is not None:
        axs = axes
    elif show:
        fig, axs = plt.subplots(2, 2)
    else:
        axs = None

    if axs is not None:
        axs[0, 0].pcolormesh(t1, f1, Sxx1)
        axs[0, 0].set_title('Spectrogram 1')
        axs[0, 1].pcolormesh(t2, f2, Sxx2)
        axs[0, 1].set_title('Spectrogram 2')
        axs[1, 0].pcolormesh(t3, f3, Sxx3)
        axs[1, 0].set_title('Spectrogram 3')
        axs[1, 1].pcolormesh(t4, f4, Sxx4)
        axs[1, 1].set_title('Spectrogram 4')
        for ax in axs.flat:
            ax.set(xlabel='Time [sec]', ylabel='Frequency [Hz]')
        if show and axes is None:
            plt.tight_layout()
            plt.show()

    return (f1, t1, Sxx1), (f2, t2, Sxx2), (f3, t3, Sxx3), (f4, t4, Sxx4)
