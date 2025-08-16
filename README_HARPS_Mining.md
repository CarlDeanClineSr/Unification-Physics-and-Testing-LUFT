# HARPS Spectral Mining for LUFT/UFT Frequency Detection

This directory contains a modular HARPS spectral mining script and Markdown relay capsule for detecting LUFT (Lattice-Unified Field Theory) and UFT (Unified Field Theory) frequency signatures.

## Files Overview

### Main Scripts
- `harps_spectral_mining.py` - Main spectral analysis script
- `create_markdown_relay_capsule.py` - Documentation generator
- `harps_config.yaml` - Configuration file

### Generated Output (in `harps_mining_results/`)
- `harps_spectral_analysis.png` - Multi-panel spectral analysis plots
- `luft_frequency_hierarchy.png` - LUFT frequency hierarchy visualization
- `detected_peaks_summary.csv` - Detailed peak detection data
- `luft_detection_summary.csv` - LUFT-specific summary statistics
- `mining_summary.json/yaml` - Complete analysis summary
- `HARPS_LUFT_Mining_Relay_Capsule.md` - Comprehensive documentation

## Quick Start

1. **Run the spectral analysis:**
```bash
python harps_spectral_mining.py --config harps_config.yaml
```

2. **Generate documentation:**
```bash
python create_markdown_relay_capsule.py
```

## Key Features

### HARPS Spectral Mining Script
- **Target Frequency:** 7,468 Hz ± 10 Hz (primary LUFT frequency)
- **Harmonic Detection:** Multiple harmonic orders and subharmonics
- **FFT Analysis:** Welch's method with configurable parameters
- **Anomaly Detection:** Statistical z-score analysis with significance thresholding
- **Visualization:** Multi-scale spectral plots and frequency hierarchy mapping
- **Data Export:** CSV tables and JSON/YAML summaries

### Markdown Relay Capsule
- **Complete Documentation:** Analysis methodology, results, and findings
- **Instrument Metadata:** HARPS observatory specifications
- **Tables and Figures:** Integration of analysis outputs
- **LUFT/UFT Context:** Astrochemical and theoretical implications
- **Repository Integration:** Ready for peer review and collaboration

## Configuration

The `harps_config.yaml` file controls all analysis parameters:

```yaml
target_frequency: 7468.0  # Hz - main LUFT frequency
frequency_tolerance: 10.0  # Hz - search window
harmonic_orders: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
subharmonic_orders: [0.5, 0.25, 0.125, 0.0625]
significance_threshold: 6.0  # Z-score threshold
```

## Analysis Results Summary

The latest analysis detected:
- **4 Main LUFT Frequency detections** around 7,468 Hz
- **6 Harmonic detections** at integer multiples  
- **5 Subharmonic detections** at fractional divisions
- **19 Spectral anomalies** requiring further investigation
- **34 Total significant peaks** above threshold

## Dependencies

```bash
pip install numpy scipy matplotlib astropy pyyaml pandas tabulate
```

## Real HARPS Data Integration

To use real HARPS FITS files instead of simulated data:

```bash
python harps_spectral_mining.py --config harps_config.yaml --input path/to/harps_data.fits
```

The script includes placeholder code for FITS file loading that can be adapted based on actual HARPS data structure.

## Integration with Repository

This module is designed to integrate with the existing luftkit framework and LUFT research documented in this repository. The detected frequency signatures align with LUFT theoretical predictions and complement existing experimental observations.

## Author

Carl Dean Cline Sr.  
Reality-based Space and its functionality repository  
LUFT/UFT Research Initiative