import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import matplotlib.cm as cm
from PIL import Image, ImageTk

# Constants
INITIAL_RATE = 44100  # Sample rate
INITIAL_CHUNK = 1024   # Number of frames per buffer
ZOOM_FACTOR = 2.0      # Zoom factor for magnifying glass
CIRCLE_RADIUS = 50     # Radius of the magnifying glass circle

# Global variables
is_streaming = False
stream = None
zoom_active = False
circle = None
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

            # Perform FFT
            fft_data = np.fft.fft(audio_data)
            fft_magnitude = np.abs(fft_data[:INITIAL_CHUNK // 2])  # Use only the first half
            
            # Create x values corresponding to the frequency bins
            x = np.linspace(0, INITIAL_RATE / 2, INITIAL_CHUNK // 2, endpoint=False)

            # Convert to dB
            fft_magnitude_db = 20 * np.log10(fft_magnitude + 1e-6)
            fft_magnitude_db = np.clip(fft_magnitude_db, -200, 200)  # Clip the dB values
            
            # Set limits
            ax.set_xlim(0, INITIAL_RATE / 2)
            ax.set_ylim(-200, 200)

            # Generate color based on the current color index
            color = cm.hsv(color_index / 360.0)  # HSV color based on angle
            color_index = (color_index + color_increment) % 360  # Cycle through hues

            # Update the line plot (create it if it doesn't exist)
            if not hasattr(animate_plot, "line"):
                animate_plot.line, = ax.plot(x, fft_magnitude_db, color=color[:3], linewidth=2)
            else:
                animate_plot.line.set_ydata(fft_magnitude_db)
                animate_plot.line.set_color(color[:3])  # Update color

            # If zoom is active, update the zoom effect
            if zoom_active and circle:
                mouse_x, mouse_y = circle.center
                zoomed_x = np.clip([mouse_x - (INITIAL_RATE / (2 * ZOOM_FACTOR)), 
                                     mouse_x + (INITIAL_RATE / (2 * ZOOM_FACTOR))], 0, INITIAL_RATE / 2)
                zoomed_y = [-200, 200]
                ax.set_xlim(zoomed_x)
                ax.set_ylim(zoomed_y)

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

def toggle_zoom():
    """Toggle the zoom functionality with a magnifying glass."""
    global zoom_active, circle
    zoom_active = not zoom_active

    if zoom_active:
        circle = plt.Circle((0, 0), CIRCLE_RADIUS, color='yellow', alpha=0.5, fill=True)  # Create a circle
        ax.add_patch(circle)
        fig.canvas.mpl_connect('motion_notify_event', update_circle)
        print("Zoom activated. Move the mouse over the graph to see the magnifying effect.")
    else:
        if circle:
            circle.remove()
            circle = None
        print("Zoom deactivated.")

def update_circle(event):
    """Update the position of the magnifying glass circle."""
    if zoom_active and event.inaxes == ax:
        circle.center = (event.xdata, event.ydata)  # Update the circle center to mouse position
        fig.canvas.draw_idle()

def on_mouse_leave(event):
    """Deactivate zoom if the mouse leaves the axes."""
    global zoom_active
    if zoom_active:
        toggle_zoom()

def resize(event):
    """Resize the canvas and background image based on the window size."""
    # Resize background image
    bg_image_resized = bg_image.resize((event.width, event.height), Image.LANCZOS)
    bg_photo_resized = ImageTk.PhotoImage(bg_image_resized)
    
    # Update the canvas background
    bg_canvas.create_image(0, 0, image=bg_photo_resized, anchor='nw')
    bg_canvas.image = bg_photo_resized  # Keep a reference to avoid garbage collection
    
    # Update the figure size
    fig.set_size_inches(event.width / 100, event.height / 100)
    fig.canvas.draw()

# Set up the Tkinter window
root = tk.Tk()
root.title("Audio Visualizer")

# Load the background image
bg_image = Image.open("wallpaper.jpg")  # Adjust the file name as needed
bg_image = bg_image.resize((800, 600))  # Resize to fit the initial window size
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas for the background
bg_canvas = tk.Canvas(root, width=800, height=600)
bg_canvas.pack(fill=tk.BOTH, expand=True)

# Set the background image
bg_canvas.create_image(0, 0, image=bg_photo, anchor='nw')

# Prepare the plot
fig, ax = plt.subplots(figsize=(10, 5), facecolor='none')  # Make the figure background transparent
fig.patch.set_alpha(0.0)  # Make the figure background transparent
ax.set_facecolor((0, 0, 0, 0))  # Set the plot background to transparent
ax.spines['bottom'].set_color('none')  # Remove axis spines
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.tick_params(axis='x', colors='white', labelsize=10)  # Set tick color to white
ax.tick_params(axis='y', colors='white', labelsize=10)
ax.set_xlim(0, INITIAL_RATE / 2)  # Set x-limit from 0 to max frequency
ax.set_ylim(-200, 200)  # Set y-limit for dB range from -200 to +200
ax.set_title('Real-Time Audio Frequency Spectrum', color='white', fontsize=14)
ax.set_xlabel('Frequency (Hz)', color='white', fontsize=12)
ax.set_ylabel('Magnitude (dB)', color='white', fontsize=12)

# Remove the grid
ax.grid(False)

# Show the plot in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=bg_canvas)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Load the wallpaper as background of the axes
ax.imshow(bg_image, extent=[0, INITIAL_RATE / 2, -200, 200], aspect='auto', zorder=-1)

# Add Start, Stop, Save, and Zoom buttons
controls_frame = tk.Frame(root, bg='black')
controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

start_button = tk.Button(controls_frame, text="Start", command=start_stream, bg='gray', fg='white')
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(controls_frame, text="Stop", command=stop_stream, bg='gray', fg='white')
stop_button.pack(side=tk.LEFT)

save_button = tk.Button(controls_frame, text="Save Plot", command=save_plot, bg='gray', fg='white')
save_button.pack(side=tk.LEFT)

zoom_button = tk.Button(controls_frame, text="Toggle Zoom", command=toggle_zoom, bg='gray', fg='white')
zoom_button.pack(side=tk.LEFT)

# Connect mouse events for zoom functionality
fig.canvas.mpl_connect('button_press_event', lambda event: event)
fig.canvas.mpl_connect('axes_leave_event', on_mouse_leave)  # Use axes_leave_event

# Bind the resize event to the Tkinter window
root.bind("<Configure>", resize)

# Start the Tkinter main loop
root.mainloop()

# Clean up PyAudio
stop_stream()
p.terminate()
