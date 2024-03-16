import numpy as np
import plotly.graph_objs as go
from flask import Flask, render_template, request, jsonify
import wfdb
import logging

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the available numbers
available_numbers = [
    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "111", "112", "113", "114", "115", "116", "117", "118", "119",
    "121", "122", "123", "124",
    "200", "201", "202", "203",
    "205", "206", "207", "208", "209", "210",
    "212", "213", "214", "215",
    "217",
    "219", "220", "221", "222", "223",
    "228",
    "230", "231", "232", "233", "234"
]

# Define the available signals
available_signals = ["Signal 1", "Signal 2"]      

def plot_ecg(signal, lead, start_time, end_time, fs=360.0, annotate_mode=False, annotation_x=None, annotation_text=None):
    # Existing code to create the plot...
    
    if annotate_mode:
        # Add a blue vertical line at the specified x-coordinate
        fig.add_shape(
            type="line",
            x0=annotation_x, y0=-2.01, x1=annotation_x, y1=2.01,
            line=dict(color="blue", width=2, dash='dash')
        )
        
        # Add text label for the vertical line
        fig.add_annotation(
            x=annotation_x, y=0, # Adjust y position as needed
            text=annotation_text,
            showarrow=False,
            font=dict(size=12, color="blue"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=4,
            opacity=0.8
        )
    
    time = np.arange(start_time, end_time) / fs

    app.logger.info(f"time: {time}")

    # Create a Plotly figure
    fig = go.Figure()

    # Add ECG signal trace
    fig.add_trace(go.Scatter(x=time, y=signal, mode='lines', name='ECG Signal'))

    # # Customize layout
    fig.update_layout(
        title="ECG Plot",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (mV)",
        plot_bgcolor='white',
        height=800,  # Set the height to 800 pixels
        width=1360,
        xaxis=dict(tickmode='array', tickvals=np.arange(start_time/360, end_time/360, 0.2), range=[start_time/360, end_time/360]),  
        yaxis=dict(range=[-2.01,2.01]),  # Adjust the range of the y-axis
    )

     # Add light red gridlines every 0.04 seconds on the x-axis
    for x in np.arange(start_time/360, end_time/360, 0.04):
        fig.add_shape(type="line",
                      x0=x, y0=-2.01, x1=x, y1=2.01,
                      line=dict(color="rgba(255, 0, 0, 0.5)", width=1, dash='solid'))  # Light red (alpha=0.5) solid line

    # Add darker red gridlines every 0.2 seconds on the x-axis
    for x in np.arange(start_time/360, end_time/360, 0.2):
        fig.add_shape(type="line",
                      x0=x, y0=-2.01, x1=x, y1=2.01,
                      line=dict(color="rgba(255, 0, 0, 1.0)", width=1, dash='solid'))  # Darker red (alpha=1.0) solid line

    # Add light red gridlines every 0.1 on the y-axis
    for y in np.arange(0, 2.01, 0.1):
        fig.add_shape(type="line",
                      x0=0, y0=y, x1=end_time/360, y1=y,
                      line=dict(color="rgba(255, 0, 0, 0.5)", width=1, dash='solid'))  # Light red (alpha=0.5) solid line

    for y in np.arange(0, -2.01, -0.1):
        fig.add_shape(type="line",
                      x0=0, y0=y, x1=end_time/360, y1=y,
                      line=dict(color="rgba(255, 0, 0, 0.5)", width=1, dash='solid'))  # Light red (alpha=0.5) solid line

    # Add darker red gridlines every 0.5 on the y-axis
    for y in np.arange(0, 2.01, 0.5):
        fig.add_shape(type="line",
                      x0=0, y0=y, x1=end_time/360, y1=y,
                      line=dict(color="rgba(255, 0, 0, 1.0)", width=1, dash='solid'))  # Darker red (alpha=1.0) solid line

    for y in np.arange(0, -2.01, -0.5):
        fig.add_shape(type="line",
                      x0=0, y0=y, x1=end_time/360, y1=y,
                      line=dict(color="rgba(255, 0, 0, 1.0)", width=1, dash='solid'))  # Darker red (alpha=1.0) solid line
   
    # Update the layout to fix the aspect ratio
    fig.update_layout(
        xaxis=dict(fixedrange=True),  # Fix the x-axis range
        yaxis=dict(fixedrange=True),   # Fix the y-axis range
        title = f"Lead: {lead}"
    )

    return fig.to_html(full_html=False)


@app.route('/', methods=['GET', 'POST'])
def display_plot():
    if request.method == 'POST':
        # Get sampto value, selected number and selected signal from the form
        sampfrom = int(request.form['sampfrom'])
        sampto = int(request.form['sampto'])
        selected_number = request.form['selected_number']
        selected_signal = request.form['selected_signal']
    else:
        sampfrom = 0                    # Default sampfrom value
        sampto = 1081                   # Default sampto value
        selected_number = "100"         # Default selected number
        selected_signal = "Signal 1"    # Default selected signal

    # Read ECG signal data -- Need to revise sampfrom and sampto
    patient_record = wfdb.rdrecord(f"mitdb-1.0.0.physionet.org/{selected_number}", sampfrom=sampfrom, sampto=sampto)
    s1 = patient_record.p_signal[:, 0]
    s2 = patient_record.p_signal[:, 1]

    # Get the selected signal data
    if (selected_signal == "Signal 1"):
        signal_data = s1 
        title = patient_record.sig_name[0]
    else:
        signal_data = s2
        title = patient_record.sig_name[1]

    # Plot ECG signal and return the HTML content
    plot_html = plot_ecg(signal_data, title, start_time=sampfrom, end_time= sampto, fs=360.0)

    app.logger.info(f"Sampfrom: {sampfrom}")
    app.logger.info(f"Sampto: {sampto}")

    # app.logger.info(f"Available signals: {available_signals}")

    return render_template('plot4.html', plot_html=plot_html, 
                           available_numbers=available_numbers, 
                           available_signals=available_signals, 
                           selected_number=selected_number, 
                           selected_signal=selected_signal,
                           last_sampfrom = sampfrom,
                           last_sampto = sampto
                           )

@app.route('/annotate-plot', methods=['POST'])
def update_plot():
    # Parse the incoming JSON data
    data = request.get_json()
    
    # Extract annotation data
    annotation_x = data.get('annotationX')
    annotation_text = data.get('annotationText')
    
    # Here, you would process the annotation data, e.g., update the plot
    # For demonstration, let's just return a success message
    return jsonify({'message': 'Annotation updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)