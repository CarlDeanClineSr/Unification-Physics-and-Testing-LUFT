import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import requests
import io

# Helper: Download a JWST FITS spectrum from a direct URL (example placeholder)
def download_jwst_fits(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download: {url}")
    return fits.open(io.BytesIO(response.content))

# Helper: Extract wavelength and flux from FITS (JWST NIRSpec 1D spectrum example)
def get_spectrum_from_fits(hdul):
    # Typical JWST 1D spectrum: data in extension 1
    flux = hdul[1].data['FLUX']
    wavelength = hdul[1].data['WAVELENGTH']
    return wavelength, flux

# Core: Analyze spectrum for LUFT frequency signatures
def analyze_spectrum_for_luft(wavelength, flux, base_freq=7468, range_hz=10, verbose=True):
    # Convert wavelength to frequency (Hz): f = c / lambda (lambda in meters)
    c = 2.99792458e8  # m/s
    freq = c / (wavelength * 1e-10)  # wavelength in Angstroms to meters
    # Interpolate to regular frequency spacing (optional)
    freq_sorted = np.sort(freq)
    flux_sorted = flux[np.argsort(freq)]
    # FFT: look for periodicities in the flux as a function of frequency
    fft_flux = np.fft.rfft(flux_sorted - np.mean(flux_sorted))
    fft_freq = np.fft.rfftfreq(len(freq_sorted), d=(freq_sorted[1] - freq_sorted[0]))
    # Search for LUFT signatures
    luft_range = (fft_freq >= (base_freq - range_hz)) & (fft_freq <= (base_freq + range_hz))
    luft_peaks = np.abs(fft_flux)[luft_range]
    if verbose:
        print(f"LUFT frequency range ({base_freq}±{range_hz} Hz): Max FFT amplitude = {np.max(luft_peaks) if luft_peaks.size else 0}")
    # Plot
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    plt.plot(wavelength, flux)
    plt.xlabel("Wavelength (Å)")
    plt.ylabel("Flux")
    plt.title("JWST Spectrum")
    plt.subplot(1,2,2)
    plt.plot(fft_freq, np.abs(fft_flux))
    plt.axvspan(base_freq - range_hz, base_freq + range_hz, color='red', alpha=0.3, label='LUFT freq range')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("FFT Amplitude")
    plt.title("FFT of Spectrum")
    plt.legend()
    plt.tight_layout()
    plt.show()
    return {
        'luft_peak_amplitude': float(np.max(luft_peaks) if luft_peaks.size else 0),
        'fft_freq': fft_freq.tolist(),
        'fft_amplitude': np.abs(fft_flux).tolist()
    }

# Example usage:
# url = 'https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:JWST/product/jw01345-o002_t005_nircam_clear-f444w_sci.fits'
# hdul = download_jwst_fits(url)
# wavelength, flux = get_spectrum_from_fits(hdul)
# analyze_spectrum_for_luft(wavelength, flux)
