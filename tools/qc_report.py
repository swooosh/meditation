#!/usr/bin/env python3
"""Run QC metrics on rendered WAV files."""
import argparse
import csv
import struct
import wave
from pathlib import Path

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.render.validate import qc_report as calc_qc_report


def read_wav_stereo(path):
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if channels != 2:
        raise ValueError(f"{path}: expected stereo WAV, got {channels} channels")
    if sampwidth != 2:
        raise ValueError(f"{path}: expected 16-bit PCM WAV, got sample width {sampwidth}")

    samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    left = []
    right = []
    scale = 32768.0
    for i in range(0, len(samples), 2):
        left.append(samples[i] / scale)
        right.append(samples[i + 1] / scale)
    return left, right, framerate


def collect_wavs(paths):
    files = []
    for p in paths:
        pp = Path(p)
        if pp.is_file() and pp.suffix.lower() == ".wav":
            files.append(pp)
        elif pp.is_dir():
            files.extend(sorted(pp.rglob("*_master.wav")))
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(description="Compute QC metrics for WAV files.")
    parser.add_argument("paths", nargs="+", help="WAV files and/or directories")
    parser.add_argument("--csv", dest="csv_path", help="Write CSV output to this path")
    args = parser.parse_args()

    wavs = collect_wavs(args.paths)
    if not wavs:
        print("No WAV files found.")
        return

    rows = []
    for wav_path in wavs:
        try:
            l, r, sr = read_wav_stereo(wav_path)
            qc = calc_qc_report(l, r, sr)
            row = {
                "file": str(wav_path),
                "duration_s": round(qc["duration_s"], 2),
                "peak": round(qc["peak"], 4),
                "rms": round(qc["rms"], 5),
                "crest_factor": round(qc["crest_factor"], 3),
                "dc_offset_l": round(qc["dc_offset_l"], 6),
                "dc_offset_r": round(qc["dc_offset_r"], 6),
                "silence_ratio": round(qc.get("silence_ratio", 0.0), 6),
                "clipped_ratio": round(qc.get("clipped_ratio", 0.0), 6),
                "sample_rate": qc["sample_rate"],
            }
            rows.append(row)
        except Exception as e:
            rows.append({"file": str(wav_path), "error": str(e)})

    ok_rows = [r for r in rows if "error" not in r]
    err_rows = [r for r in rows if "error" in r]

    for r in ok_rows:
        print(
            f"{r['file']}\n"
            f"  dur={r['duration_s']}s peak={r['peak']} rms={r['rms']} "
            f"crest={r['crest_factor']} dc=({r['dc_offset_l']},{r['dc_offset_r']}) "
            f"silence={r['silence_ratio']} clipped={r['clipped_ratio']}"
        )
    for r in err_rows:
        print(f"{r['file']}\n  ERROR: {r['error']}")

    if args.csv_path:
        out = Path(args.csv_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "file",
            "duration_s",
            "peak",
            "rms",
            "crest_factor",
            "dc_offset_l",
            "dc_offset_r",
            "silence_ratio",
            "clipped_ratio",
            "sample_rate",
            "error",
        ]
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\nWrote CSV: {out}")

    print(f"\nSummary: ok={len(ok_rows)} errors={len(err_rows)}")


if __name__ == "__main__":
    main()
