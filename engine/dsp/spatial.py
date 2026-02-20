"""Spatial audio effects - panning and spatial sweep."""
import math
import numpy as np


def spatial_sweep(sr, duration_s, sweep_period_s=8.0, pan_depth=0.6):
    """
    Generate spatial sweep effect with slow panning.
    
    Args:
        sr: Sample rate
        duration_s: Duration in seconds
        sweep_period_s: Period of one complete L-R-L sweep
        pan_depth: Panning intensity (0.0=center, 1.0=full L/R)
    
    Returns:
        (left, right): Stereo buffers with panned pink noise
    """
    n = int(duration_s * sr)
    
    # Generate pink noise via 1/f filter approximation
    white = np.random.randn(n)
    freqs = np.fft.rfftfreq(n, 1/sr)
    freqs[0] = 1  # Avoid division by zero
    pink_filter = 1 / np.sqrt(freqs)
    pink_fft = np.fft.rfft(white) * pink_filter
    pink = np.fft.irfft(pink_fft, n)
    
    # Normalize
    pink = pink / np.max(np.abs(pink))
    
    # Apply slow sine-wave panning
    left = np.zeros(n)
    right = np.zeros(n)
    
    for i in range(n):
        t = i / sr
        # Sine wave panning: -1 (left) to +1 (right)
        pan = pan_depth * math.sin(2.0 * math.pi * t / sweep_period_s)
        
        # Equal-power panning law
        angle = (pan + 1.0) * math.pi / 4  # Map [-1,1] to [0, π/2]
        gl = math.cos(angle)
        gr = math.sin(angle)
        
        left[i] = pink[i] * gl
        right[i] = pink[i] * gr
    
    return left.tolist(), right.tolist()
