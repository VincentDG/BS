import wfdb
import numpy as np
import matplotlib.pyplot as plt

# Path to the annotation file
prefix = "mitdb-1.0.0.physionet.org"
annotation_file = '100'
record_name = f"{prefix}/{annotation_file}"

# Read the record
record = wfdb.rdrecord(record_name)

# Get the ECG signal
ecg_signal = record.p_signal[:, 0]

# Read the annotation file
annotation = wfdb.rdann(record_name, extension='atr')

# Get the annotation symbols and sample indices
annotation_symbols = annotation.symbol
annotation_indices = annotation.sample

# Create a time axis for the ECG signal
time_axis = (1 / record.fs) * np.arange(len(ecg_signal))

# Plot the ECG signal
plt.figure(figsize=(12, 6))
plt.plot(time_axis, ecg_signal, label='ECG Signal', color='black')

# Plot annotations with labels
for i, index in enumerate(annotation_indices):
    plt.text((1 / record.fs) * index, ecg_signal[index], annotation_symbols[i], color='red', fontsize=8, ha='center', va='center')

# Set plot labels and title
plt.xlabel('Time (s)')
plt.ylabel('ECG Amplitude')
plt.title('ECG Signal with Annotations')
plt.legend()
plt.grid(True)
plt.show()