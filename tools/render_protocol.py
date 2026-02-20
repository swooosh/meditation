#!/usr/bin/env python3
"""Universal protocol renderer."""
import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
import yaml

# Add protocol-lab root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.dsp.noise import voss_pink_noise, brown_noise
from engine.dsp.envelopes import smoothstep, fade_in_out, swell_env
from engine.dsp.binaural import add_binaural_constant, add_binaural_ramp
from engine.dsp.mastering import get_master_profile, master_stereo
from engine.render.render_core import pan_gains, normalize_stereo, write_wav_stereo, mix_in
from engine.render.validate import qc_report, phase_spectral_balance, spectral_balance_failures, get_spectral_thresholds

SUPPORTED_LAYER_TYPES = {
    "noise_bed",
    "binaural",
    "pulse_cues",
    "irregular_pulses",
    "harmonic_pad",
    "spatial_sweep",
    "switch_cues",
    "gamma_overlay",
    "tribal_drums",
    "sub",
    "room_illusion",
    "body_cues",
    "sub_power",
    "steady_groove",
    "breath_cues",
    "return_cues",
    "letgo_swells",
    "house_beat",
    "location_tones",
    "resolution_cues",
    "shimmer",
    "sub_pulse",
    "heartbeat_cues",
    "dissolve_cues",
    "reality_check_cues",
    "dyadic_cues",
}

QC_THRESHOLDS_DEFAULT = {
    "peak_max": 0.995,
    "rms_min": 0.0015,
    "rms_max": 0.30,
    "crest_min": 1.1,
    "crest_max": 40.0,
    "dc_abs_max": 0.02,
    "silence_ratio_max": 0.985,
    "clipped_ratio_max": 0.001,
}

QC_THRESHOLDS_BY_FAMILY = {
    # Breathwork and high-drive families tolerate denser energy.
    "ARC": {"rms_max": 0.55},
    "BODY": {"rms_max": 0.60},
    # Processing and modulation families often run hotter than neutral defaults.
    "RECON": {"rms_max": 0.45},
    "META": {"rms_max": 0.50},
    "PAIN": {"rms_max": 0.50},
    "SENSE": {"rms_max": 0.42},
    "SLEEP": {"rms_max": 0.50},
    # Attention training can include sparse transients with higher crest.
    "ATTN": {"crest_max": 50.0},
}


def get_qc_thresholds(family):
    out = dict(QC_THRESHOLDS_DEFAULT)
    if family in QC_THRESHOLDS_BY_FAMILY:
        out.update(QC_THRESHOLDS_BY_FAMILY[family])
    return out


def evaluate_qc(metrics, expected_duration_s, family=None):
    """Apply simple QC gates and return (passed, failed_checks)."""
    thresholds = get_qc_thresholds(family)
    failed = []
    if metrics["peak"] > thresholds["peak_max"]:
        failed.append("peak")
    if metrics["rms"] < thresholds["rms_min"] or metrics["rms"] > thresholds["rms_max"]:
        failed.append("rms")
    if metrics["crest_factor"] < thresholds["crest_min"] or metrics["crest_factor"] > thresholds["crest_max"]:
        failed.append("crest_factor")
    if abs(metrics["dc_offset_l"]) > thresholds["dc_abs_max"] or abs(metrics["dc_offset_r"]) > thresholds["dc_abs_max"]:
        failed.append("dc_offset")
    if metrics.get("silence_ratio", 1.0) > thresholds["silence_ratio_max"]:
        failed.append("silence_ratio")
    if metrics.get("clipped_ratio", 0.0) > thresholds["clipped_ratio_max"]:
        failed.append("clipped_ratio")
    if metrics["duration_s"] < float(expected_duration_s) * 0.99:
        failed.append("duration")
    return len(failed) == 0, failed, thresholds


def write_qc_artifact(spec, out_wav_path, metrics, qc_passed, failed_checks, mastering_meta=None):
    """Write QC JSON sidecar for downstream status/UI."""
    out_wav = Path(out_wav_path)
    qc_dir = out_wav.parent / "qc"
    qc_dir.mkdir(parents=True, exist_ok=True)
    qc_path = qc_dir / f"{spec['id']}_qc.json"
    thresholds = get_qc_thresholds(spec.get("family"))
    payload = {
        "id": spec["id"],
        "family": spec.get("family"),
        "render_path": str(out_wav),
        "expected_duration_s": float(spec["duration_s"]),
        "qc_passed": qc_passed,
        "failed_checks": failed_checks,
        "thresholds": thresholds,
        "metrics": metrics,
    }
    if mastering_meta is not None:
        payload["mastering"] = mastering_meta
    qc_path.write_text(json.dumps(payload, indent=2) + "\n")
    return qc_path


def validate_audio_layers(spec):
    """Fail fast when a spec declares layer types the renderer cannot process."""
    unknown = []
    for layer in spec.get("audio_layers", []):
        layer_type = layer.get("type")
        if layer_type and layer_type not in SUPPORTED_LAYER_TYPES:
            unknown.append(layer_type)
    if unknown:
        unique_unknown = sorted(set(unknown))
        supported = ", ".join(sorted(SUPPORTED_LAYER_TYPES))
        raise ValueError(
            f"{spec.get('id', 'UNKNOWN')} has unsupported audio layer types: "
            f"{', '.join(unique_unknown)}. Supported types: {supported}"
        )


