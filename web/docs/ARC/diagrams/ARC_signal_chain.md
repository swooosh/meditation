# ARC Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Tribal Drums]
  L1 --> M[Mix Bus]
  P --> L2[Sub]
  L2 --> M[Mix Bus]
  P --> L3[Room Illusion]
  L3 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `tribal_drums` | 3/3 specs |
| `sub` | 3/3 specs |
| `room_illusion` | 3/3 specs |

