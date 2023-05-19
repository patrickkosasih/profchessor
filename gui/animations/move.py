from abc import ABC
import tkinter as tk
import math

from gui.animations.animation import Animation


class Interpolations:
    linear = lambda x: x
    quadratic = lambda x: - (x * x) + 2 * x  # f(x) = -x^2 + 2x


class MovePieceAnimation(Animation, ABC):
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
        self.canvas_item = piece
        self.start_pos = start_pos if start_pos else board.coords(piece)
        self.end_pos = end_pos
        self.interpolation = interpolation

    def tick(self):
        interpol_phase = self.interpolation(self.phase)

        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * interpol_phase
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * interpol_phase

        self.board.coords(self.canvas_item, x, y)
        # self.board.root.update()
