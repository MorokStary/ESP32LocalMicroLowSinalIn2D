import numpy as np


def phasespace(signal, dim, tau):
    """Return delay embedding of ``signal``."""
    signal = np.asarray(signal)
    n = len(signal)
    T = n - (dim - 1) * tau
    if T <= 0:
        raise ValueError("Signal too short for given embedding")
    out = np.empty((T, dim))
    for i in range(dim):
        out[:, i] = signal[i * tau : i * tau + T]
    return out


def rp_plot(P, m, t, r=0.9):
    """Compute recurrence and distance matrices."""
    P = np.asarray(P)
    r = r * np.std(P)
    X = phasespace(P, m, t)
    diff = X[:, None, :] - X[None, :, :]
    DD = np.sum(diff ** 2, axis=2)
    threshold = r ** 2
    RP = (DD <= threshold).astype(int)
    np.fill_diagonal(RP, 1)
    return RP, DD


def rpa_detection(
    s1,
    s2,
    s3,
    s4,
    fs,
    threshold=0.4,
    rp_thresh=0.9,
    show=False,
    axes=None,
):

    """Estimate TDOA using Recurrence Plot Analysis."""
    _, DD1 = rp_plot(s1, 3, 1, rp_thresh)
    _, DD2 = rp_plot(s2, 3, 1, rp_thresh)
    _, DD3 = rp_plot(s3, 3, 1, rp_thresh)
    _, DD4 = rp_plot(s4, 3, 1, rp_thresh)

    C1 = DD1.sum(axis=0)
    C2 = DD2.sum(axis=0)
    C3 = DD3.sum(axis=0)
    C4 = DD4.sum(axis=0)

    idx1 = np.argmax(C1 > threshold * C1.max())
    idx2 = np.argmax(C2 > threshold * C2.max())
    idx3 = np.argmax(C3 > threshold * C3.max())
    idx4 = np.argmax(C4 > threshold * C4.max())

    t1 = idx1 / fs
    t2 = idx2 / fs
    t3 = idx3 / fs
    t4 = idx4 / fs

    if axes is not None:
        axs = axes
    elif show:
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(2, 2)
    else:
        axs = None

    if axs is not None:

        axs[0, 0].plot(C1)
        axs[0, 0].set_title("Detection curve 1")
        axs[0, 1].plot(C2)
        axs[0, 1].set_title("Detection curve 2")
        axs[1, 0].plot(C3)
        axs[1, 0].set_title("Detection curve 3")
        axs[1, 1].plot(C4)
        axs[1, 1].set_title("Detection curve 4")
        for ax in axs.flat:
            ax.set(xlabel="Samples", ylabel="Amplitude")
        if show and axes is None:
            plt.tight_layout()
            plt.show()


    td12 = t1 - t2
    td13 = t1 - t3
    td14 = t1 - t4
    return td12, td13, td14, (C1, C2, C3, C4)

