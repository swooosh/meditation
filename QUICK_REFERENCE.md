# Protocol Quick Reference

## When to Use Each Protocol

### Before Performance
**PERF-01** (12m) - Public speaking, negotiations, high-stakes meetings
- Calm + alert coherence
- Narrow focus without tension
- Ready state for action

### For Deep Work
**FSP-01** (31m) - Extended focus sessions, complex problem-solving
- Gateway-inspired attentional lock
- 3 levels: living (balanced), temple (minimal), focus (structured)
- Binaural entrainment support

### For Emotional Work
**RECON-01** (25m) - Processing difficult memories, trauma integration
- Safe container with theta support
- Gentle activation → reframe → resolution
- Use with care, consider therapeutic support

### For Creative Work
**CREA-01** (15m) - Breaking creative blocks, novel problem-solving
- Disrupts habitual patterns
- Irregular pulses increase cognitive flexibility
- Opens associative space

### For Physical Intensity
**ARC-1TB** (60m) - Somatic processing, controlled catharsis
- Breath-driven 6→28→6 bpm
- Wave cycling with peak/recover contrast
- Tribal percussion guidance

### For Sensory Enhancement
**SENSE-01** (10m) - Before athletic performance, nature immersion, concerts
- Increases perceptual resolution
- Beta ramp for alertness
- Heightened sensory awareness

### Before Sleep
**SLEEP-01** (30m) - Conscious sleep entry, lucid dreaming prep
- Theta descent 8→4 Hz
- Hypnagogic threshold access
- Natural sleep transition

### For Meditation Deepening
**META-01** (20m) - Self-inquiry, non-dual exploration
- Observer dissolution practice
- Spatial shifting of self-reference
- Advanced consciousness work

## Protocol Sequences

### Morning Activation
1. SENSE-01 (10m) - Wake up sensory system
2. PERF-01 (12m) - Lock in ready state

### Deep Work Session
1. PERF-01 (12m) - Pre-focus
2. FSP-01 (31m) - Extended lock
3. CREA-01 (15m) - Creative emergence

### Emotional Processing
1. FSP-01 temple (31m) - Establish stability
2. RECON-01 (25m) - Process memory
3. SLEEP-01 (30m) - Integrate and rest

### Evening Wind-Down
1. ARC-1TB (60m) - Release physical tension
2. SLEEP-01 (30m) - Transition to sleep

### Consciousness Exploration
1. FSP-01 temple (31m) - Build concentration
2. META-01 (20m) - Dissolve observer
3. SLEEP-01 (30m) - Drift into hypnagogia

## Safety Notes

⚠️ **High Intensity** (use with caution)
- ARC-1TB: Can trigger strong somatic release
- RECON-01: May surface difficult emotions

⚠️ **Not for Driving**
- All protocols impair alertness during/after
- Wait 15-30 minutes before operating vehicles

⚠️ **Headphones Required**
- Binaural beats only work with stereo headphones
- Use comfortable, over-ear headphones

⚠️ **Contraindications**
- Epilepsy: Avoid rhythmic protocols (ARC, CREA)
- Severe trauma: Use RECON-01 only with therapeutic support
- Psychosis history: Avoid META-01, use grounding protocols

## Parameter Tuning

If protocol feels:
- **Too intense**: Reduce level parameters in YAML by 10-20%
- **Too subtle**: Increase level parameters by 10-20%
- **Too fast**: Extend phase durations
- **Too slow**: Compress phase durations

## Render Commands

```bash
# Single protocol
cd protocol-lab/tools
python3 render_protocol.py ../protocols/PERF/specs/PERF-01_12m.yaml

# All protocols
python3 batch_render.py

# FSP with levels
cd ../protocols/FSP/audio
python3 render_fsp.py --level living --master
```

## File Locations

Rendered audio: `protocol-lab/protocols/{FAMILY}/renders/`
Specs: `protocol-lab/protocols/{FAMILY}/specs/`
Narration: `protocol-lab/protocols/{FAMILY}/narration/`
