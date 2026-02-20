"""Binaural beat generation."""
import math
from typing import List, Tuple
from .envelopes import clamp, smoothstep


def add_binaural_constant(l: List[float], r: List[float], sr: int,
                          beat_hz: float, carrier_hz: float, level: float, ramp_s: float):
    """Add constant binaural beat to stereo buffer."""
    n = len(l)
    ramp_n = max(1, int(ramp_s * sr))
    f_l = max(1.0, carrier_hz - beat_hz / 2.0)
    f_r = max(1.0, carrier_hz + beat_hz / 2.0)
    for i in range(n):
        t = i / sr
        s_l = math.sin(2.0 * math.pi * f_l * t)
        s_r = math.sin(2.0 * math.pi * f_r * t)
        g = 1.0
        if i < ramp_n:
            g = smoothstep(i / ramp_n)
        elif i > n - ramp_n:
            g = smoothstep((n - i) / ramp_n)
        l[i] += g * level * s_l
        r[i] += g * level * s_r


def add_binaural_ramp(l: List[float], r: List[float], sr: int,
                      beat_start: float, beat_end: float, ramp_seconds: float,
                      carrier_hz: float, level: float, ramp_s: float):
    """Add ramping binaural beat to stereo buffer."""
    n = len(l)
    ramp_n = max(1, int(ramp_s * sr))
    desc_n = max(1, int(ramp_seconds * sr))
    for i in range(n):
        if i < desc_n:
            x = smoothstep(i / desc_n)
            bb = beat_start + (beat_end - beat_start) * x
        else:
            bb = beat_end
        f_l = max(1.0, carrier_hz - bb / 2.0)
        f_r = max(1.0, carrier_hz + bb / 2.0)
        t = i / sr
        s_l = math.sin(2.0 * math.pi * f_l * t)
        s_r = math.sin(2.0 * math.pi * f_r * t)
        g = 1.0
        if i < ramp_n:
            g = smoothstep(i / ramp_n)
        elif i > n - ramp_n:
            g = smoothstep((n - i) / ramp_n)
        l[i] += g * level * s_l
        r[i] += g * level * s_r
