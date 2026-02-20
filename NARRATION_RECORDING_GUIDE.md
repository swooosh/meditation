# Narration Recording Guide

## Overview
Each protocol now has a brief introduction for you to record with your voice. These intros explain the goal, mechanism, and process before the session begins.

## Structure
Each narration script has:
1. **Introduction** (30-60 seconds) - Record this first
2. **Phase guidance** (timestamped cues) - Record these at the specified times

## Introduction Format
Each intro covers:
- **Welcome** - Protocol name and duration
- **Goal** - What we're trying to achieve
- **Mechanism** - How the audio/technique works
- **Process** - Brief overview of phases
- **Transition** - "Let's begin"

## Recording Workflow

### 1. Record Introduction
Record the introduction section separately for each protocol. This will be mixed at the very beginning (after the three-tone signature).

### 2. Record Phase Cues
Record the timestamped guidance cues. These will be mixed at their specified times throughout the audio.

### 3. Mix with Audio
- Audio file: `{PROTOCOL-ID}_master.wav`
- Intro voice: Mix at 0:00 (after signature tones ~1 second)
- Phase cues: Mix at timestamps specified in script

## Voice Guidelines

**Tone by Family:**
- **ATTN** (FSP): Minimal, precise, calm
- **ARC**: Directive, commanding, physical
- **PERF**: Assertive, efficient, focused
- **RECON**: Gentle, invitational, warm
- **SLEEP**: Hypnotic, slow, soothing
- **CREA**: Permissive, exploratory, curious
- **SENSE**: Curious, phenomenological, precise
- **META**: Spacious, non-dual, contemplative
- **BODY**: Grounded, somatic, empowering
- **FLOW**: Smooth, absorbing, momentum-building
- **SOC**: Relational, inclusive, connective
- **PAIN**: Clinical, precise, empowering

## Example Recording Session

For CREA-02 (Divergent Thinking):

1. **Record intro** (~45 seconds):
   - "Welcome to Divergent Thinking, a 20-minute protocol..."
   - Save as: `CREA-02_intro.wav`

2. **Record phase cues** (20 cues total):
   - "Welcome to divergent thinking. Find your space."
   - "Notice what's here right now..."
   - etc.
   - Save as: `CREA-02_cues.wav` (with silence between cues)

3. **Mix**:
   - Base: `CREA-02_master.wav`
   - Add intro at 0:01 (after signature)
   - Add cues at timestamps

## Technical Specs

**Recording:**
- Sample rate: 44.1 kHz
- Bit depth: 16-bit or 24-bit
- Format: WAV (uncompressed)
- Mono or stereo (will be mixed to stereo)

**Levels:**
- Voice: -12 to -6 dB peak
- Should sit clearly above audio bed
- Use compression for consistency

## All Protocols with Intros

✅ CREA-02 (20m) - Divergent Thinking
✅ PERF-03 (5m) - Micro-Dose Focus
✅ ARC-2 (45m) - Gentle Activation
✅ ARC-3 (30m) - Peak Intensity
✅ FSP-02 (25m) - Distributed Attention
✅ FSP-03 (15m) - Rapid Context Switching
✅ RECON-03 (40m) - Shadow Integration
✅ SLEEP-03 (50m) - Deep Delta
✅ CREA-03 (25m) - Pattern Disruption
✅ SENSE-03 (20m) - Synesthetic Mapping
✅ META-02 (30m) - Witness Perspective
✅ META-03 (35m) - No-Self Inquiry
✅ BODY-02 (20m) - Power Embodiment
✅ FLOW-02 (25m) - Deep Immersion
✅ SOC-02 (30m) - Group Resonance
✅ PAIN-01 (15m) - Gate Control
✅ PAIN-02 (20m) - Sensation Reframe

## Next Steps

1. Review all intro scripts in `protocols/{FAMILY}/narration/`
2. Record intros in batches by family (for consistent voice)
3. Record phase cues
4. Mix with audio files
5. Test with users

All narration scripts are ready for recording!
