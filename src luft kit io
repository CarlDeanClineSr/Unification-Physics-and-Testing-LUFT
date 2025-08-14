import wave, contextlib, json, os
import numpy as np
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

def read_wav(path: str) -> Tuple[np.ndarray, int]:
    import soundfile as sf
    data, fs = sf.read(path)
    if data.ndim > 1:
        data = data[:,0]
    return data.astype(np.float64), fs

def load_sidecar(path: str) -> Dict[str, Any]:
    sidecar1 = path + ".json"
    sidecar2 = os.path.join(os.path.dirname(path), "meta.json")
    for cand in (sidecar1, sidecar2):
        if os.path.exists(cand):
            try:
                with open(cand, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
    return {}

def write_csv(path: str, rows, header):
    import csv
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
