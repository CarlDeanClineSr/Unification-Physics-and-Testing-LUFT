markdown name=docs/phase_alignment_metrics.md
# Phase Alignment Metrics (LUFT Resonance Atlas)

Purpose: Convert high‑level “non‑local / universal resonance” ideas into falsifiable, quantitative metrics on multi‑sensor time‑series.  
All metrics are computed with respect to a target narrowband frequency f0 (default 7468.779 Hz) or a set of derived lattice frequencies (harmonics / rationals).

---

## 1. Narrowband Extraction
We isolate a complex analytic narrowband component via:
1. Bandpass (IIR or FIR) around f0 ± BW/2
2. Hilbert transform -> analytic signal a(t) = A(t) e^{jφ(t)}
3. Instantaneous phase φ(t) = unwrap(angle(a(t)))

Config fields (config.yaml):
phase:
  enable: true
  f0: 7468.779
  bw_hz: 2.0
  detrend_phase: true

---

## 2. Pairwise Phase Locking Value (PLV)
PLV_{ij} = | (1/N) Σ_t exp(j(φ_i(t) - φ_j(t))) |

Interpretation:
- PLV ~1: Strong phase locking
- PLV ~0: Random relative phase

Acceptance example (adjust as data accumulates):
- Pass if PLV ≥ 0.6 over a 5–10 min block AND empirical null p ≤ 0.05.

Empirical Null:
- Time‑scramble each sensor independently (block shuffle) K times
- Recompute PLV for each permutation
- p = (count(null_plv >= real_plv)+1)/(K+1)

---

## 3. Circular Mean Phase & Drift
Mean relative phase: θ̄_{ij} = atan2( Σ sin Δφ, Σ cos Δφ )

Phase drift rate: slope (rad/s) of linear fit to unwrapped Δφ(t)

Acceptance:
- |drift_rate| ≤ drift_max_rad_s (config; e.g., 0.01 rad/s)
- Stable direction: circular variance ≤ var_max (e.g., 0.3)

---

## 4. Group Delay Approximation
Optionally approximate group delay τ via narrowband cross-spectrum:
τ ≈ - (1/ (2π)) * (Δ phase / Δf) across a small window around f0.

Used mainly to rule out simple cable length or latency artifacts if identical across physically separated sensors.

---

## 5. Phase Consistency Over Segments
Split record into M equal segments (e.g., 30 s):
Compute PLV per segment; evaluate variance.

Acceptance:
- Segment PLV median ≥ threshold (0.6)
- Inter-segment PLV coefficient of variation ≤ cv_max (e.g., 0.25)

---

## 6. Multi-Sensor Consensus Index
Given S sensors, average all pairwise PLVs:
Consensus = (2 / (S(S-1))) Σ_{i<j} PLV_{ij}

Acceptance:
- Consensus ≥ consensus_min (e.g., 0.55)
- Number of edges with PLV ≥ 0.6 ≥ fraction_min * total_edges (e.g., 0.7)

---

## 7. Harmonic / Rational Phase Alignment
For each expected lattice frequency f_k:
- Extract phase channel (narrowband_hilbert)
- Compute relative phase to base f0 component (e.g., φ_k − (k * φ_1) mod 2π)
- Evaluate clustering with Rayleigh’s test (optional future add).

Early acceptance (placeholder):
- Provide descriptive stats: mean Δφ_k, circular concentration κ_k.

---

## 8. Output Artifacts
CSV: phase_pairs.csv
Columns:
pair,sensor_i,sensor_j,plv,plv_p,mean_phase_deg,drift_rad_s,seg_median_plv,seg_plv_cv,consensus_placeholder

CSV: phase_consensus.csv
Columns:
n_sensors,global_consensus,edges_ge_0p6_frac,mean_plv,std_plv

---

## 9. Artifact Controls
- Time-scramble & circular shift permutations
- Frequency-shift test (mix by +Δf then re-extract)
- Dummy sensor / resistor substitution
- Clock de-discipline trial

All null variants should show PLV distribution overlapping near zero (or well below real).

---

## 10. Escalation Path
Phase 1: Implement PLV + empirical null
Phase 2: Add circular statistics tests (Rayleigh, Watson-Williams)
Phase 3: Add Bayesian hierarchical drift stability model

---

## 11. Interpretation Guidance
High PLV alone can arise from:
- Cross-talk
- Shared injected tone
- Leakage / alias

Therefore require simultaneous:
1. No explicit injection at f0 in either chain
2. Absent or insignificant in decoys
3. Stable across bias manipulations (magnonics field sweeps) OR shows controlled dependence (e.g., only present at resonance field)

---

Parameters are stored in config; every change should update prereg doc.

*Version: 0.1*
