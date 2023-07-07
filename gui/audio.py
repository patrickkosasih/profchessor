"""
gui/audio.py

The module that plays audio (sound effects) to the user, powered by the Pyaudio library.

Note: Audio interfacing is technically a separate field from GUI, but this module is still part of the `gui` package in
order for organizing modules.
"""

import wave
import pyaudio
import threading
import os

DEFAULT_PATH = "data/sfx/"

p = pyaudio.PyAudio()
"""
The interface object of the pyaudio module
"""


def play_sound_and_wait(filename):
    if os.path.isfile(DEFAULT_PATH + filename):
        filename = DEFAULT_PATH + filename

    file = wave.open(filename, "rb")
    stream = p.open(format=p.get_format_from_width(file.getsampwidth()),
                    channels=file.getnchannels(),
                    rate=file.getframerate(),
                    output=True)

    stream.write(file.readframes(-1))

    stream.stop_stream()
    stream.close()
    file.close()


def play_sound(filename):
    # func = lambda: winsound.PlaySound(file, winsound.SND_FILENAME)

    thread = threading.Thread(target=play_sound_and_wait, args=(filename,), daemon=True)
    thread.start()
