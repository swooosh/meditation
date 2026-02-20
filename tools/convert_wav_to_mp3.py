#!/usr/bin/env python3
"""Batch convert protocol WAV masters to MP3 using ffmpeg."""
import argparse
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Convert *_master.wav files to MP3.")
    parser.add_argument("--all", action="store_true", help="Convert all *_master.wav under protocols/*/renders.")
    parser.add_argument("--bitrate", default="192k", help="MP3 bitrate (default: 192k).")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing MP3 files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned conversions without running ffmpeg.")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not found in PATH.")

    root = Path(__file__).resolve().parents[1]
    wavs = sorted(root.glob("protocols/*/renders/*_master.wav")) if args.all else []

    if not wavs:
        print("No input files found. Use --all to convert all masters.")
        return

    print(f"Found {len(wavs)} WAV masters. bitrate={args.bitrate}")
    ok = 0
    skipped = 0
    failed = 0

    for wav in wavs:
        mp3 = wav.with_suffix(".mp3")
        if mp3.exists() and not args.overwrite:
            skipped += 1
            print(f"SKIP {mp3}")
            continue

        cmd = [
            "ffmpeg",
            "-y" if args.overwrite else "-n",
            "-i", str(wav),
            "-codec:a", "libmp3lame",
            "-b:a", args.bitrate,
            str(mp3),
        ]
        print(f"CONVERT {wav} -> {mp3}")
        if args.dry_run:
            continue

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            ok += 1
        else:
            failed += 1
            tail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "unknown ffmpeg error"
            print(f"FAILED {wav.name}: {tail}")

    print(f"Done. converted={ok} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
