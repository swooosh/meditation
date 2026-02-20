# Multi-Agent Protocol Implementation Guide

## Overview

This workflow uses specialized AI agents to implement the remaining 17 protocols. Each protocol goes through 4 stages with different agents.

## Agents

### 1. Spec Designer Agent
**Role**: Create complete YAML specifications
**Input**: Protocol requirements from FAMILY_TAXONOMY.md
**Output**: Complete YAML spec file
**Skills**: YAML structure, audio layer design, phase planning

### 2. DSP Engineer Agent  
**Role**: Implement required DSP modules
**Input**: Audio layer requirements from YAML spec
**Output**: Python modules in engine/dsp/
**Skills**: Audio synthesis, signal processing, Python

### 3. Renderer Builder Agent
**Role**: Extend universal renderer
**Input**: New audio layer types needed
**Output**: Updated render_protocol.py
**Skills**: Integration, audio mixing, Python

### 4. Narration Writer Agent
**Role**: Write timestamped narration scripts
**Input**: Protocol phases, family narration tone
**Output**: Markdown narration file
**Skills**: Writing, timing, family voice matching

## Execution Workflow

### Automated Execution (Recommended)

```bash
cd protocol-lab/tools
python3 workflow_orchestrator.py --execute
```

This will:
1. Process all 17 protocols in priority order
2. Execute tasks respecting dependencies
3. Validate each protocol after completion

### Manual Execution (Step-by-Step)

For each protocol, execute these tasks in order:

#### Task 1: Create YAML Spec
```
Agent: Spec Designer
Action: Create complete YAML specification
File: protocols/{FAMILY}/specs/{PROTOCOL_ID}_{DURATION}m.yaml
```

#### Task 2: Implement DSP Modules
```
Agent: DSP Engineer  
Action: Create required DSP modules
Files: engine/dsp/{module_name}.py
```

#### Task 3: Extend Renderer
```
Agent: Renderer Builder
Action: Add audio layer support
File: tools/render_protocol.py (update)
```

#### Task 4: Write Narration
```
Agent: Narration Writer
Action: Create narration script
File: protocols/{FAMILY}/narration/{PROTOCOL_ID}_coaching.md
```

#### Task 5: Validate
```
Agent: Validator
Action: Test render and check QC metrics
Command: python3 render_protocol.py ../protocols/{FAMILY}/specs/{PROTOCOL_ID}.yaml
```

## Protocol Implementation Order

### Priority 1-5 (High Value)
1. CREA-02 - Divergent Thinking (20m)
2. PERF-03 - Micro-Dose Focus (5m)
3. FSP-02 - Distributed Attention (25m)
4. FSP-03 - Rapid Context Switching (15m)
5. ARC-2 - Gentle Activation (45m)

### Priority 6-10 (Medium Value)
6. ARC-3 - Extended Plateau (90m)
7. RECON-03 - Anger Reframe (20m)
8. SLEEP-03 - Insomnia Protocol (60m)
9. CREA-03 - Incubation (45m)
10. SENSE-03 - Synesthesia Induction (25m)

### Priority 11-17 (Specialized)
11. META-02 - Identity Redesign (30m)
12. META-03 - Ego Softening (40m)
13. BODY-02 - Controlled Aggression Release (25m)
14. FLOW-02 - Temporal Expansion (25m)
15. SOC-02 - Group Entrainment (30m)
16. PAIN-01 - Gate Control (20m)
17. PAIN-02 - Dissociative Distance (30m)

## Using Subagents

### Example: Implement CREA-02

**Step 1: Create YAML Spec**
```
Use subagent: spec_designer
Task: Create complete YAML specification for CREA-02: Divergent Thinking

Family: CREA
Duration: 20 minutes

Requirements:
- Audio layers: gamma_overlay, polyrhythm
- Follow CREA family identity from FAMILY_TAXONOMY.md
- Include 3 phases: Baseline, Diverge, Integrate
- Gamma bursts (40 Hz) in phase 2-3
- Multiple simultaneous irregular rhythms
- Beta range binaural (13-14 Hz)

Output: protocol-lab/protocols/CREA/specs/CREA-02_20m.yaml
```

**Step 2: Implement DSP Modules**
```
Use subagent: dsp_engineer
Task: Implement DSP modules for CREA-02

Required modules: gamma_bursts, multi_rhythm

Create protocol-lab/engine/dsp/gamma.py with:
- gamma_burst(sr, dur_s, freq_hz) -> List[float]
- Generate 40 Hz oscillation with envelope

Create protocol-lab/engine/dsp/polyrhythm.py with:
- multi_rhythm(sr, dur_s, rates, levels) -> Tuple[List[float], List[float]]
- Multiple simultaneous irregular rhythms
```

**Step 3: Extend Renderer**
```
Use subagent: renderer_builder
Task: Extend universal renderer for CREA-02

In protocol-lab/tools/render_protocol.py, add:

elif layer['type'] == 'gamma_overlay':
    from engine.dsp.gamma import gamma_burst
    p = layer['params']
    if p.get('phase2_enabled'):
        phase = spec['phases'][1]
        # Add gamma bursts at intervals
        
elif layer['type'] == 'polyrhythm':
    from engine.dsp.polyrhythm import multi_rhythm
    # Mix multiple rhythms
```

**Step 4: Write Narration**
```
Use subagent: narration_writer
Task: Write narration script for CREA-02: Divergent Thinking

Duration: 20 minutes
Style: permissive_exploratory
Family: CREA

Output: protocol-lab/protocols/CREA/narration/CREA-02_coaching.md

Example structure:
## Phase 1: Baseline (0:00 - 5:00)
**00:00**
Notice your habitual thought patterns.

**02:00**
The rhythm is regular. Predictable.
```

## Validation

After implementing each protocol:

```bash
cd protocol-lab/tools
python3 render_protocol.py ../protocols/CREA/specs/CREA-02_20m.yaml --out_dir ../protocols/CREA/renders

# Check output
ls -lh ../protocols/CREA/renders/CREA-02_master.wav

# Verify QC metrics in output
```

## Batch Processing

To implement all protocols:

```bash
# Dry run (shows execution plan)
python3 workflow_orchestrator.py

# Execute all
python3 workflow_orchestrator.py --execute

# Execute single protocol
python3 workflow_orchestrator.py --execute --protocol CREA-02
```

## Success Criteria

For each protocol:
- ✅ YAML spec exists and is valid
- ✅ All required DSP modules implemented
- ✅ Renderer can process all audio layers
- ✅ Narration script complete with timestamps
- ✅ Protocol renders without errors
- ✅ QC metrics within acceptable ranges (peak < 1.0, RMS 0.01-0.10)

## Troubleshooting

**"No module named 'engine.dsp.gamma'"**
→ DSP module not implemented yet, run DSP Engineer agent

**"Unknown audio layer type 'gamma_overlay'"**
→ Renderer not extended yet, run Renderer Builder agent

**YAML parse error**
→ Spec Designer agent needs to fix YAML syntax

**Render succeeds but audio is silent**
→ Check level parameters in YAML, may be too low
