#!/usr/bin/env python3
"""ARC-1TB renderer using YAML spec."""
import argparse
import os
import random
import sys
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from engine.dsp.drums import synth_frame_drum_skin, synth_low_tom_skin, synth_wood_tick, synth_shaker
from engine.dsp.envelopes import smoothstep, fade_in_out
from engine.dsp.limiter import soft_clip
from engine.dsp.room import add_room_early_reflections, add_ambience_bed
from engine.render.render_core import normalize_stereo, write_wav_stereo, mix_mono_into_stereo
from engine.render.validate import qc_report


def br_at_minute(curve, t_min):
    for i in range(len(curve) - 1):
        if curve[i]['t_min'] <= t_min <= curve[i+1]['t_min']:
            t0, t1 = curve[i]['t_min'], curve[i+1]['t_min']
            br0, br1 = curve[i]['br'], curve[i+1]['br']
            x = 0.0 if t1 == t0 else (t_min - t0) / (t1 - t0)
            x = smoothstep(x)
            return br0 + (br1 - br0) * x
    return curve[-1]['br']


def phase4_is_peak(t_min):
    return (35.0 <= t_min < 38.0) or (40.0 <= t_min < 43.0) or (45.0 <= t_min < 48.0)


def phase4_is_recover(t_min):
    return (38.0 <= t_min < 40.0) or (43.0 <= t_min < 45.0) or (48.0 <= t_min < 50.0)


def schedule_hits(total_s, rate_fn, jitter_s, start_s=0.0):
    t = start_s
    hits = []
    while t < total_s:
        rate = max(0.001, rate_fn(t))
        dt = 1.0 / rate
        hits.append(max(0.0, t + random.uniform(-jitter_s, jitter_s)))
        t += dt
    return hits