def build_noise_bed(sr, total_s, noise, level, drift_hz, drift_depth, high_shelf=0.0):
    n = int(total_s * sr)
    base_l = voss_pink_noise(n) if noise == "pink" else brown_noise(n)
    base_r = voss_pink_noise(n) if noise == "pink" else brown_noise(n)
    
    l, r = [0.0] * n, [0.0] * n
    for i in range(n):
        t = i / sr
        pan = drift_depth * math.sin(2.0 * math.pi * drift_hz * t)
        gl, gr = pan_gains(pan)
        
        nl, nr = base_l[i], base_r[i]
        if high_shelf > 0:
            nl = nl * (1.0 + high_shelf * (i / n))
            nr = nr * (1.0 + high_shelf * (i / n))
        
        mid = 0.5 * (nl + nr)
        side = 0.5 * (nl - nr)
        l[i] = level * (mid + gl * side)
        r[i] = level * (mid - gr * side)
    
    fade_in_out(l, sr, 2.0)
    fade_in_out(r, sr, 2.0)
    return l, r


def add_pulse_cues(l, r, sr, start_s, end_s, rate_s, level, freq_hz):
    t = start_s
    while t < end_s:
        cue = [level * math.sin(2 * math.pi * freq_hz * i / sr) * 
               math.exp(-i / (sr * 0.08)) for i in range(int(0.12 * sr))]
        idx = int(t * sr)
        mix_in(l, idx, cue, 1.0)
        mix_in(r, idx, cue, 1.0)
        t += rate_s


def add_irregular_pulses(l, r, sr, start_s, end_s, base_rate_s, jitter, level):
    t = start_s
    while t < end_s:
        actual_rate = base_rate_s * (1.0 + random.uniform(-jitter, jitter))
        cue = [level * random.uniform(-1, 1) * math.exp(-i / (sr * 0.05)) 
               for i in range(int(0.08 * sr))]
        idx = int(t * sr)
        mix_in(l, idx, cue, 1.0)
        mix_in(r, idx, cue, 1.0)
        t += actual_rate


def add_harmonic_pad(l, r, sr, start_s, end_s, base_freq, level, swell_rate_s):
    t = start_s
    while t < end_s:
        dur = min(swell_rate_s * 0.8, end_s - t)
        n = int(dur * sr)
        env = swell_env(n, sr, dur * 0.3, dur * 0.1, dur * 0.6)
        pad = [0.0] * n
        for i in range(n):
            s = math.sin(2 * math.pi * base_freq * i / sr)
            s += 0.5 * math.sin(2 * math.pi * base_freq * 1.5 * i / sr)
            pad[i] = level * env[i] * s
        idx = int(t * sr)
        mix_in(l, idx, pad, 1.0)
        mix_in(r, idx, pad, 1.0)
        t += swell_rate_s


def add_signature(l, r, sr, start_s, freqs_hz, duration_ms, level):
    """Add three-tone signature at specified time."""
    tone_samples = int(duration_ms * sr / 1000)
    start_idx = int(start_s * sr)
    
    for freq in freqs_hz:
        for i in range(tone_samples):
            if start_idx + i < len(l):
                t = i / sr
                # Exponential decay envelope
                env = math.exp(-t / (duration_ms / 1000 * 0.3))
                val = level * math.sin(2 * math.pi * freq * t) * env
                l[start_idx + i] += val
                r[start_idx + i] += val
        start_idx += tone_samples


def cue_tone(sr, freq_hz, level, dur_s=0.12):
    n = max(1, int(dur_s * sr))
    out = [0.0] * n
    for i in range(n):
        t = i / sr
        env = math.exp(-t / max(0.001, dur_s * 0.35))
        out[i] = level * env * math.sin(2 * math.pi * freq_hz * t)
    return out


def synth_chime(sr, dur_s, freq_hz, harmonic2=0.25):
    """Soft percussive chime: fast attack, exponential decay."""
    n = max(1, int(dur_s * sr))
    out = [0.0] * n
    attack_n = max(1, int(0.004 * sr))
    tau = max(0.02, dur_s * 0.38)
    for i in range(n):
        t = i / sr
        env = min(1.0, i / attack_n) * math.exp(-t / tau)
        s = math.sin(2.0 * math.pi * freq_hz * t)
        s += harmonic2 * math.sin(2.0 * math.pi * (freq_hz * 2.0) * t)
        out[i] = env * s
    return out


def breath_pattern_seconds(preset):
    """Return inhale/exhale seconds for known breath presets."""
    p = (preset or "4-6").strip().lower()
    if p == "4-6":
        return 4.0, 6.0
    if p == "4-7":
        return 4.0, 7.0
    if p == "6-6":
        return 6.0, 6.0
    if p == "6-8":
        return 6.0, 8.0
    if p == "8-8":
        return 8.0, 8.0
    if p == "10-10":
        return 10.0, 10.0
    if p == "box":
        # Box breathing with silent holds simplified to 4 in / 4 out cues.
        return 4.0, 4.0
    if p == "none":
        return None, None
    return 4.0, 6.0


