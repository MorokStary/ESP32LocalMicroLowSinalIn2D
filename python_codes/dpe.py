import numpy as np


def dpe_detection(s1, s2, s3, s4, fs, level=0.35):
    """Simple amplitude threshold detection used in the MATLAB DPE script."""
    s1 = np.asarray(s1)
    s2 = np.asarray(s2)
    s3 = np.asarray(s3)
    s4 = np.asarray(s4)

    def first_idx(sig):
        for i, v in enumerate(sig[4:], start=4):
            if abs(v - 1.4) > level:
                return i
        return 0

    n1 = first_idx(s1)
    n2 = first_idx(s2)
    n3 = first_idx(s3)
    n4 = first_idx(s4)

    if not any([n1, n2, n3, n4]):
        # If no event was detected return zeros to avoid division by zero
        return 0.0, 0.0, 0.0

    td12 = (n1 - n2) / fs
    td13 = (n1 - n3) / fs
    td14 = (n1 - n4) / fs
    return td12, td13, td14
