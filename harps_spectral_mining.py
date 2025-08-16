#!/usr/bin/env python3
"""
HARPS Spectral Mining Script for LUFT/UFT Frequency Detection

This modular script performs spectral analysis on HARPS public spectra (or simulated data)
to detect LUFT/UFT frequencies, particularly around 7,468 Hz ± 10 Hz and subharmonics.

Author: Carl Dean Cline Sr.
Created for Reality-based Space and its functionality repository
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from scipy import signal
from scipy.stats import norm
from astropy.io import fits
import os
import datetime
from pathlib import Path
import argparse


class HARPSMiner:
    """Main class for HARPS spectral mining and LUFT/UFT frequency detection."""
    
    def __init__(self, config_path=None):
        """Initialize the HARPS miner with configuration."""
        self.config = self.load_config(config_path)
        self.results = {}
        self.peaks_data = []
        self.summary = {}
        
    def load_config(self, config_path):
        """Load configuration from YAML file or use defaults."""
        default_config = {
            'target_frequency': 7468.0,  # Hz - main LUFT frequency
            'frequency_tolerance': 10.0,  # Hz - ±10 Hz search window
            'sample_rate': 48000,  # Hz - assumed sample rate for simulated data
            'fft_window_size': 8192,
            'overlap': 0.5,
            'harmonic_orders': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'subharmonic_orders': [0.5, 0.25, 0.125],
            'significance_threshold': 6.0,  # Z-score threshold
            'output_dir': 'harps_mining_results',
            'plot_frequency_range': [7400, 7600],  # Hz range for detailed plots
            'instrument_metadata': {
                'name': 'HARPS',
                'location': 'La Silla Observatory',
                'wavelength_range': '378-691 nm',
                'resolution': '~115,000'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
                
        return default_config
    
    def generate_simulated_harps_data(self, duration=60, noise_level=0.1):
        """Generate simulated HARPS spectral data for demonstration."""
        print("Generating simulated HARPS spectral data...")
        
        fs = self.config['sample_rate']
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        
        # Base signal with noise
        signal_data = np.random.normal(0, noise_level, len(t))
        
        # Add LUFT target frequency with harmonics
        target_freq = self.config['target_frequency']
        
        # Main frequency peak
        signal_data += 0.05 * np.sin(2 * np.pi * target_freq * t)
        
        # Add harmonics with decreasing amplitude
        for order in self.config['harmonic_orders'][:5]:
            amplitude = 0.02 / order  # Decreasing amplitude
            signal_data += amplitude * np.sin(2 * np.pi * target_freq * order * t)
            
        # Add subharmonics
        for order in self.config['subharmonic_orders']:
            amplitude = 0.01 / (1/order)
            signal_data += amplitude * np.sin(2 * np.pi * target_freq * order * t)
            
        # Add some random peaks for anomaly detection
        anomaly_freqs = [3234.5, 5671.2, 9876.3, 12345.6]
        for freq in anomaly_freqs:
            if freq < fs/2:  # Nyquist limit
                signal_data += np.random.uniform(0.005, 0.02) * np.sin(2 * np.pi * freq * t)
        
        return signal_data, fs, t
    
    def load_harps_fits(self, fits_path):
        """Load HARPS FITS file (placeholder for real data loading)."""
        try:
            with fits.open(fits_path) as hdul:
                # Placeholder - adapt based on actual HARPS FITS structure
                data = hdul[1].data  # Assuming data is in first extension
                header = hdul[0].header
                return data, header
        except Exception as e:
            print(f"Error loading FITS file {fits_path}: {e}")
            return None, None
    
    def perform_fft_analysis(self, signal_data, fs):
        """Perform FFT analysis on the signal data."""
        print("Performing FFT analysis...")
        
        # Use Welch's method for better frequency resolution
        window_size = self.config['fft_window_size']
        overlap_samples = int(window_size * self.config['overlap'])
        
        frequencies, power_spectrum = signal.welch(
            signal_data, 
            fs=fs, 
            nperseg=window_size,
            noverlap=overlap_samples,
            window='hann'
        )
        
        # Convert to dB
        power_db = 10 * np.log10(power_spectrum + 1e-12)  # Add small value to avoid log(0)
        
        return frequencies, power_spectrum, power_db
    
    def detect_peaks_and_anomalies(self, frequencies, power_spectrum, power_db):
        """Detect peaks and anomalies in the power spectrum."""
        print("Detecting peaks and anomalies...")
        
        # Calculate local z-scores for anomaly detection
        window_size = 100  # Frequency bins for local baseline
        z_scores = np.zeros_like(power_db)
        
        for i in range(len(power_db)):
            start_idx = max(0, i - window_size//2)
            end_idx = min(len(power_db), i + window_size//2)
            local_power = power_db[start_idx:end_idx]
            
            # Exclude the current bin and nearby bins from baseline calculation
            exclude_range = 5
            exclude_mask = np.ones(len(local_power), dtype=bool)
            local_idx = i - start_idx
            exclude_start = max(0, local_idx - exclude_range)
            exclude_end = min(len(local_power), local_idx + exclude_range)
            exclude_mask[exclude_start:exclude_end] = False
            
            if np.sum(exclude_mask) > 10:  # Need enough points for statistics
                baseline_power = local_power[exclude_mask]
                mean_power = np.mean(baseline_power)
                std_power = np.std(baseline_power)
                if std_power > 0:
                    z_scores[i] = (power_db[i] - mean_power) / std_power
        
        # Find significant peaks
        significance_threshold = self.config['significance_threshold']
        peak_indices = np.where(z_scores > significance_threshold)[0]
        
        # Store peak information
        peaks_info = []
        for idx in peak_indices:
            peak_info = {
                'frequency_hz': frequencies[idx],
                'power_db': power_db[idx],
                'power_linear': power_spectrum[idx],
                'z_score': z_scores[idx],
                'significance': 1 - norm.cdf(z_scores[idx])  # p-value
            }
            peaks_info.append(peak_info)
            
        return peaks_info, z_scores
    
    def search_luft_frequencies(self, peaks_info):
        """Search for LUFT/UFT relevant frequencies in detected peaks."""
        print("Searching for LUFT/UFT frequencies...")
        
        target_freq = self.config['target_frequency']
        tolerance = self.config['frequency_tolerance']
        
        luft_matches = {
            'main_frequency': [],
            'harmonics': [],
            'subharmonics': [],
            'anomalies': []
        }
        
        for peak in peaks_info:
            freq = peak['frequency_hz']
            
            # Check main frequency
            if abs(freq - target_freq) <= tolerance:
                luft_matches['main_frequency'].append({
                    **peak,
                    'match_type': 'main_frequency',
                    'target_frequency': target_freq,
                    'frequency_error': freq - target_freq
                })
                continue
            
            # Check harmonics
            harmonic_found = False
            for order in self.config['harmonic_orders']:
                harmonic_freq = target_freq * order
                if abs(freq - harmonic_freq) <= tolerance:
                    luft_matches['harmonics'].append({
                        **peak,
                        'match_type': f'harmonic_{order}',
                        'target_frequency': harmonic_freq,
                        'frequency_error': freq - harmonic_freq,
                        'harmonic_order': order
                    })
                    harmonic_found = True
                    break
            
            if harmonic_found:
                continue
                
            # Check subharmonics
            subharmonic_found = False
            for order in self.config['subharmonic_orders']:
                subharmonic_freq = target_freq * order
                if abs(freq - subharmonic_freq) <= tolerance:
                    luft_matches['subharmonics'].append({
                        **peak,
                        'match_type': f'subharmonic_{order}',
                        'target_frequency': subharmonic_freq,
                        'frequency_error': freq - subharmonic_freq,
                        'subharmonic_order': order
                    })
                    subharmonic_found = True
                    break
            
            if not subharmonic_found:
                # Unmatched significant peak - potential anomaly
                luft_matches['anomalies'].append({
                    **peak,
                    'match_type': 'anomaly',
                    'target_frequency': None,
                    'frequency_error': None
                })
        
        return luft_matches
    
    def create_plots(self, frequencies, power_db, z_scores, luft_matches):
        """Create comprehensive plots of the analysis results."""
        print("Creating plots...")
        
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        # Plot 1: Full spectrum overview
        plt.figure(figsize=(15, 10))
        
        plt.subplot(3, 1, 1)
        plt.plot(frequencies, power_db, 'b-', alpha=0.7, linewidth=0.5)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')
        plt.title('HARPS Spectral Analysis - Full Spectrum Overview')
        plt.grid(True, alpha=0.3)
        plt.xlim(0, min(20000, frequencies[-1]))
        
        # Mark LUFT frequencies
        target_freq = self.config['target_frequency']
        plt.axvline(target_freq, color='red', linestyle='--', alpha=0.8, label=f'LUFT Target: {target_freq} Hz')
        
        # Plot 2: Z-scores for anomaly detection
        plt.subplot(3, 1, 2)
        plt.plot(frequencies, z_scores, 'g-', alpha=0.7, linewidth=0.5)
        plt.axhline(self.config['significance_threshold'], color='red', linestyle='--', 
                   label=f'Significance Threshold: {self.config["significance_threshold"]}σ')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Z-score')
        plt.title('Anomaly Detection - Local Z-scores')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xlim(0, min(20000, frequencies[-1]))
        
        # Plot 3: Detailed view around LUFT frequency
        plt.subplot(3, 1, 3)
        freq_range = self.config['plot_frequency_range']
        freq_mask = (frequencies >= freq_range[0]) & (frequencies <= freq_range[1])
        
        plt.plot(frequencies[freq_mask], power_db[freq_mask], 'b-', linewidth=1)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')
        plt.title(f'LUFT Frequency Region: {freq_range[0]}-{freq_range[1]} Hz')
        plt.grid(True, alpha=0.3)
        
        # Mark detected LUFT frequencies
        all_matches = []
        for category, matches in luft_matches.items():
            all_matches.extend(matches)
        
        for match in all_matches:
            freq = match['frequency_hz']
            if freq_range[0] <= freq <= freq_range[1]:
                plt.axvline(freq, color='red', linestyle='-', alpha=0.8)
                plt.text(freq, plt.ylim()[1] * 0.9, f"{freq:.1f} Hz\n{match['match_type']}", 
                        rotation=90, ha='center', va='top', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'harps_spectral_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 4: LUFT frequency hierarchy
        self.plot_luft_hierarchy(luft_matches, output_dir)
        
        return str(output_dir / 'harps_spectral_analysis.png')
    
    def plot_luft_hierarchy(self, luft_matches, output_dir):
        """Create a dedicated plot showing LUFT frequency hierarchy."""
        plt.figure(figsize=(12, 8))
        
        target_freq = self.config['target_frequency']
        
        # Prepare data for plotting
        categories = ['Subharmonics', 'Main Frequency', 'Harmonics']
        colors = ['blue', 'red', 'green']
        
        all_freqs = []
        all_powers = []
        all_categories = []
        all_labels = []
        
        # Subharmonics
        for match in luft_matches['subharmonics']:
            all_freqs.append(match['frequency_hz'])
            all_powers.append(match['power_db'])
            all_categories.append(0)
            all_labels.append(f"{match['frequency_hz']:.1f} Hz\n(sub {match['subharmonic_order']})")
        
        # Main frequency
        for match in luft_matches['main_frequency']:
            all_freqs.append(match['frequency_hz'])
            all_powers.append(match['power_db'])
            all_categories.append(1)
            all_labels.append(f"{match['frequency_hz']:.1f} Hz\n(main)")
        
        # Harmonics
        for match in luft_matches['harmonics']:
            all_freqs.append(match['frequency_hz'])
            all_powers.append(match['power_db'])
            all_categories.append(2)
            all_labels.append(f"{match['frequency_hz']:.1f} Hz\n(h{match['harmonic_order']})")
        
        # Create scatter plot
        for i, (category, color) in enumerate(zip(categories, colors)):
            cat_freqs = [f for f, c in zip(all_freqs, all_categories) if c == i]
            cat_powers = [p for p, c in zip(all_powers, all_categories) if c == i]
            if cat_freqs:
                plt.scatter(cat_freqs, cat_powers, c=color, s=100, alpha=0.7, 
                           label=f'{category} ({len(cat_freqs)} detected)', edgecolors='black')
        
        # Add labels
        for freq, power, label in zip(all_freqs, all_powers, all_labels):
            plt.annotate(label, (freq, power), xytext=(5, 5), textcoords='offset points',
                        fontsize=8, ha='left')
        
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')
        plt.title('LUFT/UFT Frequency Hierarchy Detection')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'luft_frequency_hierarchy.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_dir / 'luft_frequency_hierarchy.png')
    
    def create_summary_tables(self, luft_matches):
        """Create summary tables of detected frequencies."""
        print("Creating summary tables...")
        
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        # Comprehensive peaks table
        all_peaks = []
        for category, matches in luft_matches.items():
            for match in matches:
                peak_data = {
                    'Frequency (Hz)': f"{match['frequency_hz']:.3f}",
                    'Power (dB)': f"{match['power_db']:.2f}",
                    'Z-score': f"{match['z_score']:.2f}",
                    'Significance (p-value)': f"{match['significance']:.2e}",
                    'Match Type': match['match_type'],
                    'Target Frequency (Hz)': f"{match['target_frequency']:.1f}" if match['target_frequency'] else 'N/A',
                    'Frequency Error (Hz)': f"{match['frequency_error']:.3f}" if match['frequency_error'] is not None else 'N/A'
                }
                all_peaks.append(peak_data)
        
        # Sort by frequency
        all_peaks.sort(key=lambda x: float(x['Frequency (Hz)']))
        
        peaks_df = pd.DataFrame(all_peaks)
        peaks_df.to_csv(output_dir / 'detected_peaks_summary.csv', index=False)
        
        # LUFT-specific summary
        luft_summary = {
            'Main Frequency Detections': len(luft_matches['main_frequency']),
            'Harmonic Detections': len(luft_matches['harmonics']),
            'Subharmonic Detections': len(luft_matches['subharmonics']),
            'Anomaly Detections': len(luft_matches['anomalies']),
            'Total Significant Peaks': sum(len(matches) for matches in luft_matches.values())
        }
        
        luft_summary_df = pd.DataFrame([luft_summary])
        luft_summary_df.to_csv(output_dir / 'luft_detection_summary.csv', index=False)
        
        return peaks_df, luft_summary_df
    
    def generate_mining_summary(self, luft_matches, peaks_df):
        """Generate comprehensive summary for relay capsule."""
        print("Generating mining summary...")
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_freq = self.config['target_frequency']
        
        summary = {
            'mining_run_info': {
                'timestamp': timestamp,
                'target_frequency_hz': target_freq,
                'frequency_tolerance_hz': self.config['frequency_tolerance'],
                'total_analysis_duration': 'Simulated 60 seconds',
                'sample_rate_hz': self.config['sample_rate'],
                'fft_window_size': self.config['fft_window_size']
            },
            'instrument_metadata': self.config['instrument_metadata'],
            'detection_results': {
                'main_frequency_detections': len(luft_matches['main_frequency']),
                'harmonic_detections': len(luft_matches['harmonics']),
                'subharmonic_detections': len(luft_matches['subharmonics']),
                'anomaly_detections': len(luft_matches['anomalies']),
                'total_significant_peaks': len(peaks_df)
            },
            'major_findings': []
        }
        
        # Identify major findings
        if luft_matches['main_frequency']:
            main_peak = luft_matches['main_frequency'][0]
            summary['major_findings'].append({
                'type': 'Main LUFT Frequency Detection',
                'frequency_hz': main_peak['frequency_hz'],
                'power_db': main_peak['power_db'],
                'significance': main_peak['z_score'],
                'note': f'Strong detection at {main_peak["frequency_hz"]:.1f} Hz, matching LUFT target frequency'
            })
        
        # Add strongest harmonic
        if luft_matches['harmonics']:
            strongest_harmonic = max(luft_matches['harmonics'], key=lambda x: x['power_db'])
            summary['major_findings'].append({
                'type': 'Strongest Harmonic',
                'frequency_hz': strongest_harmonic['frequency_hz'],
                'power_db': strongest_harmonic['power_db'],
                'harmonic_order': strongest_harmonic['harmonic_order'],
                'significance': strongest_harmonic['z_score'],
                'note': f'Harmonic order {strongest_harmonic["harmonic_order"]} detected'
            })
        
        # Add anomalies
        for anomaly in luft_matches['anomalies'][:3]:  # Top 3 anomalies
            summary['major_findings'].append({
                'type': 'Spectral Anomaly',
                'frequency_hz': anomaly['frequency_hz'],
                'power_db': anomaly['power_db'],
                'significance': anomaly['z_score'],
                'note': f'Unexplained peak at {anomaly["frequency_hz"]:.1f} Hz'
            })
        
        self.summary = summary
        
        # Save summary as JSON for machine reading and YAML for human reading
        output_dir = Path(self.config['output_dir'])
        
        import json
        with open(output_dir / 'mining_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        with open(output_dir / 'mining_summary.yaml', 'w') as f:
            yaml.dump(summary, f, default_flow_style=False)
        
        return summary
    
    def run_complete_analysis(self, input_data=None):
        """Run the complete HARPS mining analysis pipeline."""
        print("=" * 60)
        print("HARPS Spectral Mining for LUFT/UFT Frequency Detection")
        print("=" * 60)
        
        # Generate or load data
        if input_data is None:
            signal_data, fs, t = self.generate_simulated_harps_data()
        else:
            signal_data, fs = input_data
        
        # Perform FFT analysis
        frequencies, power_spectrum, power_db = self.perform_fft_analysis(signal_data, fs)
        
        # Detect peaks and anomalies
        peaks_info, z_scores = self.detect_peaks_and_anomalies(frequencies, power_spectrum, power_db)
        
        # Search for LUFT frequencies
        luft_matches = self.search_luft_frequencies(peaks_info)
        
        # Create plots
        plot_path = self.create_plots(frequencies, power_db, z_scores, luft_matches)
        
        # Create summary tables
        peaks_df, luft_summary_df = self.create_summary_tables(luft_matches)
        
        # Generate comprehensive summary
        summary = self.generate_mining_summary(luft_matches, peaks_df)
        
        print(f"\nAnalysis complete! Results saved to: {self.config['output_dir']}")
        print(f"Main plot: {plot_path}")
        print(f"Detected {len(peaks_df)} significant peaks total")
        print(f"LUFT/UFT matches: {summary['detection_results']}")
        
        return {
            'luft_matches': luft_matches,
            'peaks_df': peaks_df,
            'summary': summary,
            'plot_path': plot_path
        }


def main():
    """Main function to run HARPS spectral mining."""
    parser = argparse.ArgumentParser(description='HARPS Spectral Mining for LUFT/UFT Detection')
    parser.add_argument('--config', type=str, help='Path to configuration YAML file')
    parser.add_argument('--input', type=str, help='Path to input FITS file (optional, uses simulated data if not provided)')
    parser.add_argument('--output-dir', type=str, default='harps_mining_results', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Initialize miner
    miner = HARPSMiner(config_path=args.config)
    
    # Override output directory if specified
    if args.output_dir:
        miner.config['output_dir'] = args.output_dir
    
    # Load input data if provided
    input_data = None
    if args.input:
        if args.input.endswith('.fits'):
            data, header = miner.load_harps_fits(args.input)
            if data is not None:
                # Adapt this based on actual HARPS FITS structure
                input_data = (data, miner.config['sample_rate'])
        else:
            print(f"Unsupported input format: {args.input}")
            print("Using simulated data instead.")
    
    # Run analysis
    results = miner.run_complete_analysis(input_data)
    
    print("\n" + "=" * 60)
    print("HARPS Spectral Mining Analysis Complete")
    print("=" * 60)
    print("Next step: Run 'python create_markdown_relay_capsule.py' to generate documentation")


if __name__ == '__main__':
    main()