def add_breath_cues(l, r, sr, start_s, end_s, preset, level, tone_hz, pan_mag):
    """Overlay inhale/exhale cue chimes based on breath-cycle timing."""
    inh_s, exh_s = breath_pattern_seconds(preset)
    if inh_s is None or exh_s is None or level <= 0:
        return

    # Inhale: brighter/higher. Exhale: darker/lower and slightly longer.
    inhale = synth_chime(sr, dur_s=0.085, freq_hz=tone_hz, harmonic2=0.33)
    exhale = synth_chime(sr, dur_s=0.095, freq_hz=tone_hz * 0.75, harmonic2=0.12)
    gl_in, gr_in = pan_gains(-abs(pan_mag))
    gl_ex, gr_ex = pan_gains(abs(pan_mag))

    t = start_s
    while t < end_s:
        idx_in = int(t * sr)
        mix_in(l, idx_in, inhale, level * gl_in)
        mix_in(r, idx_in, inhale, level * gr_in)

        t_ex = t + inh_s
        if t_ex < end_s:
            idx_ex = int(t_ex * sr)
            mix_in(l, idx_ex, exhale, level * gl_ex)
            mix_in(r, idx_ex, exhale, level * gr_ex)

        t += inh_s + exh_s


def add_periodic_cues(l, r, sr, start_s, end_s, interval_s, freq_hz, level, pan=0.0):
    t = start_s
    gl, gr = pan_gains(pan)
    while t < end_s:
        cue = cue_tone(sr, freq_hz, level)
        idx = int(t * sr)
        mix_in(l, idx, cue, gl)
        mix_in(r, idx, cue, gr)
        t += max(0.05, interval_s)


def add_sub_drone(l, r, sr, start_s, end_s, hz_a, hz_b, level):
    start = int(start_s * sr)
    end = min(len(l), int(end_s * sr))
    span = max(1, end - start)
    for i in range(start, end):
        x = (i - start) / span
        f = hz_a + (hz_b - hz_a) * x
        t = i / sr
        s = level * math.sin(2 * math.pi * f * t)
        l[i] += s
        r[i] += s


def add_sub_block(l, r, sr, freq_hz, level, start_idx, n_samples):
    """Fade-shaped sub block (avoids endless continuous drone feel)."""
    ramp = max(1, int(0.06 * sr))
    for i in range(max(0, n_samples)):
        j = start_idx + i
        if j >= len(l):
            break
        t = j / sr
        s = math.sin(2 * math.pi * freq_hz * t)
        g = 1.0
        if i < ramp:
            g = smoothstep(i / ramp)
        if i > n_samples - ramp:
            g = smoothstep((n_samples - i) / ramp)
        v = level * g * s
        l[j] += v
        r[j] += v


def schedule_hits(total_s, rate_hz_fn, jitter_s, start_s=0.0):
    """Schedule event hits from a time-varying rate function."""
    t = start_s
    hits = []
    while t < total_s:
        rate = max(0.001, float(rate_hz_fn(t)))
        dt = 1.0 / rate
        hits.append(max(0.0, t + random.uniform(-jitter_s, jitter_s)))
        t += dt
    return hits


def breath_rate_points(spec):
    """Return sorted (t_min, br) points from spec breath curve or phase bpm fields."""
    pts = []
    for p in spec.get("breath_curve", []):
        try:
            pts.append((float(p.get("t_min", 0.0)), float(p.get("br", 6.0))))
        except Exception:
            continue
    if pts:
        pts.sort(key=lambda x: x[0])
        return pts

    # Fallback: derive from phase bpm fields.
    for ph in spec.get("phases", []):
        try:
            t0 = float(ph.get("start_s", 0.0)) / 60.0
            t1 = float(ph.get("end_s", ph.get("start_s", 0.0))) / 60.0
            if "bpm" in ph:
                br = float(ph.get("bpm", 6.0))
                pts.append((t0, br))
                pts.append((t1, br))
            else:
                b0 = float(ph.get("bpm_start", ph.get("bpm", 6.0)))
                b1 = float(ph.get("bpm_end", ph.get("bpm", b0)))
                pts.append((t0, b0))
                pts.append((t1, b1))
        except Exception:
            continue
    pts.sort(key=lambda x: x[0])
    return pts


def breath_rate_at_s(points, t_s):
    """Interpolate breaths/minute from minute-based curve points."""
    if not points:
        return 6.0
    t_min = t_s / 60.0
    if t_min <= points[0][0]:
        return points[0][1]
    for i in range(1, len(points)):
        t0, b0 = points[i - 1]
        t1, b1 = points[i]
        if t_min <= t1:
            x = 0.0 if t1 == t0 else (t_min - t0) / (t1 - t0)
            x = smoothstep(max(0.0, min(1.0, x)))
            return b0 + (b1 - b0) * x
    return points[-1][1]


def is_arc1_wave_peak(t_min):
    return (35.0 <= t_min < 38.0) or (40.0 <= t_min < 43.0) or (45.0 <= t_min < 48.0)


def is_arc1_wave_recover(t_min):
    return (38.0 <= t_min < 40.0) or (43.0 <= t_min < 45.0) or (48.0 <= t_min < 50.0)


