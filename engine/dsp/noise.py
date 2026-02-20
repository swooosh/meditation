"""Noise generators for protocol audio beds."""
import random
from typing import List


def voss_pink_noise(num_samples: int, num_rows: int = 16) -> List[float]:
    """Voss-McCartney algorithm for pink noise generation."""
    rows = [0.0] * num_rows
    running_sum = 0.0
    for i in range(num_rows):
        rows[i] = random.uniform(-1.0, 1.0)
        running_sum += rows[i]
    out = []
    counter = 0
    for _ in range(num_samples):
        counter += 1
        n = counter
        row_to_update = 0
        while (n & 1) == 0 and row_to_update < num_rows:
            n >>= 1
            row_to_update += 1
        if row_to_update >= num_rows:
            row_to_update = num_rows - 1
        running_sum -= rows[row_to_update]
        rows[row_to_update] = random.uniform(-1.0, 1.0)
        running_sum += rows[row_to_update]
        white = random.uniform(-1.0, 1.0)
        sample = (running_sum + white) / (num_rows + 1)
        out.append(sample)
    return out


def brown_noise(num_samples: int) -> List[float]:
    """Brown/red noise via simple integration."""
    out = []
    x = 0.0
    for _ in range(num_samples):
        x = 0.987 * x + 0.013 * random.uniform(-1.0, 1.0)
        out.append(x)
    return out


def noise_burst(n: int) -> List[float]:
    """White noise burst."""
    return [random.uniform(-1.0, 1.0) for _ in range(n)]


def one_pole_lowpass(src: List[float], a: float) -> List[float]:
    """Simple one-pole lowpass filter."""
    out = [0.0] * len(src)
    y = 0.0
    for i, x in enumerate(src):
        y = a * y + (1.0 - a) * x
        out[i] = y
    return out


def highpass_from_lowpass(src: List[float], a: float) -> List[float]:
    """Highpass via subtraction: hp = x - lp(x)."""
    lp = one_pole_lowpass(src, a=a)
    return [src[i] - lp[i] for i in range(len(src))]
