#!/usr/bin/env python3
"""Agent implementations for protocol workflow.

This script uses the use_subagent tool to delegate protocol implementation
tasks to specialized AI agents.
"""
import json
import os
import sys

# Protocol definitions with implementation requirements
PROTOCOL_SPECS = {
    'CREA-02': {
        'name': 'Divergent Thinking',
        'duration_m': 20,
        'family': 'CREA',
        'requirements': {
            'dsp_modules': ['gamma_bursts', 'multi_rhythm'],
            'audio_layers': ['gamma_overlay', 'polyrhythm'],
            'narration_style': 'permissive_exploratory'
        }
    },
    'PERF-03': {
        'name': 'Micro-Dose Focus',
        'duration_m': 5,
        'family': 'PERF',
        'requirements': {
            'dsp_modules': ['rapid_ramp'],
            'audio_layers': ['fast_binaural_ramp'],
            'narration_style': 'minimal_setup'
        }
    },
    # Add all 17 remaining protocols...
}

def create_yaml_spec_task(protocol_id: str) -> dict:
    """Generate task for YAML spec creation."""
    spec = PROTOCOL_SPECS[protocol_id]
    
    return {
        'agent': 'spec_designer',
        'task': f"""Create complete YAML specification for {protocol_id}: {spec['name']}

Family: {spec['family']}
Duration: {spec['duration_m']} minutes

Requirements:
- Audio layers: {', '.join(spec['requirements']['audio_layers'])}
- Follow {spec['family']} family identity from FAMILY_TAXONOMY.md
- Include all phases with start/end times
- Define all audio layer parameters
- Set appropriate binaural frequencies
- Include signature marker settings

Output: protocol-lab/protocols/{spec['family']}/specs/{protocol_id}_{spec['duration_m']}m.yaml
""",
        'context': f"See FAMILY_TAXONOMY.md for {spec['family']} family identity"
    }

def create_dsp_module_task(protocol_id: str) -> dict:
    """Generate task for DSP module implementation."""
    spec = PROTOCOL_SPECS[protocol_id]
    
    return {
        'agent': 'dsp_engineer',
        'task': f"""Implement DSP modules for {protocol_id}

Required modules: {', '.join(spec['requirements']['dsp_modules'])}

For each module:
1. Create Python file in protocol-lab/engine/dsp/
2. Follow existing module patterns (see noise.py, drums.py)
3. Use pure Python, no external dependencies
4. Include docstrings
5. Keep functions minimal and focused

Example structure:
```python
def gamma_burst(sr: int, dur_s: float, freq_hz: float) -> List[float]:
    \"\"\"Generate gamma frequency burst (40 Hz).\"\"\"
    # Implementation
    return samples
```

Output: protocol-lab/engine/dsp/{module_name}.py for each module
""",
        'context': 'See existing DSP modules in engine/dsp/ for patterns'
    }

def create_renderer_extension_task(protocol_id: str) -> dict:
    """Generate task for renderer extension."""
    spec = PROTOCOL_SPECS[protocol_id]
    
    return {
        'agent': 'renderer_builder',
        'task': f"""Extend universal renderer for {protocol_id}

Add support for these audio layer types: {', '.join(spec['requirements']['audio_layers'])}

In protocol-lab/tools/render_protocol.py:
1. Add new elif blocks in render_protocol() function
2. Handle layer['type'] == '{spec['requirements']['audio_layers'][0]}'
3. Import required DSP modules
4. Mix into stereo buffers (l, r)
5. Follow existing layer patterns

Keep implementation minimal - just enough to render the layer.
""",
        'context': 'See render_protocol.py for existing layer implementations'
    }

def create_narration_task(protocol_id: str) -> dict:
    """Generate task for narration writing."""
    spec = PROTOCOL_SPECS[protocol_id]
    
    return {
        'agent': 'narration_writer',
        'task': f"""Write narration script for {protocol_id}: {spec['name']}

Duration: {spec['duration_m']} minutes
Style: {spec['requirements']['narration_style']}
Family: {spec['family']}

Follow {spec['family']} narration tone from FAMILY_TAXONOMY.md

Structure:
- Markdown format with ## Phase headers
- Timestamps in **MM:SS** format
- Brief, directive statements
- Match family voice (see FAMILY_TAXONOMY.md)

Output: protocol-lab/protocols/{spec['family']}/narration/{protocol_id}_coaching.md
""",
        'context': f"See FAMILY_TAXONOMY.md for {spec['family']} narration tone"
    }

def main():
    """Generate all agent tasks."""
    print("Multi-Agent Protocol Implementation Tasks")
    print("=" * 60)
    
    for protocol_id in PROTOCOL_SPECS.keys():
        print(f"\n{protocol_id}:")
        print("  1. YAML Spec")
        print("  2. DSP Modules")
        print("  3. Renderer Extension")
        print("  4. Narration")
    
    print("\n" + "=" * 60)
    print("To execute, use the use_subagent tool with these task definitions")
    print("Example: use_subagent with create_yaml_spec_task('CREA-02')")

if __name__ == '__main__':
    main()
