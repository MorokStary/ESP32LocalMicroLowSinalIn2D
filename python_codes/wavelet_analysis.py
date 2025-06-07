import numpy as np
import matplotlib.pyplot as plt
import pywt


def wavelet_detection(
    s1,
    s2,
    s3,
    s4,
    fs,
    threshold=0.6,
    wavelet="morl",
    show=True,
    axes=None,
):

    """Detect events using a wavelet-based method similar to MATLAB wavelet_s.m.

    Parameters
    ----------
    s1, s2, s3, s4 : array_like
        Signals from the four microphones.
    fs : int or float
        Sampling frequency in Hz.
    threshold : float, optional
        Relative threshold applied to the detection curves. The default is 0.6.
    wavelet : str, optional
        Name of a continuous wavelet supported by :mod:`pywt`. Default is
        ``'morl'``.
    show : bool, optional
        If True, plot the detection curves.

    Returns
    -------
    tuple of float
        Estimated TDOA values ``(td12, td13, td14)`` in seconds.
    """
    a0 = 2 ** (1 / 64)
    scales = a0 ** np.arange(64, 4 * 64 + 1)

    # ensure numpy arrays for ``pywt.cwt``
    s1 = np.asarray(s1)
    s2 = np.asarray(s2)
    s3 = np.asarray(s3)
    s4 = np.asarray(s4)

    cw = pywt.ContinuousWavelet(wavelet)

    coeffs1, _ = pywt.cwt(s1, scales, cw, 1 / fs)
    coeffs2, _ = pywt.cwt(s2, scales, cw, 1 / fs)
    coeffs3, _ = pywt.cwt(s3, scales, cw, 1 / fs)
    coeffs4, _ = pywt.cwt(s4, scales, cw, 1 / fs)

    det1 = np.sum(np.abs(coeffs1), axis=0)
    det2 = np.sum(np.abs(coeffs2), axis=0)
    det3 = np.sum(np.abs(coeffs3), axis=0)
    det4 = np.sum(np.abs(coeffs4), axis=0)

    idx1 = np.argmax(det1 > threshold * det1.max())
    idx2 = np.argmax(det2 > threshold * det2.max())
    idx3 = np.argmax(det3 > threshold * det3.max())
    idx4 = np.argmax(det4 > threshold * det4.max())

    t1 = idx1 / fs
    t2 = idx2 / fs
    t3 = idx3 / fs
    t4 = idx4 / fs

    if axes is not None:
        axs = axes
    elif show:
        fig, axs = plt.subplots(2, 2)
    else:
        axs = None

    if axs is not None:
        axs[0, 0].plot(det1)
        axs[0, 0].set_title("Detection curve 1")
        axs[0, 1].plot(det2)
        axs[0, 1].set_title("Detection curve 2")
        axs[1, 0].plot(det3)
        axs[1, 0].set_title("Detection curve 3")
        axs[1, 1].plot(det4)
        axs[1, 1].set_title("Detection curve 4")
        for ax in axs.flat:
            ax.set(xlabel="Samples", ylabel="Amplitude")
        if show and axes is None:
            plt.tight_layout()
            plt.show()


    td12 = t1 - t2
    td13 = t1 - t3
    td14 = t1 - t4
    return td12, td13, td14, (det1, det2, det3, det4)
