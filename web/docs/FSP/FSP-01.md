# FSP-01: Focused State Protocol

## Overview

**Duration**: 31 minutes  
**Family**: ATTN (Attention Architecture)  
**Intensity**: Medium  
**Experience Level**: Beginner to Advanced

Gateway-inspired protocol for building narrow attentional focus and controlled state shifts. The gold standard for concentration training.

## What It Does

FSP-01 systematically trains your attention through five distinct phases:

1. **Downshift** (7 min): Activates parasympathetic nervous system, reduces baseline arousal
2. **Body Scan** (5 min): Grounds awareness in somatic sensations
3. **Attentional Lock** (8 min): Narrows focus to single point with binaural support
4. **State Shift** (8 min): Controlled depth with descending binaural frequencies
5. **Reintegration** (3 min): Gentle return to baseline alertness

## Why It's Needed

Modern life fragments attention. FSP-01 rebuilds the capacity for sustained, narrow focus—essential for:
- Deep work and complex problem-solving
- Meditation practice
- Flow state access
- Cognitive performance under pressure
- Attention deficit management

## How It Works

### Audio Architecture
- **Noise Bed**: Brown/pink noise with slow stereo drift (0.008-0.014 Hz)
- **Binaural Beats**: 
  - Phase 3: Constant 9-12 Hz (alpha, depending on level)
  - Phase 4: Descending 8.5→6 Hz (alpha to theta)
  - Phase 5: Ascending 6→10 Hz (return to alpha)
- **Cues**: Optional return bells (Phase 3), let-go swells (Phase 4)

### Neurological Mechanism
1. **Parasympathetic activation** reduces arousal, creating stable baseline
2. **Somatic grounding** anchors awareness in body, preventing mind-wandering
3. **Binaural entrainment** guides brainwaves into focused alpha state
4. **Theta dip** allows brief state shift without losing stability
5. **Alpha return** brings you back alert and focused

## What to Expect

### During Protocol

**Phase 1 (Downshift)**
- Breathing slows naturally
- Body feels heavier
- Mental chatter reduces
- Mild drowsiness is normal

**Phase 2 (Body Scan)**
- Increased body awareness
- Tingling or warmth in scanned areas
- Sense of "mapping" your body
- Occasional muscle twitches

**Phase 3 (Attentional Lock)**
- Focus becomes effortless
- Time perception shifts (may feel faster)
- Distractions fade to background
- Sense of "locking in"

**Phase 4 (State Shift)**
- Mild dissociation or spaciness
- Boundaries may feel softer
- Hypnagogic imagery possible
- Sense of depth or descent

**Phase 5 (Reintegration)**
- Gradual return of alertness
- Maintained focus quality
- Calm but awake
- Ready for action

### After Protocol
- Enhanced concentration for 2-4 hours
- Reduced mental fatigue
- Improved task switching
- Sense of mental clarity

## Levels

### Living (Default)
- Balanced, warm soundfield
- Moderate binaural entrainment
- Return cues every 75 seconds (Phase 3)
- Let-go swells every 2 minutes (Phase 4)
- **Best for**: Daily use, general focus

### Temple
- Minimal cues, deeper stillness
- Reduced drift and binaural levels
- No return cues or swells
- **Best for**: Meditation, spiritual practice

### Focus
- Brighter, more structured
- Stronger binaural entrainment
- Frequent return cues (every 45s)
- **Best for**: High-stakes work, performance

## Usage Guidelines

### Preparation
- Sit upright or lie down comfortably
- Use over-ear headphones
- Dim lighting
- No interruptions for 35 minutes
- Empty bladder

### Optimal Times
- Morning: After waking, before work
- Midday: Before important meeting or deep work session
- Evening: Before creative work (not before sleep)

### Frequency
- Daily: Safe for daily use
- Multiple times: Allow 4+ hours between sessions
- Long-term: Builds cumulative attentional capacity

## Contraindications

**Avoid if**:
- Severe anxiety (may increase during Phase 4)
- Epilepsy (binaural beats contraindicated)
- Acute psychosis

**Use with caution if**:
- ADHD (start with Temple level, shorter sessions)
- Trauma history (may surface memories in Phase 4)

## Troubleshooting

**"I fell asleep"**
- Use Focus level
- Sit upright instead of lying down
- Do earlier in day

**"I couldn't focus"**
- Normal for first 3-5 sessions
- Use Living level with return cues
- Don't judge wandering mind, just return

**"Phase 4 felt scary"**
- Use Temple level (gentler descent)
- Remember: you're always in control
- Can open eyes anytime

**"Nothing happened"**
- Effects are subtle, not dramatic
- Track over multiple sessions
- Notice work performance after, not during

## Sequences

### Before Deep Work
FSP-01 (Living) → 4 hours focused work

### Extended Focus Training
FSP-01 (Temple) → 30 min break → FSP-01 (Focus)

### Meditation Deepening
FSP-01 (Temple) → META-01 (Observer Dissolution)

### Creative Session
FSP-01 (Focus) → CREA-01 (Pattern Disruption)

## Scientific Basis

- **Binaural beats**: Entrainment effects documented in alpha/theta ranges
- **Parasympathetic activation**: 4-6 breath pattern activates vagal tone
- **Attention training**: Repeated return-to-focus builds attentional control
- **State-dependent learning**: Focused state improves encoding

## Render Command

```bash
cd protocol-lab/protocols/FSP/audio
python3 render_fsp.py --level living --master
```

## Files
- Spec: `protocols/FSP/specs/FSP-01_31m.yaml`
- Narration: `protocols/FSP/narration/FSP-01_coaching.md`
- Renderer: `protocols/FSP/audio/render_fsp.py`
