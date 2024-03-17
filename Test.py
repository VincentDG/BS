import wfdb
import csv
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import neurokit2 as nk
import pandas as pd

#parameters
sample = 101
rate = 360


patient_record = wfdb.rdrecord(f"mitdb-1.0.0.physionet.org/{sample}", sampfrom=0, sampto=4000)

# print(patient_record.__dict__)

# Extract patient info, lead names, and ECG data
patient_number = patient_record.record_name
leads = patient_record.sig_name
ecg_data = patient_record.p_signal

# Create CSV
filename = f"{patient_number}.csv"
outfile = open(filename, "w")
out_csv = csv.writer(outfile)

# Write CSV header with lead names
out_csv.writerow(leads)

# Write ECG data to CSV
for row in ecg_data:
    out_csv.writerow(row)


patient_record = wfdb.rdrecord(f"mitdb-1.0.0.physionet.org/{sample}",  sampfrom=0, sampto=4000)
patient_annotation = wfdb.rdann(f"mitdb-1.0.0.physionet.org/{sample}", 'atr',  sampfrom=0, sampto=4000, shift_samps=True)
'''
wfdb.plot_wfdb(patient_record, patient_annotation) # plots the ECG
'''




lead1 = patient_record.p_signal[:, 0]
lead2= patient_record.p_signal[:, 1]


#Used for setting up your own processing pipeline
'''
def my_processing(ecg_signal):
    # Do processing
    ecg_cleaned = nk.ecg_clean(ecg_signal, sampling_rate=rate)
    instant_peaks, rpeaks, = nk.ecg_peaks(ecg_cleaned, sampling_rate=rate)
    rate = nk.ecg_rate(rpeaks, sampling_rate=rate, desired_length=len(ecg_cleaned))
    quality = nk.ecg_quality(ecg_cleaned, sampling_rate=rate)


    # Prepare output
    signals = pd.DataFrame({"ECG_Raw": ecg_signal,
                            "ECG_Clean": ecg_cleaned,
                            "ECG_Rate": rate,
                            "ECG_Quality": quality})
    signals = pd.concat([signals, instant_peaks], axis=1)

    # Create info dict
    info = rpeaks
    info["sampling_rate"] = rate
    
    return signals, info
'''








selectedecg = lead1

# Checks if the ECG is inverted or not and gets rpeaks and cleaned_ecg accordingly
leadfix, check = nk.ecg_invert(selectedecg, sampling_rate=rate)
if check == True:
    signals, info = nk.ecg_process(leadfix, sampling_rate=rate)
    rpeaks = info["ECG_R_Peaks"]
    cleaned_ecg = signals["ECG_Clean"]
    _, waves_peak = nk.ecg_delineate(leadfix, rpeaks, sampling_rate=rate, method="cwt", show=True, show_type='all')
else:
    signals, info = nk.ecg_process(selectedecg, sampling_rate=rate)
    rpeaks = info["ECG_R_Peaks"]
    cleaned_ecg = signals["ECG_Clean"]
    _, waves_peak = nk.ecg_delineate(selectedecg, rpeaks, sampling_rate=rate, method="cwt", show=True, show_type='all')


# This is for detecting P,Q,S,and T waves (not visible for large datasets) (if not detected, consider setting a sampfrom and sampto in patient_record)
    
plot = nk.events_plot([waves_peak['ECG_T_Peaks'][:3], 
                       waves_peak['ECG_P_Peaks'][:3],
                       waves_peak['ECG_Q_Peaks'][:3],
                       rpeaks[:3],
                       waves_peak['ECG_S_Peaks'][:3]], selectedecg[:1440])
plt.show()

#Plots the info of the ECG along with the locations of the P, Q, S, and T waves
nk.ecg_plot(signals, info)
plt.show()

#Compares Predicted vs Actual Heartbeats (R-peaks)
print("Predicted # of Heartbeats: " + str(len(rpeaks)))
print("Actual # of Heartbeats: " + str(len(patient_annotation.symbol)))

# Plotting all the heart beats
epochs = nk.ecg_segment(cleaned_ecg, rpeaks=None, sampling_rate=360, show=False)
nk.epochs_plot(epochs)
plt.show()
