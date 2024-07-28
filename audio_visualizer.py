import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

# Constants
INITIAL_RATE = 48000  # Sample rate
INITIAL_CHUNK = 1024   # Number of frames per buffer

# Global variables
is_streaming = False
stream = None
zoom_rect = None
zoom_start = None
zoom_end = None

# Initialize PyAudio
p = pyaudio.PyAudio()

def list_input_devices():
    """List all available audio input devices."""
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    print("Available input devices:")
    for i in range(0, numdevices):
        device = p.get_device_info_by_index(i)
        if device['maxInputChannels'] > 0:  # Check if it's an input device
            print(f"Device {i}: {device['name']}")

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
    if is_streaming:
        try:
            # Read audio data
            data = stream.read(INITIAL_CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Perform FFT
            fft_data = np.fft.fft(audio_data)
            fft_magnitude = np.abs(fft_data[:INITIAL_CHUNK // 2])  # Use only the first half
            
            # Create x values corresponding to the frequency bins
            x = np.linspace(0, INITIAL_RATE / 2, INITIAL_CHUNK // 2, endpoint=False)

            # Convert to dB
            fft_magnitude_db = 20 * np.log10(fft_magnitude + 1e-6)
            fft_magnitude_db = np.clip(fft_magnitude_db, -200, 200)  # Clip the dB values
            
            # Clear previous plot
            ax.clear()
            ax.set_xlim(0, INITIAL_RATE / 2)  # Set x-limit from 0 to max frequency
            ax.set_ylim(-200, 200)  # Set y-limit for dB range from -200 to +200
            ax.set_title('Real-Time Audio Frequency Spectrum')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Magnitude (dB)')
            ax.grid()

            # Create random colors for the bars
            num_bars = len(fft_magnitude_db)
            colors = np.random.rand(num_bars, 3)  # Generate random RGB colors

            # Create bars for frequency bands
            width = np.diff(x, prepend=0)  # Bar width for each frequency
            ax.bar(x, fft_magnitude_db, width=width, align='edge', edgecolor='black', color=colors)  # Plot bars with random colors

            # If zoom is active, update the limits
            if zoom_start is not None and zoom_end is not None:
                ax.set_xlim(zoom_start, zoom_end)

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
        fig.savefig(filename)
        print(f"Plot saved as: {filename}")

def reset_zoom():
    """Reset the zoom to the original view."""
    global zoom_start, zoom_end
    zoom_start = None
    zoom_end = None
    ax.set_xlim(0, INITIAL_RATE / 2)
    ax.set_ylim(-200, 200)
    fig.canvas.draw()

def on_mouse_press(event):
    """Record the starting point of the zoom rectangle."""
    global zoom_start, zoom_end
    if event.inaxes == ax:
        zoom_start = event.xdata

def on_mouse_release(event):
    """Record the end point of the zoom rectangle and update the plot."""
    global zoom_start, zoom_end
    if event.inaxes == ax:
        zoom_end = event.xdata
        if zoom_start and zoom_end:
            ax.set_xlim(sorted([zoom_start, zoom_end]))
            fig.canvas.draw()
            zoom_start = None
            zoom_end = None

# Set up the Tkinter window
root = tk.Tk()
root.title("Audio Visualizer")

# Prepare the plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, INITIAL_RATE / 2)  # Set x-limit from 0 to max frequency
ax.set_ylim(-200, 200)  # Set y-limit for dB range from -200 to +200
ax.set_title('Real-Time Audio Frequency Spectrum')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude (dB)')
ax.grid()

# Show the plot in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Add Start, Stop, Save, and Reset Zoom buttons
start_button = tk.Button(root, text="Start", command=start_stream)
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(root, text="Stop", command=stop_stream)
stop_button.pack(side=tk.LEFT)

save_button = tk.Button(root, text="Save Plot", command=save_plot)
save_button.pack(side=tk.LEFT)

reset_zoom_button = tk.Button(root, text="Reset Zoom", command=reset_zoom)
reset_zoom_button.pack(side=tk.LEFT)

# Connect mouse events for zoom functionality
fig.canvas.mpl_connect('button_press_event', on_mouse_press)
fig.canvas.mpl_connect('button_release_event', on_mouse_release)

# List input devices
list_input_devices()

# Start the Tkinter main loop
root.mainloop()

# Clean up
if stream is not None:
    stream.stop_stream()
    stream.close()
p.terminate()
