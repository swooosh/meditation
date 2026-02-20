# Installation & Setup

## Requirements

- Python 3.7+
- PyYAML (for YAML spec parsing)

## Install Dependencies

```bash
pip install pyyaml
```

## Verify Installation

```bash
cd protocol-lab

# Test engine
python3 -c "
import sys
sys.path.insert(0, '.')
from engine.dsp.noise import brown_noise
from engine.render.render_core import write_wav_stereo, normalize_stereo

sr = 44100
l = brown_noise(int(5 * sr))
r = brown_noise(int(5 * sr))
l, r = normalize_stereo(l, r, 0.5)
write_wav_stereo('test.wav', l, r, sr)
print('Engine test passed!')
"
```

## Render Your First Protocol

### FSP-01 (Focused State Protocol)

```bash
cd protocols/FSP/audio
python3 render_fsp.py --level living --out_dir ../renders --master
```

Output:
- `../renders/phase1_downshift.wav`
- `../renders/phase2_body_scan.wav`
- `../renders/phase3_attentional_lock.wav`
- `../renders/phase4_state_shift.wav`
- `../renders/phase5_reintegration.wav`
- `../renders/FSP-01_master.wav` (stitched)

### ARC-1TB (Tribal Breath)

```bash
cd protocols/ARC/audio
python3 render_arc.py --out_dir ../renders
```

Output:
- `../renders/ARC-1TB_master.wav`

## Render Options

### FSP Levels
- `--level living`: Balanced, warm (default)
- `--level temple`: Minimal, deep stillness
- `--level focus`: Structured, brighter

### Common Options
- `--out_dir PATH`: Output directory
- `--master`: Create stitched master file (FSP only)
- `--spec PATH`: Custom YAML spec file

## Troubleshooting

### "No module named 'yaml'"
Install PyYAML: `pip install pyyaml`

### "Permission denied"
Make scripts executable: `chmod +x protocols/*/audio/*.py`

### Audio too quiet/loud
Adjust level parameters in YAML spec or use `--peak_norm` flag

## Next Steps

1. Listen to rendered protocols
2. Adjust parameters in YAML specs
3. Re-render and compare
4. Create new protocols using existing structure
