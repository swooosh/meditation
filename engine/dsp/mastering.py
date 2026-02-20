"""Lightweight mastering utilities for protocol renders."""
import math
from typing import Dict, List, Tuple

from engine.dsp.limiter import soft_clip


MASTER_PROFILE_DEFAULT = {
    "target_lufs": -18.0,
    "dc_remove": True,
    "hp_hz": 24.0,
    "low_gain_db": 0.0,
    "high_gain_db": 0.0,
    "drive": 1.08,
    "ceiling": 0.985,
    "low_env_threshold": 0.11,
    "low_env_ratio": 2.0,
    "low_sidechain": 0.25,
}

MASTER_PROFILE_BY_FAMILY = {
    "ATTN": {"target_lufs": -18.5, "high_gain_db": 0.4, "drive": 1.06},
    "ARC": {"target_lufs": -15.0, "low_gain_db": 0.6, "drive": 1.14, "low_env_threshold": 0.09, "low_env_ratio": 3.2},
    "PERF": {"target_lufs": -17.0, "high_gain_db": 0.6, "drive": 1.10},
    "RECON": {"target_lufs": -18.0, "low_gain_db": 0.3, "drive": 1.09},
    "SLEEP": {"target_lufs": -21.0, "high_gain_db": -0.8, "drive": 1.05, "low_env_threshold": 0.08, "low_env_ratio": 2.5, "low_sidechain": 0.4},
    "CREA": {"target_lufs": -18.0, "high_gain_db": 0.8, "drive": 1.08},
    "SENSE": {"target_lufs": -17.5, "high_gain_db": 1.0, "drive": 1.08},
    "META": {"target_lufs": -19.5, "high_gain_db": -0.3, "drive": 1.06},
    "FLOW": {"target_lufs": -17.0, "high_gain_db": 0.4, "drive": 1.10},
    "BODY": {"target_lufs": -16.0, "low_gain_db": 0.8, "drive": 1.12, "low_env_threshold": 0.09, "low_env_ratio": 3.0},
    "SOC": {"target_lufs": -18.0, "high_gain_db": 0.2, "drive": 1.08},
    "PAIN": {"target_lufs": -18.5, "high_gain_db": -0.2, "drive": 1.07},
    "SUN": {"target_lufs": -20.0, "high_gain_db": -0.6, "drive": 1.05},
    "FSP": {"target_lufs": -18.5, "high_gain_db": 0.2, "drive": 1.07},
}


def get_master_profile(family: str) -> Dict[str, float]:
    p = dict(MASTER_PROFILE_DEFAULT)
    p.update(MASTER_PROFILE_BY_FAMILY.get(family or "", {}))
    return p


def db_to_lin(db: float) -> float:
    return math.pow(10.0, db / 20.0)


def estimate_lufs_stereo(l: List[float], r: List[float]) -> float:
    """Very rough integrated loudness estimate from channel energy."""
    n = len(l)
    if n == 0:
        return -70.0
    energy = 0.0
    for i in range(n):
        energy += l[i] * l[i] + r[i] * r[i]
    mean_sq = energy / float(2 * n)
    if mean_sq <= 1e-12:
        return -70.0
    # Approximate LUFS transform from mean-square power.
    return -0.691 + 10.0 * math.log10(mean_sq)


def remove_dc(l: List[float], r: List[float]) -> Tuple[List[float], List[float]]:
    if not l:
        return l, r
    dc_l = sum(l) / len(l)
    dc_r = sum(r) / len(r)
    return [x - dc_l for x in l], [x - dc_r for x in r]


def one_pole_highpass(x: List[float], sr: int, cutoff_hz: float) -> List[float]:
    if not x or cutoff_hz <= 0:
        return x
    dt = 1.0 / float(sr)
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    alpha = rc / (rc + dt)
    out = [0.0] * len(x)
    y_prev = 0.0
    x_prev = x[0]
    for i, cur in enumerate(x):
        y = alpha * (y_prev + cur - x_prev)
        out[i] = y
        y_prev = y
        x_prev = cur
    return out


