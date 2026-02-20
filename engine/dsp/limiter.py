"""Limiting and soft clipping."""
import math


def soft_clip(x: float, drive: float) -> float:
    """Gentle tanh soft clip."""
    return math.tanh(drive * x) / math.tanh(drive)
