import os
import gzip
import numpy as np
import scipy.signal
import scipy.fftpack
import matplotlib.pyplot as plt
import csv
from datetime import datetime

LUFT_TARGET_FREQS = [7468, 1420000000]  # 7,468 Hz and 1.42 GHz (hydrogen line)
DATA_DIR = "data"
DASHBOARD_MD = "LUFT_Findings.md"
DASHBOARD_CSV = "LUFT_Findings.csv"

def analyze_signal(data, fs, file_name):
    # Perform FFT
    N = len(data)
    yf = np.abs(np.fft.rfft(data))
    xf = np.fft.rfftfreq(N, 1/fs)
    # Find LUFT anomalies
    findings = []
    for f in LUFT_TARGET_FREQS:
        idx = (np.abs(xf - f)).argmin()
        amplitude = yf[idx]
        if amplitude > np.mean(yf) + 4 * np.std(yf):
            findings.append((f, amplitude))
    return findings, xf, yf

def process_file(file_path):
    # Try to read .gz or .csv or .txt as raw signal data
    try:
        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rb") as f:
                raw = f.read()
            data = np.frombuffer(raw, dtype=np.float32)
            fs = 44100  # Placeholder: replace with metadata, if available
        elif file_path.endswith(".csv"):
            data = np.loadtxt(file_path, delimiter=",")
            fs = 44100  # Placeholder
        elif file_path.endswith(".txt"):
            data = np.loadtxt(file_path)
            fs = 44100  # Placeholder
        else:
            return None
        findings, xf, yf = analyze_signal(data, fs, os.path.basename(file_path))
        return findings
    except Exception as e:
        return None

def main():
    all_results = []
    for root, dirs, files in os.walk(DATA_DIR):
        for fname in files:
            if fname.endswith(('.gz', '.csv', '.txt')):
                fpath = os.path.join(root, fname)
                findings = process_file(fpath)
                if findings:
                    for freq, amp in findings:
                        all_results.append({
                            'file': fname,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'anomaly_frequency': freq,
                            'amplitude': amp,
                            'notes': f"LUFT anomaly at {freq} Hz"
                        })
    # Write Markdown dashboard
    with open(DASHBOARD_MD, 'w') as md:
        md.write("# LUFT Anomaly Scan Results\n\n")
        md.write("| File | Date | Anomaly Frequency (Hz) | Amplitude | Notes |\n")
        md.write("|------|------|-----------------------|-----------|-------|\n")
        for row in all_results:
            md.write(f"| {row['file']} | {row['date']} | {row['anomaly_frequency']} | {row['amplitude']:.2f} | {row['notes']} |\n")
    # Write CSV
    with open(DASHBOARD_CSV, 'w', newline='') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print("Scan complete. Results written to LUFT_Findings.md and LUFT_Findings.csv.")

if __name__ == "__main__":
    main()
