# SENSE Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Binaural]
  L2 --> M[Mix Bus]
  P --> L3[Shimmer]
  L3 --> M[Mix Bus]
  P --> L4[Sub Pulse]
  L4 --> M[Mix Bus]
  P --> L5[Heartbeat Cues]
  L5 --> M[Mix Bus]
  P --> L6[Spatial Sweep]
  L6 --> M[Mix Bus]
  P --> L7[Harmonic Pad]
  L7 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 3/3 specs |
| `binaural` | 3/3 specs |
| `shimmer` | 1/3 specs |
| `sub_pulse` | 1/3 specs |
| `heartbeat_cues` | 1/3 specs |
| `spatial_sweep` | 1/3 specs |
| `harmonic_pad` | 1/3 specs |

