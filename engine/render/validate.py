"""Audio validation and QC metrics."""
from typing import List, Tuple
import math


def compute_peak(l: List[float], r: List[float]) -> float:
    """Compute peak amplitude."""
    peak = 0.0
    for x in l:
        peak = max(peak, abs(x))
    for x in r:
        peak = max(peak, abs(x))
    return peak


def compute_rms(l: List[float], r: List[float]) -> float:
    """Compute RMS level."""
    sum_sq = 0.0
    n = len(l)
    for i in range(n):
        sum_sq += l[i] * l[i] + r[i] * r[i]
    return math.sqrt(sum_sq / (2 * n))


def compute_dc_offset(l: List[float], r: List[float]) -> Tuple[float, float]:
    """Compute DC offset for each channel."""
    dc_l = sum(l) / len(l)
    dc_r = sum(r) / len(r)
    return dc_l, dc_r


def compute_silence_ratio(l: List[float], r: List[float], threshold: float = 1e-4) -> float:
    """Estimate ratio of near-silent stereo frames."""
    n = len(l)
    if n == 0:
        return 1.0
    silent = 0
    for i in range(n):
        if abs(l[i]) < threshold and abs(r[i]) < threshold:
            silent += 1
    return silent / float(n)


def compute_clipped_ratio(l: List[float], r: List[float], threshold: float = 0.999) -> float:
    """Estimate ratio of clipped/near-clipped stereo samples across both channels."""
    n = len(l)
    if n == 0:
        return 0.0
    clipped = 0
    total = 2 * n
    for i in range(n):
        if abs(l[i]) >= threshold:
            clipped += 1
        if abs(r[i]) >= threshold:
            clipped += 1
    return clipped / float(total)


def qc_report(l: List[float], r: List[float], sr: int) -> dict:
    """Generate QC metrics report."""
    peak = compute_peak(l, r)
    rms = compute_rms(l, r)
    dc_l, dc_r = compute_dc_offset(l, r)
    silence_ratio = compute_silence_ratio(l, r)
    clipped_ratio = compute_clipped_ratio(l, r)
    crest = peak / rms if rms > 0 else 0
    duration = len(l) / sr
    
    return {
        "peak": peak,
        "rms": rms,
        "crest_factor": crest,
        "dc_offset_l": dc_l,
        "dc_offset_r": dc_r,
        "silence_ratio": silence_ratio,
        "clipped_ratio": clipped_ratio,
        "duration_s": duration,
        "sample_rate": sr,
        "samples": len(l)
    }


SPECTRAL_THRESHOLDS_DEFAULT = {
    "low_to_mid_max": 6.0,
    "high_to_mid_max": 3.0,
}

SPECTRAL_THRESHOLDS_BY_FAMILY = {
    "ARC": {"low_to_mid_max": 7.0},
    "BODY": {"low_to_mid_max": 6.5},
    "SLEEP": {"low_to_mid_max": 6.0, "high_to_mid_max": 2.5},
    "SUN": {"low_to_mid_max": 6.0, "high_to_mid_max": 2.5},
    "ATTN": {"low_to_mid_max": 5.0},
    "SENSE": {"low_to_mid_max": 6.5},
    "CREA": {"low_to_mid_max": 5.5},
    "FLOW": {"low_to_mid_max": 5.5},
    "META": {"low_to_mid_max": 6.0},
    "PAIN": {"low_to_mid_max": 6.0},
}


def one_pole_lowpass(x: List[float], sr: int, cutoff_hz: float) -> List[float]:
    if not x:
        return x
    dt = 1.0 / float(sr)
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    alpha = dt / (rc + dt)
    out = [0.0] * len(x)
    y = x[0]
    for i, cur in enumerate(x):
        y = y + alpha * (cur - y)
        out[i] = y
    return out


def phase_spectral_balance(l: List[float], r: List[float], sr: int, phases: List[dict]) -> List[dict]:
    out = []
    n = len(l)
    for idx, ph in enumerate(phases, start=1):
        start = max(0, min(n, int(float(ph.get("start_s", 0.0)) * sr)))
        end = max(start, min(n, int(float(ph.get("end_s", 0.0)) * sr)))
        if end <= start:
            continue
        mono = [0.5 * (l[i] + r[i]) for i in range(start, end)]
        low_lp = one_pole_lowpass(mono, sr, 180.0)
        upper_lp = one_pole_lowpass(mono, sr, 2500.0)
        low = low_lp
        mid = [upper_lp[i] - low_lp[i] for i in range(len(mono))]
        high = [mono[i] - upper_lp[i] for i in range(len(mono))]

        def rms(sig):
            if not sig:
                return 0.0
            return math.sqrt(sum(x * x for x in sig) / float(len(sig)))

        low_r = rms(low)
        mid_r = rms(mid)
        high_r = rms(high)
        out.append({
            "phase_index": idx,
            "phase_name": ph.get("name", f"Phase {idx}"),
            "low_rms": low_r,
            "mid_rms": mid_r,
            "high_rms": high_r,
            "low_to_mid": (low_r / (mid_r + 1e-9)),
            "high_to_mid": (high_r / (mid_r + 1e-9)),
        })
    return out


def get_spectral_thresholds(family: str) -> dict:
    t = dict(SPECTRAL_THRESHOLDS_DEFAULT)
    t.update(SPECTRAL_THRESHOLDS_BY_FAMILY.get(family or "", {}))
    return t


def spectral_balance_failures(phase_stats: List[dict], family: str) -> List[str]:
    t = get_spectral_thresholds(family)
    failed = []
    for ph in phase_stats:
        pi = ph["phase_index"]
        if ph["low_to_mid"] > t["low_to_mid_max"]:
            failed.append(f"spectral_p{pi}_low")
        if ph["high_to_mid"] > t["high_to_mid_max"]:
            failed.append(f"spectral_p{pi}_high")
    return failed