def render_arc(spec, sr):
    random.seed(spec['render']['seed'])
    
    total_s = spec['duration_s']
    n = int(total_s * sr)
    l = [0.0] * n
    r = [0.0] * n
    
    curve = spec['breath_curve']
    params = spec['audio_layers'][0]['params']
    
    def br_fn(t_s):
        return br_at_minute(curve, t_s / 60.0)
    
    def x_from_br(br):
        return max(0.0, min(1.0, (br - 6.0) / (28.0 - 6.0)))
    
    # Synth voices
    frame = synth_frame_drum_skin(sr, 0.115, 76.0)
    tom = synth_low_tom_skin(sr, 0.165, 60.0)
    tick = synth_wood_tick(sr)
    shak = synth_shaker(sr)
    
    # Schedule
    floor_hits = schedule_hits(total_s, lambda t: br_fn(t) * 2.0 / 60.0, 0.006)
    drum_hits = schedule_hits(total_s, lambda t: br_fn(t) * 4.0 / 60.0, 0.010, 0.2)
    accent_hits = schedule_hits(total_s, lambda t: br_fn(t) * 6.0 / 60.0, 0.012, 0.3)
    shaker_hits = schedule_hits(total_s, lambda t: br_fn(t) * 4.0 / 60.0, 0.010, 0.4)
    
    # Floor
    for t_s in floor_hits:
        br = br_fn(t_s)
        x = x_from_br(br)
        g = params['floor_level'] * (0.68 + 0.32 * smoothstep(x))
        i0 = int(t_s * sr)
        mix_mono_into_stereo(l, r, i0, frame, g, 0.0)
    
    # Primary drums
    for idx, t_s in enumerate(drum_hits):
        br = br_fn(t_s)
        x = x_from_br(br)
        g = params['drum_level'] * smoothstep(x)
        
        t_min = t_s / 60.0
        if phase4_is_peak(t_min):
            g *= params['phase4_peak_multiplier']
        elif phase4_is_recover(t_min):
            g *= params['phase4_recover_multiplier']
        
        src = frame if (idx % 2 == 0) else tom
        pan = 0.12 * (1.0 if (idx % 4) < 2 else -1.0)
        i0 = int(t_s * sr)
        mix_mono_into_stereo(l, r, i0, src, g, pan)
    
    # Accents
    for idx, t_s in enumerate(accent_hits):
        br = br_fn(t_s)
        x = x_from_br(br)
        if x < 0.22:
            continue
        
        g = params['accent_level'] * (smoothstep(x) ** 1.5)
        t_min = t_s / 60.0
        if phase4_is_peak(t_min):
            g *= 1.35
        elif phase4_is_recover(t_min):
            g *= 0.45
        
        pan = 0.20 * (1.0 if (idx % 2 == 0) else -1.0)
        i0 = int(t_s * sr)
        mix_mono_into_stereo(l, r, i0, tick, g, pan)
    
    # Shaker
    for idx, t_s in enumerate(shaker_hits):
        br = br_fn(t_s)
        x = x_from_br(br)
        if x < 0.58:
            continue
        
        t_min = t_s / 60.0
        if 35.0 <= t_min < 50.0 and not phase4_is_peak(t_min):
            continue
        
        g = params['shaker_level'] * (smoothstep(x) ** 1.9)
        if phase4_is_peak(t_min):
            g *= 1.20
        
        pan = 0.24 * (1.0 if (idx % 2 == 0) else -1.0)
        i0 = int(t_s * sr)
        mix_mono_into_stereo(l, r, i0, shak, g, pan)
    
    # Sub
    import math
    sub_params = spec['audio_layers'][1]['params']
    block_s = 1.0
    block_n = int(block_s * sr)
    for b in range(0, n, block_n):
        t_s = b / sr
        br = br_fn(t_s)
        x = x_from_br(br)
        
        sub_hz = sub_params['hz_min'] + (sub_params['hz_max'] - sub_params['hz_min']) * x
        sub_lv = sub_params['level'] * (0.65 + 0.55 * smoothstep(x))
        
        t_min = t_s / 60.0
        if phase4_is_peak(t_min):
            sub_lv *= sub_params['phase4_peak_multiplier']
        elif phase4_is_recover(t_min):
            sub_lv *= sub_params['phase4_recover_multiplier']
        
        ramp = max(1, int(0.06 * sr))
        for i in range(min(block_n, n - b)):
            j = b + i
            t = j / sr
            s = math.sin(2 * math.pi * sub_hz * t)
            g = 1.0
            if i < ramp:
                g = smoothstep(i / ramp)
            if i > block_n - ramp:
                g = smoothstep((block_n - i) / ramp)
            v = sub_lv * g * s
            l[j] += v
            r[j] += v
    
    # Room
    room_params = spec['audio_layers'][2]['params']
    if room_params['enabled']:
        add_room_early_reflections(l, r, sr, room_params['room_ms'], room_params['room_level'])
        add_ambience_bed(l, r, sr, room_params['ambience_level'])
    
    # Fade
    fade_in_out(l, sr, 0.6)
    fade_in_out(r, sr, 0.6)
    
    # Soft clip
    if spec['render']['bus_softclip']:
        drive = spec['render']['clip_drive']
        for i in range(n):
            l[i] = soft_clip(l[i], drive)
            r[i] = soft_clip(r[i], drive)
    
    if spec['render']['peak_norm']:
        l, r = normalize_stereo(l, r, 0.98)
    
    return l, r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec", default="specs/ARC-1TB_60m.yaml")
    p.add_argument("--out_dir", default="renders")
    args = p.parse_args()
    
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    
    sr = spec['render']['sr']
    
    print(f"Rendering {spec['id']}...")
    l, r = render_arc(spec, sr)
    
    out_path = os.path.join(args.out_dir, f"{spec['id']}_master.wav")
    write_wav_stereo(out_path, l, r, sr)
    
    metrics = qc_report(l, r, sr)
    print(f"Rendered: {out_path}")
    print(f"Peak: {metrics['peak']:.3f} | RMS: {metrics['rms']:.4f} | Crest: {metrics['crest_factor']:.1f}dB")


if __name__ == "__main__":
    main()
