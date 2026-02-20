# FSP Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Binaural]
  L2 --> M[Mix Bus]
  P --> L3[Breath Cues]
  L3 --> M[Mix Bus]
  P --> L4[Return Cues]
  L4 --> M[Mix Bus]
  P --> L5[Letgo Swells]
  L5 --> M[Mix Bus]
  P --> L6[House Beat]
  L6 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 1/1 specs |
| `binaural` | 1/1 specs |
| `breath_cues` | 1/1 specs |
| `return_cues` | 1/1 specs |
| `letgo_swells` | 1/1 specs |
| `house_beat` | 1/1 specs |

