"""Envelope generators and utilities."""
import math
from typing import List


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp value between lo and hi."""
    return lo if x < lo else hi if x > hi else x


def smoothstep(x: float) -> float:
    """Smooth interpolation curve."""
    x = clamp(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def swell_env(n: int, sr: int, attack: float, hold: float, release: float) -> List[float]:
    """Attack-hold-release envelope with smoothstep curves."""
    a = max(1, int(attack * sr))
    h = max(0, int(hold * sr))
    r = max(1, int(release * sr))
    env = [0.0] * n
    for i in range(n):
        if i < a:
            env[i] = smoothstep(i / a)
        elif i < a + h:
            env[i] = 1.0
        else:
            x = (i - (a + h)) / r
            env[i] = 1.0 - smoothstep(x)
    return env[:n]


def exp_env(n: int, sr: int, attack_s: float, decay_s: float) -> List[float]:
    """Exponential attack-decay envelope."""
    out = [0.0] * n
    a = max(1, int(attack_s * sr))
    for i in range(n):
        if i < a:
            out[i] = smoothstep(i / a)
        else:
            t = (i - a) / sr
            out[i] = math.exp(-t / max(1e-6, decay_s))
    return out


def fade_in_out(buf: List[float], sr: int, fade_s: float):
    """Apply fade in/out to buffer in-place."""
    n = len(buf)
    fn = max(1, int(fade_s * sr))
    for i in range(min(fn, n)):
        buf[i] *= smoothstep(i / fn)
    for i in range(max(0, n - fn), n):
        buf[i] *= smoothstep((n - i) / fn)
