import threading
import time
from abc import ABC, abstractmethod


class Animation(ABC):
    def __init__(self, duration, fps=120, min_phase=0, max_phase=1):
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

    @abstractmethod
    def tick(self):
        pass

# Example "animation"

# class Thingy(Animation, ABC):
#     def __init__(self, duration, *args, **kwargs):
#         super().__init__(duration)
#
#     def tick(self):
#         print(self.phase)
#
#
# Thingy(1).start()
# time.sleep(2)
