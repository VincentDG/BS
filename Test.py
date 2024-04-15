import wfdb
import csv
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import neurokit2 as nk
import pandas as pd
from kneed import KneeLocator
from scipy.spatial import ConvexHull


#parameters
folder = "00000"
sample = "00016_lr"
rate = 100


patient_record = wfdb.rdrecord(f"mitdb-1.0.0.physionet.org/records100/{folder}/{sample}")

# print(patient_record.__dict__)
'''
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


patient_record = wfdb.rdrecord(f"mitdb-1.0.0.physionet.org/{sample}")
wfdb.plot_wfdb(patient_record, patient_annotation) # plots the ECG
'''




lead1 = patient_record.p_signal[:, 6]
lead2= patient_record.p_signal[:, 7]
lead3= patient_record.p_signal[:, 8]

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









ecg_signal = lead2


signals, info = nk.ecg_process(ecg_signal, sampling_rate=rate)
rpeaks = info["ECG_R_Peaks"]
ecg_signal = signals["ECG_Clean"]
'''
_, rpeaks = nk.ecg_peaks(ecg_signal, sampling_rate=rate)
'''

plot = nk.events_plot(rpeaks, ecg_signal)
plt.show()

_, waves_peak = nk.ecg_delineate(ecg_signal, rpeaks, sampling_rate=rate, method="dwt")



t_peak = waves_peak['ECG_T_Peaks']
t_peak = np.array(t_peak)
t_peak = t_peak[~np.isnan(t_peak)]
t_peak = t_peak.astype('int64')
    
s_peak = waves_peak['ECG_S_Peaks']
s_peak = np.array(s_peak)
s_peak = s_peak[~np.isnan(s_peak)]
s_peak = s_peak.astype('int64')


t_onset = waves_peak['ECG_T_Onsets']
t_onset = np.array(t_onset)
t_onset = t_onset[~np.isnan(t_onset)]
t_onset = t_onset.astype('int64')




def saddleback(points):

    # Check if the difference between the first index and the last index is within percentage%
    n1 = points[0]
    n2 = points[-1]

    percentage = 100

    difference = abs(n1 - n2)
    percentage_difference = (difference / max(n1, n2)) * 100

    if abs(percentage_difference) > percentage:
        return False


    # Check if the minimum value is within +-1 index of the middle index
    min_index = np.argmin(points)
    middle_index = len(points) // 2
    
    if abs(min_index - middle_index) > 3:
        return False
   
    # Check if the graph is constantly decreasing from first index to minima, and constantly increasing from minima to last index to form a saddleback shape
    decreasing = np.all(points[:min_index] >= points[1:min_index+1])
    increasing = np.all(points[min_index:len(points)-1] <= points[min_index+1:len(points)])

    return decreasing and increasing

def coved(points):
    last_index = len(points)
    decreasing = np.all(points[:len(points)-1] >= points[1:len(points)])

    return decreasing



# TYPE 1 BRUGADA DETECTION#
def Type1():

    # Get the J-points from the S and T peaks
    jpoint= []
    for i in range(0, len(s_peak)):
        x= [i for i in range(s_peak[i], t_peak[i]+1)]
        y = ecg_signal[s_peak[i]:t_peak[i]+1]
        kn = KneeLocator(x, y, curve='concave', direction='increasing')
        kneepoint = kn.knee
        jpoint.append(kneepoint)



    # Plot the S and T peaks and the J point
    plot = nk.events_plot([waves_peak['ECG_T_Peaks'],
                        waves_peak['ECG_S_Peaks'],
                         waves_peak['ECG_T_Onsets'],
                           jpoint], ecg_signal)
    plt.show()

    # Check if the ST segment is elevated by checking if the Jpoint is >= 0.2 mV
    elevate2 = []
    for i in range(0, len(jpoint)):
        if ecg_signal[jpoint[i]] >= 0.2:
            elevate2.append(1)
        else:
            elevate2.append(0)


    elevate2[0] =1
    elevate2[1] = 1


    # If ST segment is elevated, check if coved
    for i in range(0, len(elevate2)):
        if elevate2[i] == 1:
            x= np.array([i for i in range(jpoint[i], t_onset[i]+1)])
            y= np.array(ecg_signal[jpoint[i]:t_onset[i]+1])
            # Check if T-wave is inverted by checking if T point is negative
            if t_onset[i] <= 0.2:
                # Check if coved 
                if coved(y):
                    print('Type 1 Brugada: ' + str(jpoint[i]))
                else:
                    print('Not Type 1 Brugada: ' + str(jpoint[i]))
            else:
                print('Not Type 1 Brugada: ' + str(jpoint[i]))
        else:
            print('Not Type 1 Brugada: ' + str(jpoint[i]))


# TYPE 2 BRUGADA DETECTION#
def Type2():

    # Get the J-points from the S and T peaks
    jpoint= []
    for i in range(0, len(s_peak)):
        x= [i for i in range(s_peak[i], t_peak[i]+1)]
        y = ecg_signal[s_peak[i]:t_peak[i]+1]
        kn = KneeLocator(x, y, curve='concave', direction='increasing')
        kneepoint = kn.knee
        jpoint.append(kneepoint)



    # Plot the S and T peaks and the J point
    plot = nk.events_plot([waves_peak['ECG_T_Peaks'],
                        waves_peak['ECG_S_Peaks'],
                         waves_peak['ECG_T_Onsets'],
                           jpoint], ecg_signal)
    plt.show()

    # Check if the ST segment is elevated by checking if the Jpoint is >= 0.2 mV
    elevate2 = []
    for i in range(0, len(jpoint)):
        if ecg_signal[jpoint[i]] >= 0.2:
            elevate2.append(1)
        else:
            elevate2.append(0)

    elevate2[0] =1
    elevate2[1] = 1


    # If ST segment is elevated, check if saddleback
    for i in range(0, len(elevate2)):
        if elevate2[i] == 1:
            y= np.array(ecg_signal[jpoint[i]:t_onset[i]+1])
            if saddleback(y):
                print('Type 2 Brugada: ' + str(jpoint[i]))
            else:
                print('Not Type 2 Brugada: ' + str(jpoint[i]))

        else:
            print('Not Type 2 Brugada: ' + str(jpoint[i]))
    






Type1()
Type2()




'''
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
'''