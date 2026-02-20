"""Core rendering utilities."""
import math
import os
import struct
import wave
from typing import List, Tuple


def pan_gains(pan: float) -> Tuple[float, float]:
    """Equal-power panning. pan -1..+1"""
    pan = max(-1.0, min(1.0, pan))
    theta = (pan + 1.0) * (math.pi / 4.0)
    return math.cos(theta), math.sin(theta)


def normalize_stereo(l: List[float], r: List[float], peak: float = 0.98) -> Tuple[List[float], List[float]]:
    """Peak normalize stereo buffer."""
    m = 1e-9
    for x in l:
        m = max(m, abs(x))
    for x in r:
        m = max(m, abs(x))
    scale = peak / m
    return [x * scale for x in l], [x * scale for x in r]


def write_wav_stereo(path: str, left: List[float], right: List[float], sr: int):
    """Write stereo WAV file."""
    assert len(left) == len(right)
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for i in range(len(left)):
            li = int(max(-1.0, min(1.0, left[i])) * 32767.0)
            ri = int(max(-1.0, min(1.0, right[i])) * 32767.0)
            wf.writeframes(struct.pack("<hh", li, ri))


def mix_in(dst: List[float], start: int, src: List[float], gain: float = 1.0):
    """Mix source into destination buffer."""
    end = min(len(dst), start + len(src))
    for i in range(start, end):
        dst[i] += gain * src[i - start]


def mix_mono_into_stereo(l: List[float], r: List[float], start_idx: int, 
                         mono: List[float], gain: float, pan: float):
    """Mix mono source into stereo with panning."""
    gl, gr = pan_gains(pan)
    n = len(l)
    for i, s in enumerate(mono):
        j = start_idx + i
        if j >= n:
            break
        v = gain * s
        l[j] += gl * v
        r[j] += gr * v