def split_tilt(x: List[float], sr: int, crossover_hz: float = 240.0) -> Tuple[List[float], List[float]]:
    if not x:
        return [], []
    dt = 1.0 / float(sr)
    rc = 1.0 / (2.0 * math.pi * crossover_hz)
    alpha = dt / (rc + dt)
    low = [0.0] * len(x)
    prev = x[0]
    for i, cur in enumerate(x):
        prev = prev + alpha * (cur - prev)
        low[i] = prev
    high = [x[i] - low[i] for i in range(len(x))]
    return low, high


def lin_interp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def phase_scene_targets(phase_name: str, phase_intent: str, family: str):
    name = f"{phase_name or ''} {phase_intent or ''}".lower()
    width = 1.0
    high_db = 0.0
    low_db = 0.0

    if any(k in name for k in ("ground", "settle", "downshift", "seal", "sleep", "drift", "delta", "reintegrat")):
        width = 0.88
        high_db = -0.7
        low_db = 0.1
    elif any(k in name for k in ("sharpen", "activate", "peak", "explore", "distribute", "rise", "immersion")):
        width = 1.10
        high_db = 0.6
        low_db = -0.1
    elif any(k in name for k in ("integrate", "resolution", "return", "descent")):
        width = 0.95
        high_db = -0.2
        low_db = 0.0

    if family in ("SLEEP", "SUN", "META"):
        width *= 0.95
        high_db -= 0.2
    if family in ("ARC", "BODY"):
        low_db += 0.2

    return width, low_db, high_db


def smooth_curve(curve: List[float], sr: int, tau_s: float = 1.2) -> List[float]:
    if not curve:
        return curve
    dt = 1.0 / float(sr)
    alpha = dt / (max(1e-4, tau_s) + dt)
    out = [curve[0]] * len(curve)
    for i in range(1, len(curve)):
        out[i] = out[i - 1] + alpha * (curve[i] - out[i - 1])
    return out


def build_scene_curves(n: int, sr: int, phases: List[dict], family: str):
    if not phases:
        return [1.0] * n, [0.0] * n, [0.0] * n

    width = [1.0] * n
    low_db = [0.0] * n
    high_db = [0.0] * n

    for ph in phases:
        start = max(0, min(n, int(float(ph.get("start_s", 0.0)) * sr)))
        end = max(start, min(n, int(float(ph.get("end_s", 0.0)) * sr)))
        w, ldb, hdb = phase_scene_targets(ph.get("name", ""), ph.get("intent", ""), family)
        for i in range(start, end):
            width[i] = w
            low_db[i] = ldb
            high_db[i] = hdb

    return smooth_curve(width, sr), smooth_curve(low_db, sr), smooth_curve(high_db, sr)


def apply_tilt(x: List[float], sr: int, low_gain_db: float, high_gain_db: float) -> List[float]:
    if not x or (abs(low_gain_db) < 1e-6 and abs(high_gain_db) < 1e-6):
        return x
    low, high = split_tilt(x, sr)
    gl = db_to_lin(low_gain_db)
    gh = db_to_lin(high_gain_db)
    return [low[i] * gl + high[i] * gh for i in range(len(x))]


def apply_tilt_curve(x: List[float], sr: int, low_db_curve: List[float], high_db_curve: List[float]) -> List[float]:
    if not x:
        return x
    low, high = split_tilt(x, sr)
    out = [0.0] * len(x)
    for i in range(len(x)):
        out[i] = low[i] * db_to_lin(low_db_curve[i]) + high[i] * db_to_lin(high_db_curve[i])
    return out


def apply_width_curve(l: List[float], r: List[float], width_curve: List[float]) -> Tuple[List[float], List[float]]:
    n = len(l)
    out_l = [0.0] * n
    out_r = [0.0] * n
    for i in range(n):
        mid = 0.5 * (l[i] + r[i])
        side = 0.5 * (l[i] - r[i]) * width_curve[i]
        out_l[i] = mid + side
        out_r[i] = mid - side
    return out_l, out_r


