"""
Note: PhotoImage objects must be a global variable/attribute, otherwise Tkinter won't display the image
"""

from PIL import Image, ImageTk
import os
import json


def create_translucent_rectangle(width, height, opacity: float, color=(0, 0, 0)):
    image = Image.new("RGBA", (width, height), (*color, int(opacity * 255)))
    photoimage = ImageTk.PhotoImage(image)

    return photoimage


class SpriteGroup:
    """
    SpriteGroup is used to create a PhotoImage object and store it on a dictionary
    An instance of this class is ought to be created globally, because objects that are stored locally are deleted
    once the function call ends, causing images to not display properly on the Tkinter window
    """

    def __init__(self):
        self.sprite_dict = {}

    def open(self, path, size: tuple=None):
        """
        Returns the PhotoImage instance of a specified image file.
        If the PhotoImage is already in the sprite group, then it returns the instance that already has been made
        Otherwise, create the PhotoImage object and add it to the dictionary.

        If the size argument (tuple) is passed in, then the image is resized to the specified size
        """
        if path not in self.sprite_dict:
            image = Image.open(path)
            if size:
                image = image.resize(size)
            self.sprite_dict[path] = ImageTk.PhotoImage(image)

        return self.sprite_dict[path]


class PieceSpriteGroup(SpriteGroup):
    """
    PieceSpriteGroup is used to easily access PhotoImage objects based on a given piece type
    """

    def __init__(self, piece_map):
        """
        :param piece_map: The JSON file that contains the {piece: file path} pairs
        """
        super().__init__()

        # Attributes
        self.piece_size = 60  # Coming soon: resize method that resizes all sprites

        # Load the json file into a dictionary
        with open(piece_map, "r") as f:
            self.sprite_paths = json.loads(f.read())

        # Add the root dictionary of the json file to the file paths
        piece_map_dir = os.path.dirname(piece_map)
        for k in self.sprite_paths:
            self.sprite_paths[k] = os.path.join(piece_map_dir, self.sprite_paths[k])

    def piece_to_sprite(self, piece_type):
        return self.open(self.sprite_paths[piece_type], (self.piece_size, self.piece_size))
