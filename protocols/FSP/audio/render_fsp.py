#!/usr/bin/env python3
"""FSP renderer using YAML spec."""
import argparse
import os
import random
import sys
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from engine.dsp.noise import voss_pink_noise, brown_noise
from engine.dsp.envelopes import smoothstep, fade_in_out
from engine.dsp.binaural import add_binaural_constant, add_binaural_ramp
from engine.render.render_core import pan_gains, normalize_stereo, write_wav_stereo, mix_in
from engine.render.stitch import crossfade_concat
from engine.render.validate import qc_report


def build_noise_bed(sr, total_s, noise, level, drift_hz, drift_depth, ramp_s):
    n = int(total_s * sr)
    if noise == "pink":
        base_l = voss_pink_noise(n)
        base_r = voss_pink_noise(n)
    else:
        base_l = brown_noise(n)
        base_r = brown_noise(n)
    
    l = [0.0] * n
    r = [0.0] * n
    ramp_n = max(1, int(ramp_s * sr))
    
    import math
    for i in range(n):
        t = i / sr
        pan = drift_depth * math.sin(2.0 * math.pi * drift_hz * t)
        gl, gr = pan_gains(pan)
        
        nl = base_l[i]
        nr = base_r[i]
        mid = 0.5 * (nl + nr)
        side = 0.5 * (nl - nr)
        
        l[i] = level * (mid + gl * side)
        r[i] = level * (mid - gr * side)
        
        if i < ramp_n:
            g = smoothstep(i / ramp_n)
            l[i] *= g; r[i] *= g
        elif i > n - ramp_n:
            g = smoothstep((n - i) / ramp_n)
            l[i] *= g; r[i] *= g
    
    return l, r


def render_phase(spec, phase_idx, level_cfg, sr):
    phase = spec['phases'][phase_idx]
    dur_s = phase['end_s'] - phase['start_s']
    
    if phase_idx in [0, 1]:
        # Simple brown bed
        level = 0.060 if phase_idx == 0 else 0.062
        drift = 0.008 if phase_idx == 0 else 0.010
        depth = 0.12 if phase_idx == 0 else 0.14
        return build_noise_bed(sr, dur_s, "brown", level, drift, depth, 4.0)
    
    elif phase_idx == 2:
        # Phase 3: attentional lock
        l, r = build_noise_bed(
            sr, dur_s,
            level_cfg['p3_noise'],
            level_cfg['p3_noise_level'],
            level_cfg['p3_drift_hz'],
            level_cfg['p3_drift_depth'],
            4.0
        )
        add_binaural_constant(
            l, r, sr,
            level_cfg['p3_binaural_hz'],
            level_cfg['p3_carrier_hz'],
            level_cfg['p3_binaural_level'],
            4.0
        )
        return l, r
    
    elif phase_idx == 3:
        # Phase 4: state shift
        l, r = build_noise_bed(
            sr, dur_s,
            level_cfg['p4_noise'],
            level_cfg['p4_noise_level'],
            level_cfg['p4_drift_hz'],
            level_cfg['p4_drift_depth'],
            4.5
        )
        add_binaural_ramp(
            l, r, sr,
            level_cfg['p4_bb_start'],
            level_cfg['p4_bb_end'],
            level_cfg['p4_bb_ramp_s'],
            level_cfg['p4_carrier_hz'],
            level_cfg['p4_bb_level'],
            4.5
        )
        return l, r
    
    elif phase_idx == 4:
        # Phase 5: reintegration
        l, r = build_noise_bed(sr, dur_s, "brown", 0.066, 0.012, 0.18, 3.0)
        add_binaural_ramp(l, r, sr, 6.0, 10.0, dur_s, 190.0, 0.016, 3.0)
        return l, r
    
    return [], []


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec", default="specs/FSP-01_31m.yaml")
    p.add_argument("--level", default="living", choices=["living", "temple", "focus"])
    p.add_argument("--out_dir", default="renders")
    p.add_argument("--master", action="store_true")
    args = p.parse_args()
    
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    
    sr = spec['render']['sr']
    random.seed(spec['render']['seed'])
    level_cfg = spec['levels'][args.level]
    
    outputs = []
    for i, phase in enumerate(spec['phases']):
        print(f"Rendering {phase['name']}...")
        l, r = render_phase(spec, i, level_cfg, sr)
        l, r = normalize_stereo(l, r, 0.98)
        
        fname = f"phase{i+1}_{phase['name'].lower().replace(' ', '_')}.wav"
        path = os.path.join(args.out_dir, fname)
        write_wav_stereo(path, l, r, sr)
        outputs.append((fname, l, r))
        
        metrics = qc_report(l, r, sr)
        print(f"  Peak: {metrics['peak']:.3f} | RMS: {metrics['rms']:.4f} | Crest: {metrics['crest_factor']:.1f}dB")
    
    if args.master:
        print("Stitching master...")
        parts = [(l, r) for _, l, r in outputs]
        ml, mr = crossfade_concat(parts, sr, 0.25)
        ml, mr = normalize_stereo(ml, mr, 0.98)
        master_path = os.path.join(args.out_dir, f"{spec['id']}_master.wav")
        write_wav_stereo(master_path, ml, mr, sr)
        print(f"Master: {master_path}")


if __name__ == "__main__":
    main()
