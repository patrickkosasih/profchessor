"""
gui/animations/animation.py

The Python module that contains the Animation base class and other shared classes and functions for creating animations.
"""

import threading
import time
from abc import ABC, abstractmethod


class Animation(ABC):
    def __init__(self, duration, fps=60, min_phase=0, max_phase=1):
        self.duration = duration
        self.fps = fps
        self.period = 1 / fps

        self.min_phase = min_phase
        self.max_phase = max_phase

        self.phase = min_phase
        self.running = False

        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        last_tick = time.time()

        while self.running and self.phase < self.max_phase:
            dt = time.time() - last_tick

            if dt >= self.period:
                self.tick()
                self.phase += (dt / self.duration) * (self.max_phase - self.min_phase)
                last_tick += self.period

        self.phase = self.max_phase
        self.tick()
        self.finished()

    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def finished(self):
        pass


class Interpolations:
    linear = lambda x: x
    ease_out = lambda x: -(x * x) + 2 * x  # Simple ease out function: f(x) = -x^2 + 2x
