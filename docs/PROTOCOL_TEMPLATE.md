# Protocol Documentation Template

Use this template to document each protocol. Copy and customize.

---

# [PROTOCOL-ID]: [Protocol Name]

## Overview

**Duration**: [X] minutes  
**Family**: [FAMILY] ([Family Full Name])  
**Intensity**: [Low/Medium/High]  
**Experience Level**: [Beginner/Intermediate/Advanced]

[One-sentence description of what this protocol does]

## What It Does

[Detailed description of the protocol's phases and progression]

### Phases
1. **[Phase 1 Name]** ([X] min): [What happens]
2. **[Phase 2 Name]** ([X] min): [What happens]
3. **[Phase 3 Name]** ([X] min): [What happens]

## Why It's Needed

[Problem this protocol solves, use cases, who benefits]

Use for:
- [Use case 1]
- [Use case 2]
- [Use case 3]

## How It Works

### Audio Architecture
- **Noise Bed**: [Type, level, drift parameters]
- **Binaural Beats**: [Frequencies, progression]
- **Special Layers**: [Any unique audio elements]
- **Signature**: [Frequency triad if applicable]

### Mechanism
[Explain the neurological/physiological/psychological mechanism]

1. [Step 1 of how it works]
2. [Step 2]
3. [Step 3]

## What to Expect

### During Protocol

**Phase 1 ([Name])**
- [Physical sensation 1]
- [Mental state 1]
- [What's normal]

**Phase 2 ([Name])**
- [Physical sensation 2]
- [Mental state 2]
- [What's normal]

**Phase 3 ([Name])**
- [Physical sensation 3]
- [Mental state 3]
- [What's normal]

### After Protocol
- [Effect 1] for [duration]
- [Effect 2]
- [Effect 3]

## Usage Guidelines

### Preparation
- [Preparation step 1]
- [Preparation step 2]
- [Position/setting requirements]

### Optimal Times
- **Morning**: [When/why]
- **Afternoon**: [When/why]
- **Evening**: [When/why or avoid]

### Frequency
- **Beginners**: [Recommendation]
- **Experienced**: [Recommendation]
- **Integration time**: [Time between sessions]

## Contraindications

**Avoid if**:
- [Condition 1]
- [Condition 2]

**Use with caution if**:
- [Condition 3]
- [Condition 4]

## Troubleshooting

**"[Common problem 1]"**
- [Solution]

**"[Common problem 2]"**
- [Solution]

**"[Common problem 3]"**
- [Solution]

## Sequences

### [Sequence Name 1]
[Protocol] → [Next step]

### [Sequence Name 2]
[Protocol] → [Next step] → [Final step]

## Scientific Basis

- **[Mechanism 1]**: [Evidence or explanation]
- **[Mechanism 2]**: [Evidence or explanation]

## Render Command

```bash
cd protocol-lab/tools
python3 render_protocol.py ../protocols/[FAMILY]/specs/[PROTOCOL-ID]_[X]m.yaml
```

## Files
- Spec: `protocols/[FAMILY]/specs/[PROTOCOL-ID]_[X]m.yaml`
- Narration: `protocols/[FAMILY]/narration/[PROTOCOL-ID]_coaching.md`

---

## Documentation Checklist

- [ ] Overview section complete
- [ ] All phases described
- [ ] Use cases clear
- [ ] Mechanism explained
- [ ] Expected experiences documented
- [ ] Safety information included
- [ ] Troubleshooting section
- [ ] Sequences provided
- [ ] Render command tested
