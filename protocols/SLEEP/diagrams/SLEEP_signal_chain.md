# SLEEP Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Binaural]
  L2 --> M[Mix Bus]
  P --> L3[Dissolve Cues]
  L3 --> M[Mix Bus]
  P --> L4[Reality Check Cues]
  L4 --> M[Mix Bus]
  P --> L5[Sub]
  L5 --> M[Mix Bus]
  P --> L6[Room Illusion]
  L6 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 3/3 specs |
| `binaural` | 3/3 specs |
| `dissolve_cues` | 1/3 specs |
| `reality_check_cues` | 1/3 specs |
| `sub` | 1/3 specs |
| `room_illusion` | 1/3 specs |

