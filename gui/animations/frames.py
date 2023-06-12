"""
gui/animations/frames.py

The python module that handles frame animations.

Frame animations are animations that runs based on updating the PhotoImage of a canvas item / widget every single frame.
Frame animations uses the `FrameBuffer` class as its base.

Note: Frame animations are still in an unstable state. Bugs may arise.
"""
import threading
from abc import ABC, abstractmethod
from typing import Callable
from PIL import Image, ImageTk

import debug
from gui.animations.animation import Animation, Interpolations
from gui.sprites import SpriteGroup


class FrameBuffer(SpriteGroup):
    """
    Frame buffers are the bases of frame animations. It enables generating and storing `PhotoImage` instances for each
    of the frames of an animation.
    """

    def __init__(self, generator: Callable[[int], ImageTk.PhotoImage], n_frames: int):
        """
        :param generator:
        :param n_frames:
        """

        super().__init__()

        if not callable(generator):
            raise ValueError("generator argument must be callable")

        self.generator = generator
        self.n_frames = n_frames

    @debug.func_timer
    def generate_frames(self):
        for i in range(self.n_frames):
            self.add_photo(i, self.generator(i))

    def get_frame(self, i: int):
        if i not in range(self.n_frames + 1):
            raise ValueError(f"frame index is out of bounds: {i}")

        return self.add_photo(i, self.generator(i))

# Example frame buffer thing
#
# Tk()
# ack = FrameBuffer(generator=lambda x: gui.shared_gui.translucent_rectangle(x / 60, 50, 50), n_frames=60)
# ack.generate_frames()
# print(ack.sprite_dict)
# print(sys.getsizeof(ack.sprite_dict))


class FrameAnimation(Animation, ABC):
    """
    FrameAnimation is the base class for a frame animation class.
    """

    def __init__(self, duration, generator: Callable[[int], ImageTk.PhotoImage], original_photo: ImageTk.PhotoImage,
                 *args, **kwargs):
        super().__init__(duration, *args, **kwargs)

        self.frame_buffer = FrameBuffer(generator, n_frames=int(self.duration * self.fps))
        self.n_frame = 0

        self.original_image: Image = ImageTk.getimage(original_photo)
        self.current_photo: ImageTk.PhotoImage = original_photo

        self.generator_thread = threading.Thread(target=self.frame_buffer.generate_frames, daemon=True)

    @abstractmethod
    def generator(self, frame) -> ImageTk.PhotoImage:
        pass

    def tick(self):
        self.n_frame = int(self.phase * self.fps * self.duration)
        self.current_photo = self.frame_buffer.get_frame(self.n_frame)


class ScalePieceAnimation(FrameAnimation, ABC):
    def __init__(self, duration, original_photo: ImageTk.PhotoImage,
                 board, piece: int,
                 start_size: int or None, end_size: int, interpolation=Interpolations.ease_out,
                 *args, **kwargs):
        """
        :param board: The board GUI (subclass of tk.Canvas).
        :param piece: The canvas item ID of the piece GUI.
        :param start_size: The size before the animation starts playing.
        :param end_size: The size to scale to.
        :param interpolation: The interpolation function which converts the phase into the interpolation phase.
                              Defaults to linear interpolation.
        """

        super().__init__(duration, self.generator, original_photo, *args, **kwargs)

        self.board = board
        self.piece = piece

        self.start_size = start_size if start_size is not None else original_photo.height()
        self.end_size = end_size
        self.interpolation = interpolation

        # self.generator_thread.start()

    def generator(self, frame: int) -> ImageTk.PhotoImage:
        size = int(self.start_size + self.interpolation(self.phase) * (self.end_size - self.start_size))
        size = max(1, size)

        resized: Image = self.original_image.resize((size, size))

        return ImageTk.PhotoImage(resized)

    def tick(self):
        super().tick()

        self.board.itemconfig(self.piece, image=self.current_photo)

    def finished(self):
        if self.end_size == 0:
            self.board.delete(self.piece)
