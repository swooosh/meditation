"""Tribal drum synthesis for ARC protocols."""
import math
import random
from typing import List
from .noise import noise_burst, one_pole_lowpass, highpass_from_lowpass
from .envelopes import exp_env, smoothstep


def synth_frame_drum_skin(sr: int, dur_s: float, f0: float) -> List[float]:
    """Skin-forward frame drum with reduced tonal body."""
    n = max(1, int(dur_s * sr))
    env = exp_env(n, sr, attack_s=0.0015, decay_s=dur_s * 0.55)
    
    body = [0.0] * n
    phase = 0.0
    for i in range(n):
        t = i / sr
        f = f0 * (0.86 ** (t / max(1e-6, dur_s * 0.35)))
        phase += 2.0 * math.pi * f / sr
        body[i] = math.sin(phase)
    
    w = noise_burst(n)
    skin_lp = one_pole_lowpass(w, a=0.90)
    skin_hp = highpass_from_lowpass(w, a=0.95)
    
    out = [0.0] * n
    for i in range(n):
        v = 0.55 * skin_lp[i] + 0.45 * skin_hp[i] + 0.45 * body[i]
        out[i] = env[i] * v
    return [0.85 * x for x in out]


def synth_low_tom_skin(sr: int, dur_s: float, f0: float) -> List[float]:
    """Low tom with skin-forward character."""
    n = max(1, int(dur_s * sr))
    env = exp_env(n, sr, attack_s=0.0025, decay_s=dur_s * 0.70)
    
    w = noise_burst(n)
    skin_lp = one_pole_lowpass(w, a=0.87)
    skin_hp = highpass_from_lowpass(w, a=0.93)
    
    phase = 0.0
    out = [0.0] * n
    for i in range(n):
        t = i / sr
        f = f0 * (0.90 ** (t / max(1e-6, dur_s * 0.50)))
        phase += 2.0 * math.pi * f / sr
        body = math.sin(phase)
        v = 0.62 * skin_lp[i] + 0.30 * skin_hp[i] + 0.38 * body
        out[i] = env[i] * v
    return [0.78 * x for x in out]


def synth_wood_tick(sr: int, dur_s: float = 0.028) -> List[float]:
    """Bright wood tick accent."""
    n = max(1, int(dur_s * sr))
    env = exp_env(n, sr, attack_s=0.001, decay_s=0.018)
    w = noise_burst(n)
    hp = highpass_from_lowpass(w, a=0.85)
    return [0.55 * env[i] * hp[i] for i in range(n)]


def synth_shaker(sr: int, dur_s: float = 0.060) -> List[float]:
    """High-frequency shaker."""
    n = max(1, int(dur_s * sr))
    env = exp_env(n, sr, attack_s=0.001, decay_s=0.040)
    w = noise_burst(n)
    hp = highpass_from_lowpass(w, a=0.92)
    return [0.35 * env[i] * hp[i] for i in range(n)]
