#!/usr/bin/env python3
"""Batch render all protocols."""
import os
import subprocess
import sys

PROTOCOLS = [
    ("FSP", "FSP-01_31m.yaml"),
    ("ARC", "ARC-1TB_60m.yaml"),
    ("PERF", "PERF-01_12m.yaml"),
    ("RECON", "RECON-01_25m.yaml"),
    ("SLEEP", "SLEEP-01_30m.yaml"),
    ("CREA", "CREA-01_15m.yaml"),
    ("SENSE", "SENSE-01_10m.yaml"),
    ("META", "META-01_20m.yaml"),
]

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    renderer = os.path.join(root, "tools", "render_protocol.py")
    
    # Set PYTHONPATH to include protocol-lab root
    env = os.environ.copy()
    env['PYTHONPATH'] = root
    
    print("Batch rendering all protocols...\n")
    
    for family, spec_file in PROTOCOLS:
        spec_path = os.path.join(root, "protocols", family, "specs", spec_file)
        out_dir = os.path.join(root, "protocols", family, "renders")
        
        if not os.path.exists(spec_path):
            print(f"⚠️  Skipping {family}: spec not found")
            continue
        
        print(f"▶ Rendering {family}/{spec_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, renderer, spec_path, "--out_dir", out_dir],
                capture_output=True,
                text=True,
                timeout=300,
                env=env
            )
            
            if result.returncode == 0:
                print(f"✓ {family} complete")
                if result.stdout:
                    for line in result.stdout.strip().split('\n')[-2:]:
                        print(f"  {line}")
            else:
                print(f"✗ {family} failed:")
                print(f"  {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"✗ {family} timed out")
        except Exception as e:
            print(f"✗ {family} error: {e}")
        
        print()
    
    print("Batch render complete!")


if __name__ == "__main__":
    main()
