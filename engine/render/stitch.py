"""Phase stitching with crossfades."""
import math
from typing import List, Tuple


def crossfade_concat(parts: List[Tuple[List[float], List[float]]], sr: int, 
                    xfade_s: float) -> Tuple[List[float], List[float]]:
    """Concatenate stereo buffers with equal-power crossfade."""
    if not parts:
        return [], []
    xfade_n = max(1, int(xfade_s * sr))
    out_l, out_r = parts[0][0][:], parts[0][1][:]
    for (nl, nr) in parts[1:]:
        if xfade_n >= len(out_l) or xfade_n >= len(nl):
            out_l.extend(nl)
            out_r.extend(nr)
            continue
        a_start = len(out_l) - xfade_n
        b_start = 0
        for i in range(xfade_n):
            x = i / xfade_n
            ga = math.cos(x * math.pi / 2)
            gb = math.sin(x * math.pi / 2)
            out_l[a_start + i] = out_l[a_start + i] * ga + nl[b_start + i] * gb
            out_r[a_start + i] = out_r[a_start + i] * ga + nr[b_start + i] * gb
        out_l.extend(nl[xfade_n:])
        out_r.extend(nr[xfade_n:])
    return out_l, out_r