def phase_bpm(phase, t_norm):
    if "bpm" in phase:
        return float(phase["bpm"])
    a = float(phase.get("bpm_start", 6.0))
    b = float(phase.get("bpm_end", a))
    return a + (b - a) * max(0.0, min(1.0, t_norm))


def add_tribal_drums(l, r, sr, spec, params):
    from engine.dsp.drums import synth_frame_drum_skin, synth_low_tom_skin, synth_shaker, synth_wood_tick
    drum_level = float(params.get("drum_level", 0.05))
    accent_level = float(params.get("accent_level", 0.04))
    shaker_level = float(params.get("shaker_level", 0.025))
    floor_level = float(params.get("floor_level", drum_level * 0.4))
    intensity = float(params.get("intensity_scale", 1.0))
    peak_mult = float(params.get("phase4_peak_multiplier", 1.25))
    recover_mult = float(params.get("phase4_recover_multiplier", 0.75))

    # ARC-style breath-locked groove (also available as opt-in for other families).
    points = breath_rate_points(spec)
    use_breath_locked = bool(params.get("breath_locked", False)) or spec.get("family") == "ARC"
    if use_breath_locked and points:
        total_s = float(spec.get("duration_s", len(l) / sr))

        def br_fn(t_s):
            return breath_rate_at_s(points, t_s)

        def x_from_br(br):
            return max(0.0, min(1.0, (br - 6.0) / (28.0 - 6.0)))

        def rate_floor(t_s):
            return (br_fn(t_s) * 2.0) / 60.0

        def rate_primary(t_s):
            return (br_fn(t_s) * 4.0) / 60.0

        def rate_accent(t_s):
            return (br_fn(t_s) * 6.0) / 60.0

        frame = synth_frame_drum_skin(sr, float(params.get("frame_dur_s", 0.115)), float(params.get("frame_f0", 76.0)))
        tom = synth_low_tom_skin(sr, float(params.get("tom_dur_s", 0.165)), float(params.get("tom_f0", 60.0)))
        tick = synth_wood_tick(sr, float(params.get("tick_dur_s", 0.028)))
        shak = synth_shaker(sr, float(params.get("shaker_dur_s", 0.060)))

        floor_hits = schedule_hits(total_s, rate_floor, jitter_s=float(params.get("floor_jitter_s", 0.006)), start_s=0.0)
        drum_hits = schedule_hits(total_s, rate_primary, jitter_s=float(params.get("drum_jitter_s", 0.010)), start_s=0.2)
        accent_hits = schedule_hits(total_s, rate_accent, jitter_s=float(params.get("accent_jitter_s", 0.012)), start_s=0.3)
        shaker_hits = schedule_hits(total_s, rate_primary, jitter_s=float(params.get("shaker_jitter_s", 0.010)), start_s=0.4)

        # Floor anchor.
        for t_s in floor_hits:
            br = br_fn(t_s)
            x = x_from_br(br)
            g = floor_level * (0.68 + 0.32 * smoothstep(x)) * intensity
            idx = int(t_s * sr)
            mix_in(l, idx, frame, g)
            mix_in(r, idx, frame, g)

        # Primary hits: alternating frame/tom and peak-recover contrast.
        for idx_hit, t_s in enumerate(drum_hits):
            br = br_fn(t_s)
            x = x_from_br(br)
            g = drum_level * smoothstep(x) * intensity
            t_min = t_s / 60.0
            if spec.get("id") == "ARC-1TB":
                if is_arc1_wave_peak(t_min):
                    g *= peak_mult
                elif is_arc1_wave_recover(t_min):
                    g *= recover_mult
            src = frame if (idx_hit % 2 == 0) else tom
            pan = float(params.get("primary_pan", 0.12)) * (1.0 if (idx_hit % 4) < 2 else -1.0)
            gl, gr = pan_gains(pan)
            i0 = int(t_s * sr)
            mix_in(l, i0, src, g * gl)
            mix_in(r, i0, src, g * gr)

        # Accents: sparse at low rates, stronger on peaks, weaker on recovers.
        for idx_hit, t_s in enumerate(accent_hits):
            br = br_fn(t_s)
            x = x_from_br(br)
            if x < float(params.get("accent_min_x", 0.22)):
                continue
            g = accent_level * (smoothstep(x) ** 1.5) * intensity
            t_min = t_s / 60.0
            if spec.get("id") == "ARC-1TB":
                if is_arc1_wave_peak(t_min):
                    g *= float(params.get("accent_peak_multiplier", 1.35))
                elif is_arc1_wave_recover(t_min):
                    g *= float(params.get("accent_recover_multiplier", 0.45))
            pan = float(params.get("accent_pan", 0.20)) * (1.0 if (idx_hit % 2 == 0) else -1.0)
            gl, gr = pan_gains(pan)
            i0 = int(t_s * sr)
            mix_in(l, i0, tick, g * gl)
            mix_in(r, i0, tick, g * gr)

        # Shaker: high-rate zones only, peak-gated during ARC-1 wave cycle.
        for idx_hit, t_s in enumerate(shaker_hits):
            br = br_fn(t_s)
            x = x_from_br(br)
            if x < float(params.get("shaker_min_x", 0.58)):
                continue
            t_min = t_s / 60.0
            if spec.get("id") == "ARC-1TB" and (35.0 <= t_min < 50.0) and not is_arc1_wave_peak(t_min):
                continue
            g = shaker_level * (smoothstep(x) ** 1.9) * intensity
            if spec.get("id") == "ARC-1TB" and is_arc1_wave_peak(t_min):
                g *= float(params.get("shaker_peak_multiplier", 1.20))
            pan = float(params.get("shaker_pan", 0.24)) * (1.0 if (idx_hit % 2 == 0) else -1.0)
            gl, gr = pan_gains(pan)
            i0 = int(t_s * sr)
            mix_in(l, i0, shak, g * gl)
            mix_in(r, i0, shak, g * gr)
        return

    # Generic fallback for non-ARC families.
    for phase in spec.get("phases", []):
        start_s = phase["start_s"]
        end_s = phase["end_s"]
        t = start_s
        while t < end_s:
            tn = 0.0 if end_s <= start_s else (t - start_s) / (end_s - start_s)
            bpm = max(1.0, phase_bpm(phase, tn))
            beat_s = 60.0 / bpm
            idx = int(t * sr)

            kick = synth_frame_drum_skin(sr, 0.16, 65.0)
            tom = synth_low_tom_skin(sr, 0.12, 92.0)
            tick = synth_wood_tick(sr, 0.028)
            shake = synth_shaker(sr, 0.05)

            mix_in(l, idx, kick, drum_level * intensity)
            mix_in(r, idx, kick, drum_level * intensity)
            mix_in(l, idx + int(0.5 * beat_s * sr), tom, accent_level * intensity)
            mix_in(r, idx + int(0.5 * beat_s * sr), tom, accent_level * intensity)
            mix_in(l, idx + int(0.25 * beat_s * sr), tick, accent_level * 0.7 * intensity)
            mix_in(r, idx + int(0.25 * beat_s * sr), tick, accent_level * 0.7 * intensity)
            mix_in(l, idx + int(0.1 * beat_s * sr), shake, shaker_level * intensity)
            mix_in(r, idx + int(0.6 * beat_s * sr), shake, shaker_level * intensity)

            t += beat_s


