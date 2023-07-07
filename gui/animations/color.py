"""
gui/animations/color.py

A module containing animations of changing the color or opacity of a certain GUI component.
"""

from abc import ABC
from typing import Callable

from .animation import Animation
from .frames import FrameAnimation

from gui.shared_gui import rgb_hex_to_int, mix_color


class FadeColorAnimation(Animation, ABC):
    def __init__(self, duration,
                 update: Callable[[tuple], None], start_color: tuple or str, end_color: tuple or str,
                 *args, **kwargs):
        """
        :param update: The update function that is called every tick. The current color (tuple) is passed in as an
        argument of the update function.

        :param start_color: Starting color.
        :param end_color: Color after animation.

        `start_color` and `end_color` can be a string of "#RRGGBB" format, or a tuple of (R, G, B) format.
        """

        super().__init__(duration, *args, **kwargs)

        self.update = update
        self.start_color = start_color if type(start_color) is tuple else rgb_hex_to_int(start_color)
        self.end_color = end_color if type(end_color) is tuple else rgb_hex_to_int(end_color)

    def tick(self):
        current_color = mix_color(self.start_color, self.end_color, self.phase)
        self.update(current_color)

    def finished(self):
        self.update(self.end_color)


class FadeAlphaAnimation(FrameAnimation, ABC):
    pass
