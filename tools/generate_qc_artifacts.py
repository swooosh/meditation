#!/usr/bin/env python3
"""Backfill QC JSON artifacts for existing rendered WAV masters."""
import argparse
import json
import math
import struct
import wave
from pathlib import Path

import yaml

from status_report import build_status
from render_protocol import evaluate_qc
from engine.render.validate import spectral_balance_failures, get_spectral_thresholds


def compute_qc_from_wav(path: Path, phases=None, chunk_frames: int = 4096, windows: int = 512):
    """Compute approximate QC metrics from sampled windows across stereo WAV."""
    phases = phases or []
    phase_bounds = []
    for idx, ph in enumerate(phases, start=1):
        phase_bounds.append({
            "index": idx,
            "name": ph.get("name", f"Phase {idx}"),
            "start": int(float(ph.get("start_s", 0.0))),
            "end": int(float(ph.get("end_s", 0.0))),
            "low_sq": 0.0,
            "mid_sq": 0.0,
            "high_sq": 0.0,
            "count": 0,
        })

    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()

        if channels != 2:
            raise ValueError(f"{path}: expected stereo WAV, got {channels} channels")
        if sampwidth != 2:
            raise ValueError(f"{path}: expected 16-bit PCM WAV, got sample width {sampwidth}")

        peak = 0.0
        sum_sq = 0.0
        sum_l = 0.0
        sum_r = 0.0
        silent_frames = 0
        clipped_samples = 0
        scanned_frames = 0
        scale = 32768.0

        if nframes <= chunk_frames * windows:
            sample_positions = [0]
            pos = 0
            while pos < nframes:
                sample_positions.append(pos)
                pos += chunk_frames
        else:
            step = max(1, int((nframes - chunk_frames) / max(1, windows - 1)))
            sample_positions = [i * step for i in range(windows)]

        for pos in sample_positions:
            pos = min(max(0, int(pos)), max(0, nframes - 1))
            wf.setpos(pos)
            raw = wf.readframes(min(chunk_frames, nframes - pos))
            if not raw:
                continue
            samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
            frames_in_chunk = len(samples) // 2
            scanned_frames += frames_in_chunk
            # Local filter state per sampled window for coarse spectral estimate.
            lp180 = 0.0
            lp2500 = 0.0
            dt = 1.0 / float(framerate)
            rc1 = 1.0 / (2.0 * math.pi * 180.0)
            rc2 = 1.0 / (2.0 * math.pi * 2500.0)
            a1 = dt / (rc1 + dt)
            a2 = dt / (rc2 + dt)
            abs_frame = pos
            phase_i = 0

            for i in range(0, len(samples), 2):
                l = samples[i] / scale
                r = samples[i + 1] / scale
                al = abs(l)
                ar = abs(r)
                if al > peak:
                    peak = al
                if ar > peak:
                    peak = ar
                sum_sq += (l * l) + (r * r)
                sum_l += l
                sum_r += r
                if al < 1e-4 and ar < 1e-4:
                    silent_frames += 1
                if al >= 0.999:
                    clipped_samples += 1
                if ar >= 0.999:
                    clipped_samples += 1
                mono = 0.5 * (l + r)
                lp180 = lp180 + a1 * (mono - lp180)
                lp2500 = lp2500 + a2 * (mono - lp2500)
                low = lp180
                mid = lp2500 - lp180
                high = mono - lp2500

                while phase_i < len(phase_bounds) and abs_frame >= phase_bounds[phase_i]["end"] * framerate:
                    phase_i += 1
                if phase_i < len(phase_bounds):
                    ph = phase_bounds[phase_i]
                    if abs_frame >= ph["start"] * framerate:
                        ph["low_sq"] += low * low
                        ph["mid_sq"] += mid * mid
                        ph["high_sq"] += high * high
                        ph["count"] += 1
                abs_frame += 1

    if nframes == 0 or scanned_frames == 0:
        return {
            "peak": 0.0,
            "rms": 0.0,
            "crest_factor": 0.0,
            "dc_offset_l": 0.0,
            "dc_offset_r": 0.0,
            "silence_ratio": 1.0,
            "clipped_ratio": 0.0,
            "duration_s": 0.0,
            "sample_rate": framerate,
            "samples": 0,
        }

    rms = math.sqrt(sum_sq / float(2 * scanned_frames))
    phase_spectral = []
    for ph in phase_bounds:
        if ph["count"] <= 0:
            continue
        low_r = math.sqrt(ph["low_sq"] / float(ph["count"]))
        mid_r = math.sqrt(ph["mid_sq"] / float(ph["count"]))
        high_r = math.sqrt(ph["high_sq"] / float(ph["count"]))
        phase_spectral.append({
            "phase_index": ph["index"],
            "phase_name": ph["name"],
            "low_rms": low_r,
            "mid_rms": mid_r,
            "high_rms": high_r,
            "low_to_mid": low_r / (mid_r + 1e-9),
            "high_to_mid": high_r / (mid_r + 1e-9),
        })

    return {
        "peak": peak,
        "rms": rms,
        "crest_factor": (peak / rms) if rms > 0 else 0.0,
        "dc_offset_l": sum_l / float(scanned_frames),
        "dc_offset_r": sum_r / float(scanned_frames),
        "silence_ratio": silent_frames / float(scanned_frames),
        "clipped_ratio": clipped_samples / float(2 * scanned_frames),
        "duration_s": nframes / float(framerate),
        "sample_rate": framerate,
        "samples": int(nframes),
        "scanned_frames": int(scanned_frames),
        "phase_spectral_balance": phase_spectral,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate QC sidecars for existing *_master.wav renders.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing QC JSON files.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    rows = build_status(root)

    written = 0
    skipped = 0
    failed = 0
    for row in rows:
        if not row.get("render_exists"):
            continue
        wav_path = Path(row["render_path"])
        qc_dir = wav_path.parent / "qc"
        qc_path = qc_dir / f"{row['id']}_qc.json"

        if qc_path.exists() and not args.overwrite:
            skipped += 1
            continue

        try:
            spec = yaml.safe_load(Path(row["spec_path"]).read_text())
            metrics = compute_qc_from_wav(wav_path, phases=spec.get("phases", []))
            expected_duration_s = float(row["spec_duration_m"] * 60)
            qc_passed, failed_checks, thresholds = evaluate_qc(
                metrics, expected_duration_s, row.get("family")
            )
            spectral_failed = spectral_balance_failures(
                metrics.get("phase_spectral_balance", []),
                row.get("family"),
            )
            if spectral_failed:
                failed_checks.extend(spectral_failed)
                qc_passed = False
            payload = {
                "id": row["id"],
                "family": row["family"],
                "render_path": str(wav_path),
                "expected_duration_s": expected_duration_s,
                "qc_passed": qc_passed,
                "failed_checks": failed_checks,
                "thresholds": thresholds,
                "metrics": metrics,
                "spectral_thresholds": get_spectral_thresholds(row.get("family")),
            }
            qc_dir.mkdir(parents=True, exist_ok=True)
            qc_path.write_text(json.dumps(payload, indent=2) + "\n")
            written += 1
        except Exception as e:
            failed += 1
            print(f"FAILED {row['id']}: {e}")

    print(f"Done. written={written} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
