# BODY Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Sub Power]
  L2 --> M[Mix Bus]
  P --> L3[Body Cues]
  L3 --> M[Mix Bus]
  P --> L4[Room Illusion]
  L4 --> M[Mix Bus]
  P --> L5[Tribal Drums]
  L5 --> M[Mix Bus]
  P --> L6[Sub]
  L6 --> M[Mix Bus]
  P --> L7[Pulse Cues]
  L7 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 1/2 specs |
| `sub_power` | 1/2 specs |
| `body_cues` | 1/2 specs |
| `room_illusion` | 1/2 specs |
| `tribal_drums` | 1/2 specs |
| `sub` | 1/2 specs |
| `pulse_cues` | 1/2 specs |

