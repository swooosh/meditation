#!/usr/bin/env python3
"""Test renderer without YAML dependency."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.dsp.noise import brown_noise, voss_pink_noise
from engine.dsp.envelopes import fade_in_out
from engine.dsp.binaural import add_binaural_constant
from engine.render.render_core import normalize_stereo, write_wav_stereo
from engine.render.validate import qc_report

def test_perf_protocol():
    """Render PERF-01 without YAML."""
    sr = 44100
    total_s = 720  # 12 minutes
    n = int(total_s * sr)
    
    # Pink noise bed
    l = voss_pink_noise(n)
    r = voss_pink_noise(n)
    
    # Scale to level
    for i in range(n):
        l[i] *= 0.055
        r[i] *= 0.055
    
    # Add binaural ramp 8->12 Hz
    phase2_start = int(180 * sr)
    phase2_end = int(540 * sr)
    
    for i in range(phase2_start, phase2_end):
        t = (i - phase2_start) / (phase2_end - phase2_start)
        bb = 8.0 + (12.0 - 8.0) * t
        f_l = 200.0 - bb / 2.0
        f_r = 200.0 + bb / 2.0
        
        import math
        s_l = 0.016 * math.sin(2 * math.pi * f_l * i / sr)
        s_r = 0.016 * math.sin(2 * math.pi * f_r * i / sr)
        l[i] += s_l
        r[i] += s_r
    
    # Fade
    fade_in_out(l, sr, 2.0)
    fade_in_out(r, sr, 2.0)
    
    # Normalize
    l, r = normalize_stereo(l, r, 0.98)
    
    # Write
    os.makedirs("test_renders", exist_ok=True)
    write_wav_stereo("test_renders/PERF-01_test.wav", l, r, sr)
    
    # QC
    metrics = qc_report(l, r, sr)
    print(f"✓ PERF-01 test render complete")
    print(f"  Peak: {metrics['peak']:.3f} | RMS: {metrics['rms']:.4f}")
    print(f"  Duration: {metrics['duration_s']:.1f}s")
    print(f"  File: test_renders/PERF-01_test.wav")

if __name__ == "__main__":
    test_perf_protocol()
