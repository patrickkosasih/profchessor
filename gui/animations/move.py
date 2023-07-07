"""
gui/animations/move.py

A module containing moving animations for pieces and soon other GUI widgets.
"""

from abc import ABC
import tkinter as tk
from math import sin, pi

from gui.animations.animation import Animation, Interpolations


class PieceMoveAnimation(Animation, ABC):
    def __init__(self, duration,
                 board, piece: int, start_pos: tuple, end_pos: tuple, interpolation=Interpolations.linear,
                 *args, **kwargs):
        """
        :param duration: The duration of the animation.

        MovePieceAnimation subclass attributes:
        :param board: The board GUI (subclass of tk.Canvas).
        :param piece: The canvas item ID of the piece GUI.
        :param start_pos: The starting position in (x, y) format, if an empty tuple is passed in then the starting
                          position is set to the current position of the piece.
        :param end_pos: The position to go to in (x, y) format.
        :param interpolation: The interpolation function which converts the phase into the interpolation phase.
                              Defaults to linear interpolation.
        """

        super().__init__(duration, *args, **kwargs)

        self.board = board
        self.piece = piece
        self.start_pos = start_pos if start_pos else board.coords(piece)
        self.end_pos = end_pos
        self.interpolation = interpolation

    def tick(self):
        interpol_phase = self.interpolation(self.phase)

        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * interpol_phase
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * interpol_phase

        self.board.coords(self.piece, x, y)
        # self.board.root.update()

    def finished(self):
        self.board.coords(self.piece, *self.end_pos)

class PieceWiggleAnimation(Animation, ABC):
    def __init__(self, duration,
                 board, piece: int, amp: float, freq: float,
                 *args, **kwargs):
        super().__init__(duration, *args, **kwargs)

        self.board = board
        self.piece = piece
        self.amp = amp
        self.original_pos = board.coords(piece)

        self.wiggle_func = lambda t: sin(pi * t) * sin(2 * pi * freq * t)
        """
        The wiggle function converts the animation phase into a value between -1 and 1 with 2 sine functions.
        The values "wiggle" back and forth in the desired frequency, with the wiggle going from weak, to strong, and
        to weak again.
        """

    def tick(self):
        wiggle_phase = self.wiggle_func(self.phase)

        x = self.original_pos[0] + self.amp * wiggle_phase
        y = self.original_pos[1]

        self.board.coords(self.piece, x, y)

    def finished(self):
        self.board.coords(self.piece, *self.original_pos)
