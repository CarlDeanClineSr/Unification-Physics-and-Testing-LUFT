import argparse, os
from .config import load_config, ensure_report_dir
from .domain.magnonics import analyze_magnonics_dir, load_magnonics_dir
from .io import write_csv
from .phase import pairwise_phase_metrics

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--magnonics_dir", required=True)
    args = ap.parse_args()
    config = load_config(args.config)
    report_dir = ensure_report_dir(config)

    peaks = analyze_magnonics_dir(args.magnonics_dir, config)
    write_csv(os.path.join(report_dir,"magnonics_peaks.csv"),
              peaks, ["sensor","freq_hz","z","p_approx"])

    # Phase if multi-sensor
    traces, fs, meta = load_magnonics_dir(args.magnonics_dir)
    if config.phase.enable and len(traces) >= 2:
        rows, consensus = pairwise_phase_metrics(traces, fs, config.phase.f0,
                                                 config.phase.bw_hz,
                                                 segment_s=config.phase.segment_s,
                                                 plv_permutations=config.phase.plv_permutations)
        write_csv(os.path.join(report_dir,"magnonics_phase_pairs.csv"),
                  rows, ["pair","sensor_i","sensor_j","plv","plv_p","mean_phase_deg","drift_rad_s","seg_median_plv","seg_plv_cv"])
        write_csv(os.path.join(report_dir,"magnonics_phase_consensus.csv"),
                  [[len(traces), consensus]], ["n_sensors","consensus_plv"])
    print("Magnonics analysis complete. Dir:", report_dir)

if __name__ == "__main__":
    main()
