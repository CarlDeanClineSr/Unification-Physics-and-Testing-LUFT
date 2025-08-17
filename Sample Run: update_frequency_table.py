# Sample Run: update_frequency_table.py (Synthetic Data Demo)

**Goal:**  
Show that the LUFT frequency logging tool will capture *any* frequency anomaly, not just LUFT-predicted values.

---

### Step 1: Generate Synthetic Data

- Simulate a time series with strong peaks at **1,234 Hz** and **8,765 Hz** (not LUFT-standard).

```python
import numpy as np

fs = 20000  # 20 kHz sample rate
duration = 5  # seconds
t = np.linspace(0, duration, int(fs*duration), endpoint=False)
signal = 0.5*np.sin(2*np.pi*1234*t) + 0.7*np.sin(2*np.pi*8765*t) + 0.1*np.random.randn(len(t))
np.savetxt("synthetic_signal.txt", signal)
```

---

### Step 2: Run `update_frequency_table.py`

```python
from update_frequency_table import update_frequency_table

update_frequency_table("synthetic_signal.txt", fs=20000, dataset="Synthetic Test Data", freq_range=(0, 10000))
```

---

### Step 3: Output in `frequency_coincidence_table.md`

| Frequency (Hz/eV) | Dataset/Source     | Signal Type        | Coincidence/Note | Discovery Date | Reference/Script        | Notes/Hypotheses   |
|-------------------|--------------------|--------------------|------------------|----------------|------------------------|--------------------|
| 1,234.00 Hz       | Synthetic Test Data| Frequency anomaly  | Potential lattice resonance, check cross-dataset | 2025-08-17 | update_frequency_table.py | Synthetic demo, not LUFT-predicted |

- **Result:**  
  The script logs the *actual detected peak*, not just LUFT/theoretical frequencies.
- The table can now record *any recurring peak*—even if it’s new, unexplained, or cross-dataset.

---

### Step 4: Plot (Optional)

![Synthetic Frequency Plot](data/frequency_logs/plot_20250817.png)

---

**Conclusion:**  
This proves the pipeline is “open”—ready for new discoveries, not closed to old ideas. The more we log, the more we may notice **true coincidences** that matter for *unification*.
