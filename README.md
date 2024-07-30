# Audio Visualizer

This project is a real-time audio visualizer built using Python. It captures audio from a microphone and displays its frequency spectrum in real-time using a graphical interface. The visualizer can also apply noise reduction to enhance the visibility of dominant frequencies. It includes a spectrogram visualization that displays audio frequency content over time.

## Features

- Real-time frequency spectrum visualization.
- Real-time spectrogram visualization of audio.
- Advanced noise reduction to improve clarity of louder sounds.
- Ability to save the current plot or spectrogram as an image.
- Intuitive graphical user interface (GUI) using Tkinter.
- Customizable microphone input settings.

## Requirements

To run this project, you need to have Python installed on your machine. Additionally, you will need to install the following Python packages:

- `numpy`
- `pyaudio`
- `matplotlib`
- `tkinter` (comes pre-installed with Python)
- `noisereduce`
- `scipy`

You can install the required packages using `pip`:

```bash
pip install numpy pyaudio matplotlib noisereduce scipy
