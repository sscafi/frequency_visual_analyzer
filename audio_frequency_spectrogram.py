import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import noisereduce as nr  # Import noise reduction library
from scipy.signal import spectrogram  # For STFT

# Constants
INITIAL_RATE = 48000  # Sample rate
INITIAL_CHUNK = 1024   # Number of frames per buffer

# Global variables
is_streaming = False
stream = None
color_index = 0  # To cycle through colors
color_increment = 5  # Increase this value for faster transitions

# Initialize PyAudio
p = pyaudio.PyAudio()

def start_stream():
    """Start the audio stream."""
    global is_streaming, stream
    if not is_streaming:
        is_streaming = True
        device_index = 1  # Change this to the index of your microphone
        stream = p.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=INITIAL_RATE,
                         input=True,
                         input_device_index=device_index,
                         frames_per_buffer=INITIAL_CHUNK)
        animate_plot()  # Start updating the plot

def stop_stream():
    """Stop the audio stream."""
    global is_streaming, stream
    if is_streaming:
        is_streaming = False
        stream.stop_stream()
        stream.close()

def animate_plot():
    """Update the plot in real-time."""
    global color_index
    if is_streaming:
        try:
            # Read audio data
            data = stream.read(INITIAL_CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Apply advanced noise reduction using spectral gating
            audio_data = nr.reduce_noise(y=audio_data, sr=INITIAL_RATE)

            # Compute the Short-Time Fourier Transform (STFT)
            f, t, Sxx = spectrogram(audio_data, fs=INITIAL_RATE, nperseg=512, noverlap=256)

            # Convert the power spectrum to dB
            Sxx_db = 10 * np.log10(Sxx + 1e-10)  # Avoid log of zero

            # Set limits
            ax.set_xlim(0, INITIAL_RATE / 2)
            ax.set_ylim(-200, 0)  # Typically, we plot dB in negative values

            # Update the image plot
            ax.clear()  # Clear previous data
            ax.imshow(Sxx_db, aspect='auto', extent=[t.min(), t.max(), f.min(), f.max()],
                      origin='lower', cmap='viridis')
            ax.set_title('Real-Time Audio Spectrogram', color='black', fontsize=14)
            ax.set_xlabel('Time (s)', color='black', fontsize=12)
            ax.set_ylabel('Frequency (Hz)', color='black', fontsize=12)
            ax.set_facecolor('white')
            ax.spines['bottom'].set_color('black')
            ax.spines['left'].set_color('black')
            ax.spines['right'].set_color('black')
            ax.spines['top'].set_color('black')
            ax.tick_params(axis='x', colors='black', labelsize=10)
            ax.tick_params(axis='y', colors='black', labelsize=10)

            # Draw the updated figure
            fig.canvas.draw()

            # Call animate_plot again
            fig.canvas.get_tk_widget().after(1, animate_plot)
        except Exception as e:
            print("Error in animate_plot:", e)

def save_plot():
    """Save the current plot as an image file."""
    filename = filedialog.asksaveasfilename(defaultextension=".png", 
                                              filetypes=[("PNG files", "*.png"),
                                                         ("JPEG files", "*.jpg"),
                                                         ("All files", "*.*")])
    if filename:
        fig.savefig(filename, bbox_inches='tight', transparent=True)  # Save with transparency
        print(f"Plot saved as: {filename}")

# Set up the Tkinter window
root = tk.Tk()
root.title("Audio Visualizer")

# Prepare the plot
fig, ax = plt.subplots(figsize=(10, 5))  # Create a figure for the plot
ax.set_facecolor('white')  # Set the plot background to white
ax.spines['bottom'].set_color('black')  # Set axis spines color to black
ax.spines['left'].set_color('black')
ax.spines['right'].set_color('black')
ax.spines['top'].set_color('black')
ax.tick_params(axis='x', colors='black', labelsize=10)  # Set tick color to black
ax.tick_params(axis='y', colors='black', labelsize=10)
ax.set_title('Real-Time Audio Spectrogram', color='black', fontsize=14)
ax.set_xlabel('Time (s)', color='black', fontsize=12)
ax.set_ylabel('Frequency (Hz)', color='black', fontsize=12)

# Show the plot in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add Start and Stop buttons
controls_frame = tk.Frame(root, bg='white')
controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

start_button = tk.Button(controls_frame, text="Start", command=start_stream, bg='gray', fg='white')
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(controls_frame, text="Stop", command=stop_stream, bg='gray', fg='white')
stop_button.pack(side=tk.LEFT)

save_button = tk.Button(controls_frame, text="Save Plot", command=save_plot, bg='gray', fg='white')
save_button.pack(side=tk.LEFT)

# Start the Tkinter main loop
root.mainloop()

# Clean up PyAudio
stop_stream()
p.terminate()
