# CREA Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Irregular Pulses]
  L2 --> M[Mix Bus]
  P --> L3[Gamma Overlay]
  L3 --> M[Mix Bus]
  P --> L4[Binaural]
  L4 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 3/3 specs |
| `irregular_pulses` | 3/3 specs |
| `gamma_overlay` | 2/3 specs |
| `binaural` | 1/3 specs |

