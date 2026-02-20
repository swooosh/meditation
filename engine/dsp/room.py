"""Room illusion and spatial effects."""
from typing import List
from .noise import noise_burst, one_pole_lowpass


def add_room_early_reflections(l: List[float], r: List[float], sr: int, 
                               room_ms: float, level: float):
    """Add subtle early reflections for spatial width."""
    n = len(l)
    d = max(1, int((room_ms / 1000.0) * sr))
    
    taps_ms = [room_ms, room_ms * 1.8, room_ms * 2.6]
    gains = [level, level * 0.55, level * 0.35]
    
    for tap_ms, g in zip(taps_ms, gains):
        dd = max(1, int((tap_ms / 1000.0) * sr))
        for i in range(n - dd):
            l[i + dd] += g * r[i]
            r[i + dd] += g * l[i]


def add_ambience_bed(l: List[float], r: List[float], sr: int, level: float):
    """Add subtle filtered noise bed for air/space."""
    n = len(l)
    wL = noise_burst(n)
    wR = noise_burst(n)
    wL = one_pole_lowpass(wL, a=0.985)
    wR = one_pole_lowpass(wR, a=0.985)
    for i in range(n):
        l[i] += level * wL[i]
        r[i] += level * wR[i]
