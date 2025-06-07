import numpy as np


def tdoa(td1, td2, td3, x, y, z, v=343, eps=1e-6):
    """Compute source coordinates using the TDOA method.

    Small or zero time delays can lead to divisions by zero and numerical
    issues.  ``eps`` is used as a lower bound to avoid these problems.
    """

    time_delays = [0, td1, td2, td3]
    time_delays = [td if abs(td) > eps else eps * (1 if td >= 0 else -1) for td in time_delays]
    n = len(time_delays)

    Amat = np.zeros((n, 1))
    Bmat = np.zeros((n, 1))
    Cmat = np.zeros((n, 1))
    Dmat = np.zeros((n, 1))

    for i in range(2, n):
        Amat[i] = (1 / (v * time_delays[i])) * (-2 * x[0] + 2 * x[i]) - (
            1 / (v * time_delays[1])
        ) * (-2 * x[1] + 2 * x[2])
        Bmat[i] = (1 / (v * time_delays[i])) * (-2 * y[0] + 2 * y[i]) - (
            1 / (v * time_delays[1])
        ) * (-2 * y[1] + 2 * y[2])
        Cmat[i] = (1 / (v * time_delays[i])) * (-2 * z[0] + 2 * z[i]) - (
            1 / (v * time_delays[1])
        ) * (-2 * z[1] + 2 * z[2])
        sum1 = (x[0] ** 2) + (y[0] ** 2) + (z[0] ** 2) - (x[i] ** 2) - (y[i] ** 2) - (
            z[i] ** 2
        )
        sum2 = (x[0] ** 2) + (y[0] ** 2) + (z[0] ** 2) - (x[1] ** 2) - (y[1] ** 2) - (
            z[1] ** 2
        )
        Dmat[i] = v * (time_delays[i] - time_delays[1]) + (1 / (v * time_delays[i])) * sum1 - (
            1 / (v * time_delays[1])
        ) * sum2

    M = np.zeros((n + 1, 3))
    D = np.zeros((n + 1, 1))
    for i in range(n):
        M[i, 0] = Amat[i]
        M[i, 1] = Bmat[i]
        M[i, 2] = Cmat[i]
        D[i] = Dmat[i]

    M = np.array(M[2:n, :])
    D = np.array(D[2:n])
    D = np.multiply(-1, D)

    Minv = np.linalg.pinv(M)
    T = np.dot(Minv, D)
    xs, ys, zs = T.flatten()
    return xs, ys, zs
