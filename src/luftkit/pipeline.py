import argparse, os
import numpy as np
from .config import load_config, expand_inputs, ensure_report_dir
from .io import read_wav, write_csv, load_sidecar
from .dsp import PsdParams, welch_psd, local_robust_z
from .stats import benjamini_hochberg, harmonic_targets, match_peaks_to_targets, rational_targets, match_rationals, enrichment_empirical, empirical_pvalue
from .decoy import time_scramble

def detect_peaks(f, z, alpha_mask, z_min):
    peaks_idx = np.where((alpha_mask) & (z >= z_min))[0]
    return f[peaks_idx], z[peaks_idx]

def within_band(f, low, high):
    mask = (f >= low) & (f <= high)
    return mask

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    config = load_config(args.config)
    report_dir = ensure_report_dir(config)

    wavs = expand_inputs(config.input)
    rows_peak=[]
    all_f = None
    global_peaks=[]
    global_z=[]
    global_q=[]
    for wpath in wavs:
        data, fs = read_wav(wpath)
        params = PsdParams(fs=fs, segment_s=config.welch.segment_s, overlap=config.welch.overlap, window=config.welch.window)
        f, p = welch_psd(data, params)
        band_mask = within_band(f, config.band.psd_low_hz, config.band.psd_high_hz)
        f2 = f[band_mask]; p2 = p[band_mask]
        z, power_db = local_robust_z(f2, p2, config.significance.local_baseline_window_hz, config.significance.exclude_bin_halfwidth_hz)
        # Convert z to p (approx Gaussian tail)
        from scipy.stats import norm
        pvals = 1 - norm.cdf(z)
        sig_mask = benjamini_hochberg(pvals, alpha=config.significance.alpha)
        peaks_f, peaks_z = detect_peaks(f2, z, sig_mask, config.significance.z_min)
        # Record
        for pf, pz in zip(peaks_f, peaks_z):
            # approximate q as pval (post BH pass)
            idx = np.where(f2==pf)[0][0]
            rows_peak.append([os.path.basename(wpath), pf, pz, pvals[idx]])
        # Aggregate
        global_peaks.extend(peaks_f)
        global_z.extend(peaks_z)
        global_q.extend([pvals[np.where(f2==pf)[0][0]] for pf in peaks_f])
        all_f = f2  # reuse

    write_csv(os.path.join(report_dir,"peaks.csv"), rows_peak,
              ["file","freq_hz","z","p_approx"])

    # Harmonic enrichment
    if config.harmonics.enable:
        targets = harmonic_targets(config.band.target_hz, config.harmonics.max_n,
                                   config.harmonics.include_subharmonics,
                                   config.harmonics.odd_only)
        h_rows, matches = match_peaks_to_targets(np.array(global_peaks), np.array(global_z),
                                                 np.array(global_q), targets,
                                                 config.harmonics.tolerance_hz,
                                                 config.significance.z_min,
                                                 config.significance.alpha)
        write_csv(os.path.join(report_dir,"harmonic_matches.csv"),
                  h_rows, ["target_freq_hz","order","type","matched","peak_freq_hz","delta_hz","z","q"])
        null_counts=[]
        if config.harmonics.enrichment.enable:
            null_counts = enrichment_empirical(global_peaks, global_z, global_q,
                                               len(targets),
                                               config.harmonics.enrichment.freq_low,
                                               config.harmonics.enrichment.freq_high,
                                               config.harmonics.tolerance_hz,
                                               config.significance.z_min,
                                               config.significance.alpha,
                                               permutations=config.harmonics.enrichment.permutations)
            empirical_p = empirical_pvalue(matches, null_counts)
        else:
            empirical_p = ""
        write_csv(os.path.join(report_dir,"harmonic_enrichment.csv"),
                  [[config.band.target_hz, len(targets), matches, empirical_p]],
                  ["f0","n_targets","n_matches","empirical_p"])

    # Rational patterns
    if config.rationals.enable:
        r_targets = rational_targets(config.band.target_hz, config.rationals.ratios)
        r_rows = match_rationals(np.array(global_peaks), np.array(global_z), np.array(global_q),
                                 r_targets, config.rationals.tolerance_hz,
                                 config.significance.z_min, config.significance.alpha)
        write_csv(os.path.join(report_dir,"rational_matches.csv"),
                  r_rows, ["ratio","p","q","target_freq_hz","matched","peak_freq_hz","delta_hz","z","q"])

    print("Done. Report dir:", report_dir)

if __name__ == "__main__":
    main()
