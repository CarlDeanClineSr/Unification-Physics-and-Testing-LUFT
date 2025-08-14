markdown name=docs/harmonic_patterns.md
# Harmonic & Rational Pattern Configuration

Purpose: Encode expected lattice / harmonic / rational relationships to test enrichment beyond chance.

## Config Section Example
harmonics:
  enable: true
  max_n: 12
  include_subharmonics: true
  odd_only: false
  tolerance_hz: 0.4
  falloff_alpha: 1.0    # optional amplitude ~ 1/n^alpha (future)
  enrichment:
    permutations: 500
    freq_low: 2000
    freq_high: 20000

rationals:
  enable: true
  ratios: ["3/2", "5/3", "7/5", "9/4"]
  tolerance_hz: 0.5

## Metrics
1. Match Count: Number of expected harmonic bins with detected peak passing z ≥ z_min & q ≤ q_alpha.
2. Enrichment p-value: Probability random frequency sets (same size) yield ≥ observed matches.
3. Rational Ratio Hits: For each ratio p/q, test if a peak near (p/q)*f0 exists.

## Procedure
- Build list H = { n*f0 : n=1..max_n } (+ subharmonics f0/n if enabled)
- For each frequency h in H, find nearest detected peak; if |f_peak - h| ≤ tolerance_hz, count match.
- Randomization: For each permutation, draw |H| random frequencies Uniform(freq_low, freq_high), test matches against same peak list & tolerance; compute empirical p.

## Output CSV (harmonic_enrichment.csv)
columns:
f0,max_n,include_subharmonics,odd_only,tolerance_hz,n_expected,n_matches,empirical_p

## Output CSV (harmonic_matches.csv)
columns:
target_freq_hz,order,type,matched,peak_freq_hz,delta_hz,z,q

## Rational Output (rational_matches.csv)
columns:
ratio,p,q,target_freq_hz,matched,peak_freq_hz,delta_hz,z,q

## Interpretation
Low empirical_p (< 0.05 after correction) suggests non-random clustering at harmonic set.  
Ensure proper multiple comparison treatment if testing many patterns.

*Version 0.1*