def apply_low_end_management(l: List[float], r: List[float], sr: int, profile: Dict[str, float]) -> Tuple[List[float], List[float]]:
    if not l:
        return l, r

    low_l, high_l = split_tilt(l, sr, crossover_hz=140.0)
    low_r, high_r = split_tilt(r, sr, crossover_hz=140.0)

    th = float(profile.get("low_env_threshold", 0.11))
    ratio = float(profile.get("low_env_ratio", 2.0))
    sidechain = float(profile.get("low_sidechain", 0.25))

    env_low = 0.0
    env_high = 0.0
    attack = 0.03
    release = 0.002

    out_l = [0.0] * len(l)
    out_r = [0.0] * len(r)
    for i in range(len(l)):
        low_abs = abs(0.5 * (low_l[i] + low_r[i]))
        high_abs = abs(0.5 * (high_l[i] + high_r[i]))
        env_low += (low_abs - env_low) * (attack if low_abs > env_low else release)
        env_high += (high_abs - env_high) * (attack if high_abs > env_high else release)

        over = max(0.0, env_low - th)
        comp = 1.0 / (1.0 + over * ratio * 4.0)
        sc = 1.0 / (1.0 + env_high * sidechain * 2.0)
        g = max(0.55, min(1.0, comp * sc))

        out_l[i] = low_l[i] * g + high_l[i]
        out_r[i] = low_r[i] * g + high_r[i]

    return out_l, out_r


def apply_gain(l: List[float], r: List[float], gain_lin: float) -> Tuple[List[float], List[float]]:
    if abs(gain_lin - 1.0) < 1e-9:
        return l, r
    return [x * gain_lin for x in l], [x * gain_lin for x in r]


def apply_soft_ceiling(l: List[float], r: List[float], drive: float, ceiling: float) -> Tuple[List[float], List[float]]:
    if not l:
        return l, r
    cl = [soft_clip(x, max(1.0, drive)) for x in l]
    cr = [soft_clip(x, max(1.0, drive)) for x in r]
    peak = 1e-9
    for x in cl:
        peak = max(peak, abs(x))
    for x in cr:
        peak = max(peak, abs(x))
    scale = min(1.0, ceiling / peak)
    return [x * scale for x in cl], [x * scale for x in cr]


def master_stereo(l: List[float], r: List[float], sr: int, profile: Dict[str, float], phases=None, family: str = ""):
    """Apply lightweight mastering and return (l, r, meta)."""
    pre_lufs = estimate_lufs_stereo(l, r)

    out_l, out_r = l, r
    if profile.get("dc_remove", True):
        out_l, out_r = remove_dc(out_l, out_r)

    hp_hz = float(profile.get("hp_hz", 24.0))
    out_l = one_pole_highpass(out_l, sr, hp_hz)
    out_r = one_pole_highpass(out_r, sr, hp_hz)

    width_curve, low_curve, high_curve = build_scene_curves(len(out_l), sr, phases or [], family or "")
    base_low = float(profile.get("low_gain_db", 0.0))
    base_high = float(profile.get("high_gain_db", 0.0))
    low_curve = [x + base_low for x in low_curve]
    high_curve = [x + base_high for x in high_curve]

    out_l = apply_tilt_curve(out_l, sr, low_curve, high_curve)
    out_r = apply_tilt_curve(out_r, sr, low_curve, high_curve)
    out_l, out_r = apply_width_curve(out_l, out_r, width_curve)
    out_l, out_r = apply_low_end_management(out_l, out_r, sr, profile)

    mid_lufs = estimate_lufs_stereo(out_l, out_r)
    target_lufs = float(profile.get("target_lufs", -18.0))
    gain_db = max(-12.0, min(12.0, target_lufs - mid_lufs))
    out_l, out_r = apply_gain(out_l, out_r, db_to_lin(gain_db))

    out_l, out_r = apply_soft_ceiling(
        out_l,
        out_r,
        float(profile.get("drive", 1.08)),
        float(profile.get("ceiling", 0.985)),
    )
    post_lufs = estimate_lufs_stereo(out_l, out_r)
    return out_l, out_r, {
        "target_lufs": target_lufs,
        "pre_lufs": pre_lufs,
        "mid_lufs": mid_lufs,
        "post_lufs": post_lufs,
        "gain_db_applied": gain_db,
        "scene_width_range": [min(width_curve) if width_curve else 1.0, max(width_curve) if width_curve else 1.0],
        "scene_high_db_range": [min(high_curve) if high_curve else 0.0, max(high_curve) if high_curve else 0.0],
        "profile": profile,
    }
