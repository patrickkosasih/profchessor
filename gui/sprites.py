"""
sprites.py

The module that stores multiple PhotoImage objects into a sprite group in order to store PhotoImage objects globally
with ease. PhotoImage objects must be a global variable/attribute, otherwise Tkinter won't display the image.
"""

from PIL import Image, ImageTk
import os
import json


class SpriteGroup:
    """
    SpriteGroup is used to create a PhotoImage object and store it on a dictionary
    An instance of this class should be created globally, because objects that stored locally are deleted once the
    function call ends, which can cause images to not display properly on the Tkinter window.
    """

    def __init__(self):
        self.sprite_dict = {}

    def open(self, path: str, size: tuple=None):
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

    def add_photo(self, name, photo: ImageTk.PhotoImage=None):
        """
        Adds a PhotoImage object to the sprite dict of the sprite group
        The newly added photo is also returned
        """

        if photo:
            self.sprite_dict[name] = photo

        return self.sprite_dict[name]


class PieceSpriteGroup(SpriteGroup):
    """
    PieceSpriteGroup is used to easily access PhotoImage objects based on a given piece type
    """

    def __init__(self, piece_map, piece_size=100):
        """
        :param piece_map: The JSON file that contains the {piece: file path} pairs
        """
        super().__init__()

        # Attributes
        self.piece_size = piece_size

        # Load the json file into a dictionary
        with open(piece_map, "r") as f:
            self.sprite_paths = json.loads(f.read())

        # Add the root dictionary of the json file to the file paths
        piece_map_dir = os.path.dirname(piece_map)
        for k in self.sprite_paths:
            self.sprite_paths[k] = os.path.join(piece_map_dir, self.sprite_paths[k])

    def piece_to_sprite(self, piece_type):
        return self.open(self.sprite_paths[piece_type], (self.piece_size, self.piece_size))

    def resize_all(self, size):
        if size == self.piece_size:
            return

        self.piece_size = size

        for x in self.sprite_dict:
            original = ImageTk.getimage(self.sprite_dict[x])  # PIL.Image object
            resized = original.resize((size, size))
            resized_photo = ImageTk.PhotoImage(resized)

            self.sprite_dict[x] = resized_photo