def render_protocol(spec, sr):
    random.seed(spec['render']['seed'])
    total_s = spec['duration_s']
    n = int(total_s * sr)
    l, r = [0.0] * n, [0.0] * n
    
    # Check if this is old format (has 'levels' instead of 'audio_layers')
    if 'levels' in spec and 'audio_layers' not in spec:
        print(f"Warning: {spec['id']} uses old format - skipping for now")
        # Return silence for old format protocols
        return l, r

    validate_audio_layers(spec)
    
    # Noise bed
    for layer in spec.get('audio_layers', []):
        if layer['type'] == 'noise_bed':
            # Handle both old format (params as siblings) and new format (params as dict)
            if 'params' in layer:
                p = layer.get('params', layer)
            else:
                p = layer  # Old format: params are direct children
            
            noise_type = p.get('noise_type', p.get('noise', 'brown'))
            bl, br = build_noise_bed(sr, total_s, noise_type, p.get('level', 0.03), 
                                     p.get('drift_hz', 0.02), p.get('drift_depth', 0.1), 
                                     p.get('high_shelf', 0.0))
            for i in range(n):
                l[i] += bl[i]
                r[i] += br[i]
        
        elif layer['type'] == 'binaural':
            # Handle both formats
            p = layer.get('params', layer)
            phases = spec['phases']
            for i, phase in enumerate(phases):
                start, end = phase['start_s'], phase['end_s']
                dur = end - start
                seg_l = [0.0] * int(dur * sr)
                seg_r = [0.0] * int(dur * sr)
                
                key = f'phase{i+1}_hz'
                if key in p:
                    add_binaural_constant(seg_l, seg_r, sr, p[key], 
                                        p.get('carrier_hz', 174), p.get('level', 0.02), 2.0)
                else:
                    start_key = f'phase{i+1}_start'
                    end_key = f'phase{i+1}_end'
                    if start_key in p and end_key in p:
                        add_binaural_ramp(seg_l, seg_r, sr, p[start_key], 
                                        p[end_key], dur, p.get('carrier_hz', 174), 
                                        p['level'], 2.0)
                
                for j in range(len(seg_l)):
                    idx = int(start * sr) + j
                    if idx < n:
                        l[idx] += seg_l[j]
                        r[idx] += seg_r[j]
        
        elif layer['type'] == 'pulse_cues':
            p = layer.get('params', layer)
            for i, phase in enumerate(spec['phases'][1:], 1):
                rate_key = f'phase{i+1}_rate_s'
                if rate_key in p:
                    add_pulse_cues(l, r, sr, phase['start_s'], phase['end_s'],
                                 p[rate_key], p['level'], p['freq_hz'])
        
        elif layer['type'] == 'irregular_pulses':
            p = layer.get('params', layer)
            for i, phase in enumerate(spec['phases'][1:], 1):
                jitter_key = f'phase{i+1}_jitter'
                if jitter_key in p:
                    add_irregular_pulses(l, r, sr, phase['start_s'], 
                                       phase['end_s'], p['base_rate_s'],
                                       p[jitter_key], p['level'])
        
        elif layer['type'] == 'harmonic_pad':
            p = layer.get('params', layer)
            if p.get('phase3_enabled'):
                phase = spec['phases'][2]
                add_harmonic_pad(l, r, sr, phase['start_s'], phase['end_s'],
                               p['base_freq'], p['level'], p['swell_rate_s'])
        
        elif layer['type'] == 'spatial_sweep':
            from engine.dsp.spatial import spatial_sweep
            p = layer.get('params', layer)
            sl, sr_ch = spatial_sweep(sr, total_s, p['sweep_period_s'], p['pan_depth'])
            for i in range(n):
                l[i] += sl[i] * p['level']
                r[i] += sr_ch[i] * p['level']
        
        elif layer['type'] == 'switch_cues':
            p = layer.get('params', layer)
            switch_interval_s = p['switch_interval_s']
            cue_width_ms = p['cue_width_ms']
            cue_level = p['cue_level']
            tone_hz = p['tone_hz']
            
            cue_samples = int(cue_width_ms * sr / 1000)
            interval_samples = int(switch_interval_s * sr)
            
            for start_sample in range(0, n, interval_samples):
                if start_sample + cue_samples <= n:
                    for i in range(cue_samples):
                        t = i / sr
                        tone = math.sin(2 * math.pi * tone_hz * t)
                        env = math.exp(-5 * abs(t - cue_width_ms/2000) / (cue_width_ms/2000))
                        val = tone * env * cue_level
                        l[start_sample + i] += val
                        r[start_sample + i] += val
        
        elif layer['type'] == 'gamma_overlay':
            p = layer.get('params', layer)
            freq_hz = p['freq_hz']
            burst_rate_s = p['burst_rate_s']
            level = p['level']
            
            for i, phase in enumerate(spec['phases']):
                phase_num = i + 1
                enabled_key = f'phase{phase_num}_enabled'
                if p.get(enabled_key, False):
                    start_s = phase['start_s']
                    end_s = phase['end_s']
                    t = start_s
                    while t < end_s:
                        burst_start = int(t * sr)
                        burst_samples = int(0.2 * sr)
                        for j in range(burst_samples):
                            if burst_start + j < n:
                                sample_t = j / sr
                                gamma = math.sin(2 * math.pi * freq_hz * sample_t)
                                env = math.exp(-sample_t / 0.05)
                                val = gamma * env * level
                                l[burst_start + j] += val
                                r[burst_start + j] += val
                        t += burst_rate_s

        elif layer['type'] == 'tribal_drums':
            p = layer.get('params', layer)
            add_tribal_drums(l, r, sr, spec, p)

        elif layer['type'] == 'sub':
            p = layer.get('params', layer)
            hz_min = float(p.get('hz_min', 45.0))
            hz_max = float(p.get('hz_max', 55.0))
            base_level = float(p.get('level', 0.03))
            mode = str(p.get('mode', 'breath_locked' if spec.get('family') == 'ARC' else 'continuous'))

            if mode == 'breath_locked' and spec.get('family') == 'ARC' and breath_rate_points(spec):
                points = breath_rate_points(spec)
                block_s = float(p.get('block_seconds', 1.0))
                block_n = max(1, int(block_s * sr))
                for b in range(0, n, block_n):
                    t_s = b / sr
                    br = breath_rate_at_s(points, t_s)
                    x = max(0.0, min(1.0, (br - 6.0) / (28.0 - 6.0)))
                    sub_hz = hz_min + (hz_max - hz_min) * x
                    sub_lv = base_level * (0.65 + 0.55 * smoothstep(x))

                    t_min = t_s / 60.0
                    if spec.get("id") == "ARC-1TB":
                        if is_arc1_wave_peak(t_min):
                            sub_lv *= float(p.get("phase4_peak_multiplier", 1.18))
                        elif is_arc1_wave_recover(t_min):
                            sub_lv *= float(p.get("phase4_recover_multiplier", 0.72))

                    add_sub_block(l, r, sr, sub_hz, sub_lv, b, min(block_n, n - b))
            else:
                add_sub_drone(l, r, sr, 0.0, total_s, hz_min, hz_max, base_level)

        elif layer['type'] == 'room_illusion':
            from engine.dsp.room import add_room_early_reflections, add_ambience_bed
            p = layer.get('params', layer)
            if p.get('enabled', True):
                add_room_early_reflections(
                    l, r, sr, float(p.get('room_ms', 10.0)), float(p.get('room_level', 0.015))
                )
                ambience = p.get('ambience_level', float(p.get('room_level', 0.015)) * 0.5)
                add_ambience_bed(l, r, sr, float(ambience))

        elif layer['type'] == 'body_cues':
            p = layer.get('params', layer)
            if len(spec.get('phases', [])) >= 2 and p.get('phase2_enabled', True):
                ph = spec['phases'][1]
                add_periodic_cues(
                    l, r, sr, ph['start_s'], ph['end_s'],
                    float(p.get('rate_s', 45.0)),
                    float(p.get('freq_hz', 110.0)),
                    float(p.get('transient_level', 0.03)),
                )

        elif layer['type'] == 'sub_power':
            p = layer.get('params', layer)
            phases = spec.get('phases', [])
            mult2 = float(p.get('phase2_multiplier', 1.0))
            mult3 = float(p.get('phase3_multiplier', 1.0))
            base = float(p.get('level', 0.04))
            hz_min = float(p.get('hz_min', 40.0))
            hz_max = float(p.get('hz_max', 60.0))
            if phases:
                add_sub_drone(l, r, sr, phases[0]['start_s'], phases[0]['end_s'], hz_min, hz_max, base)
            if len(phases) > 1:
                add_sub_drone(l, r, sr, phases[1]['start_s'], phases[1]['end_s'], hz_min, hz_max, base * mult2)
            if len(phases) > 2:
                add_sub_drone(l, r, sr, phases[2]['start_s'], phases[2]['end_s'], hz_min, hz_max, base * mult3)

        elif layer['type'] == 'steady_groove':
            p = layer.get('params', layer)
            bpm = float(p.get('bpm', 78.0))
            rate_s = 60.0 / max(1.0, bpm)
            for i, ph in enumerate(spec.get('phases', [])):
                enabled = p.get(f'phase{i+1}_enabled', True)
                if enabled:
                    add_periodic_cues(
                        l, r, sr, ph['start_s'], ph['end_s'], rate_s,
                        140.0, float(p.get('level', 0.02))
                    )

        elif layer['type'] == 'breath_cues':
            p = layer.get('params', layer)
            phase_idxs = layer.get('phases', [1])
            for pi in phase_idxs:
                if 1 <= pi <= len(spec.get('phases', [])):
                    ph = spec['phases'][pi - 1]
                    add_breath_cues(
                        l, r, sr,
                        ph['start_s'], ph['end_s'],
                        p.get('preset', '4-6'),
                        float(p.get('level', 0.03)),
                        float(p.get('tone_hz', 880.0)),
                        float(p.get('pan_mag', 0.15)),
                    )

        elif layer['type'] == 'return_cues':
            phase_idxs = layer.get('phases', [3])
            for pi in phase_idxs:
                if 1 <= pi <= len(spec.get('phases', [])):
                    ph = spec['phases'][pi - 1]
                    add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], 75.0, 320.0, 0.03)

        elif layer['type'] == 'letgo_swells':
            phase_idxs = layer.get('phases', [4])
            for pi in phase_idxs:
                if 1 <= pi <= len(spec.get('phases', [])):
                    ph = spec['phases'][pi - 1]
                    add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], 120.0, 180.0, 0.025)

        elif layer['type'] == 'house_beat':
            p = layer.get('params', layer)
            if p.get('enabled', False):
                bpm = float(p.get('bpm', 122.0))
                rate = 60.0 / max(1.0, bpm)
                for ph in spec.get('phases', []):
                    add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], rate, 96.0, float(p.get('level', 0.02)))

        elif layer['type'] == 'location_tones':
            p = layer.get('params', layer)
            if len(spec.get('phases', [])) >= 2:
                ph = spec['phases'][1]
                rate = float(p.get('phase2_rate_s', 90.0))
                pan_sep = 0.6 if p.get('pan_sweep', False) else 0.0
                t = ph['start_s']
                flip = 1.0
                while t < ph['end_s']:
                    pan = pan_sep * flip
                    add_periodic_cues(
                        l, r, sr, t, min(t + 0.01, ph['end_s']), 9999.0,
                        float(p.get('freq_hz', 220.0)), float(p.get('level', 0.02)), pan=pan
                    )
                    flip *= -1.0
                    t += rate

        elif layer['type'] == 'resolution_cues':
            p = layer.get('params', layer)
            phases = spec.get('phases', [])
            if phases and p.get('phase1_enabled', False):
                ph = phases[0]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], 45.0, float(p.get('freq_hz', 174.0)), float(p.get('level', 0.03)))
            if len(phases) >= 3 and p.get('phase3_enabled', False):
                ph = phases[2]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], 60.0, float(p.get('freq_hz', 174.0)), float(p.get('level', 0.03)))

        elif layer['type'] == 'shimmer':
            p = layer.get('params', layer)
            if len(spec.get('phases', [])) >= 2 and p.get('phase2_enabled', True):
                ph = spec['phases'][1]
                lo, hi = p.get('freq_range', [3000.0, 8000.0])
                for k, frac in enumerate([0.2, 0.5, 0.8]):
                    f = float(lo) + (float(hi) - float(lo)) * frac
                    add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], 12.0 + k * 3, f, float(p.get('level', 0.008)) * 0.5)

        elif layer['type'] == 'sub_pulse':
            p = layer.get('params', layer)
            if len(spec.get('phases', [])) >= 2 and p.get('phase2_enabled', True):
                ph = spec['phases'][1]
                add_sub_drone(l, r, sr, ph['start_s'], ph['end_s'], float(p.get('hz', 0.3)), float(p.get('hz', 0.3)), float(p.get('level', 0.03)))

        elif layer['type'] == 'heartbeat_cues':
            p = layer.get('params', layer)
            if len(spec.get('phases', [])) >= 2 and p.get('phase2_enabled', True):
                ph = spec['phases'][1]
                interval = 60.0 / max(1.0, float(p.get('bpm', 60.0)))
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], interval, 70.0, float(p.get('level', 0.02)))

        elif layer['type'] == 'dissolve_cues':
            p = layer.get('params', layer)
            phases = spec.get('phases', [])
            if len(phases) >= 2:
                add_periodic_cues(
                    l, r, sr, phases[1]['start_s'], phases[1]['end_s'],
                    float(p.get('phase2_rate_s', 120.0)), float(p.get('freq_start', 220.0)),
                    float(p.get('level', 0.02))
                )
            if len(phases) >= 3:
                add_periodic_cues(
                    l, r, sr, phases[2]['start_s'], phases[2]['end_s'],
                    float(p.get('phase3_rate_s', 180.0)), float(p.get('freq_end', 110.0)),
                    float(p.get('level', 0.02))
                )

        elif layer['type'] == 'reality_check_cues':
            p = layer.get('params', layer)
            phases = spec.get('phases', [])
            interval = float(p.get('interval_s', 180.0))
            level = float(p.get('level', 0.018))
            freq = float(p.get('freq_hz', 220.0))
            if len(phases) >= 2 and p.get('phase2_enabled', False):
                ph = phases[1]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], interval, freq, level)
            if len(phases) >= 3 and p.get('phase3_enabled', False):
                ph = phases[2]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], interval, freq, level)

        elif layer['type'] == 'dyadic_cues':
            p = layer.get('params', layer)
            phases = spec.get('phases', [])
            interval = 60.0 / max(1.0, float(p.get('breath_rate', 6.0)))
            level = float(p.get('level', 0.03))
            pan_sep = float(p.get('pan_separation', 0.6))
            if len(phases) >= 1:
                ph = phases[0]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], interval, 220.0, level, pan=0.0)
            if len(phases) >= 2:
                ph = phases[1]
                t = ph['start_s']
                side = -1.0
                while t < ph['end_s']:
                    add_periodic_cues(l, r, sr, t, min(t + 0.01, ph['end_s']), 9999.0, 220.0, level, pan=side * pan_sep)
                    side *= -1.0
                    t += interval
            if len(phases) >= 3:
                ph = phases[2]
                add_periodic_cues(l, r, sr, ph['start_s'], ph['end_s'], interval, 220.0, level, pan=0.0)
    
    # Add signature tones at start and phase transitions
    if 'identity' in spec and 'signature_hz' in spec['identity']:
        sig_freqs = spec['identity']['signature_hz']
        sig_ms = spec['identity'].get('signature_ms', 300)
        sig_level = spec['identity'].get('signature_level', 0.020)
        
        # Signature at start (0s)
        add_signature(l, r, sr, 0.0, sig_freqs, sig_ms, sig_level)
        
        # Signature at each phase transition
        for phase in spec['phases'][1:]:
            add_signature(l, r, sr, phase['start_s'], sig_freqs, sig_ms, sig_level)
    
    # Family-aware loudness targeting + lightweight mastering bus.
    profile = get_master_profile(spec.get("family"))
    l, r, _ = master_stereo(l, r, sr, profile, phases=spec.get("phases", []), family=spec.get("family", ""))

    if spec['render']['peak_norm']:
        l, r = normalize_stereo(l, r, 0.98)
    
    return l, r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec", help="Path to YAML spec")
    p.add_argument("--out_dir", default="renders")
    p.add_argument("--strict-qc", action="store_true", help="Exit non-zero if QC fails.")
    args = p.parse_args()
    
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    
    sr = spec['render']['sr']
    print(f"Rendering {spec['id']}...")
    
    l, r = render_protocol(spec, sr)
    
    out_path = os.path.join(args.out_dir, f"{spec['id']}_master.wav")
    write_wav_stereo(out_path, l, r, sr)
    
    metrics = qc_report(l, r, sr)
    phase_spectral = phase_spectral_balance(l, r, sr, spec.get("phases", []))
    spectral_failed = spectral_balance_failures(phase_spectral, spec.get("family", ""))
    qc_passed, failed_checks, _ = evaluate_qc(metrics, spec["duration_s"], spec.get("family"))
    if spectral_failed:
        failed_checks.extend(spectral_failed)
        qc_passed = False
    # Recompute mastering meta from finished buffers for QC artifact traceability.
    from engine.dsp.mastering import estimate_lufs_stereo
    mastering_meta = {
        "target_lufs": get_master_profile(spec.get("family")).get("target_lufs"),
        "post_lufs_estimate": estimate_lufs_stereo(l, r),
        "spectral_thresholds": get_spectral_thresholds(spec.get("family", "")),
        "phase_spectral_balance": phase_spectral,
    }
    qc_path = write_qc_artifact(spec, out_path, metrics, qc_passed, failed_checks, mastering_meta=mastering_meta)
    print(f"Complete: {out_path}")
    print(f"Peak: {metrics['peak']:.3f} | RMS: {metrics['rms']:.4f}")
    print(f"QC: {'PASS' if qc_passed else 'FAIL'} ({qc_path})")
    if args.strict_qc and not qc_passed:
        print(f"QC checks failed: {', '.join(failed_checks)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
