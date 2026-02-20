# What the Workflow Orchestrator Actually Does

## Current Behavior

The `workflow_orchestrator.py` script is a **simulation/planning tool**, not an execution engine. When you run it with `--execute`, it:

1. ✅ Shows you the 102 tasks needed
2. ✅ Prints what each agent would do
3. ✅ Respects task dependencies
4. ❌ Does NOT actually create files
5. ❌ Does NOT implement protocols

## What You're Seeing

```
Executing: CREA-02 / spec_designer / complete_yaml_spec
  [SpecDesigner] Creating YAML spec for CREA-02
```

This is just a **log message**, not actual work being done.

## How to Actually Implement Protocols

You have **three options**:

### Option 1: Manual Implementation (Recommended)

Use the workflow as a guide, implement manually:

```bash
# See the plan
cd protocol-lab/tools
python3 workflow_orchestrator.py

# Then manually create each protocol following AGENT_WORKFLOW.md
```

**For each protocol**:
1. Create YAML spec (copy from similar protocol)
2. Implement any new DSP modules needed
3. Extend renderer if needed
4. Write narration script
5. Test render

### Option 2: Use Subagents (AI-Assisted)

Delegate each task to a specialized AI agent:

**Example for CREA-02**:

```
Task 1: Create YAML Spec
→ Ask AI: "Create complete YAML specification for CREA-02: Divergent Thinking
   - 20 minutes duration
   - CREA family (see FAMILY_TAXONOMY.md)
   - Gamma bursts (40 Hz) in phases 2-3
   - Multiple irregular rhythms
   - Output: protocols/CREA/specs/CREA-02_20m.yaml"

Task 2: Implement DSP Modules
→ Ask AI: "Implement gamma_burst() function in engine/dsp/gamma.py
   - Generate 40 Hz oscillation with envelope
   - Return List[float] of samples"

Task 3: Extend Renderer
→ Ask AI: "Add gamma_overlay layer support to tools/render_protocol.py"

Task 4: Write Narration
→ Ask AI: "Write 20-minute narration for CREA-02 in CREA family voice"

Task 5: Test
→ Run: python3 render_protocol.py ../protocols/CREA/specs/CREA-02_20m.yaml
```

### Option 3: Implement Priority Protocols Only

Focus on the 5 highest-value protocols:

1. **CREA-02** - Divergent Thinking (20m)
2. **PERF-03** - Micro-Dose Focus (5m)
3. **FSP-02** - Distributed Attention (25m)
4. **FSP-03** - Rapid Context Switching (15m)
5. **ARC-2** - Gentle Activation (45m)

## Practical Next Steps

### Immediate Action

**If you want to use protocols NOW**:
```bash
# You already have 15 working protocols!
cd protocol-lab/tools
python3 batch_render.py  # Renders all existing protocols
```

**If you want to implement new protocols**:
1. Pick ONE protocol (start with PERF-03 - simplest)
2. Follow the manual implementation guide below
3. Test it works
4. Repeat for others

## Manual Implementation Guide: PERF-03

Let's implement the simplest new protocol as an example:

### Step 1: Create YAML Spec

```bash
cd protocol-lab/protocols/PERF/specs
```

Create `PERF-03_5m.yaml`:
```yaml
id: PERF-03
title: "Micro-Dose Focus — Quick Reset"
family: PERF
version: 1.0
duration_s: 300

render:
  sr: 44100
  seed: 2003
  peak_norm: true

identity:
  signature_marker:
    enabled: true
    freqs_hz: [220, 293, 440]
    dur_ms_each: 150
    level: 0.010

phases:
  - name: "Rapid Ramp"
    start_s: 0
    end_s: 300

audio_layers:
  - type: "noise_bed"
    params:
      noise: "pink"
      level: 0.058
      drift_hz: 0.015
      drift_depth: 0.12
  - type: "binaural"
    params:
      phase1_start: 10.0
      phase1_end: 14.0
      carrier_hz: 200.0
      level: 0.018
```

### Step 2: Test Render

```bash
cd protocol-lab/tools
python3 render_protocol.py ../protocols/PERF/specs/PERF-03_5m.yaml --out_dir ../protocols/PERF/renders
```

If it works, you're done! If not, debug the YAML.

### Step 3: Write Narration

Create `protocols/PERF/narration/PERF-03_coaching.md`:
```markdown
# PERF-03 Narration — Micro-Dose Focus

## Phase 1: Rapid Ramp (0:00 - 5:00)

**00:00**
Quick reset. Sit upright. Eyes closed.

**01:00**
Narrow your attention. Single point.

**02:30**
Feel the focus sharpening.

**04:00**
Lock in. You're ready.

**04:45**
Open your eyes when ready.
```

Done! You've implemented PERF-03.

## Summary

**The workflow orchestrator is a planning tool, not an execution engine.**

**To actually implement protocols, you need to**:
1. Manually create YAML specs
2. Manually implement DSP modules (if needed)
3. Manually extend renderer (if needed)
4. Manually write narration
5. Test renders

**OR**

Use AI assistance to generate each component, then test.

**Current Status**:
- ✅ 15 protocols fully working
- ✅ 17 protocols planned
- ⏳ Implementation requires manual work or AI delegation

**Recommendation**: Start with PERF-03 (simplest), follow the guide above, then repeat for others.
