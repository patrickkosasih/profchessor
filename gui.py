import tkinter as tk
from PIL import Image, ImageTk

import shared
import sprites

PIECE_SPRITE_GROUP = sprites.PieceSpriteGroup("sprites/piece_map.json")


class Piece:
    def __init__(self, board: tk.Canvas, piece_type, square):
        if piece_type not in shared.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        self.piece_type = piece_type
        self.square = square

        # Load image
        # self.image = Image.open("sprites/black rook.png").resize((size, size))
        # self.sprite = ImageTk.PhotoImage(self.image)

        # self.canvas_item = canvas.create_rectangle(69, 69, 420, 420, fill="green")
        sprite = PIECE_SPRITE_GROUP.piece_to_sprite(piece_type)
        self.canvas_item = board.create_image(*square.get_center(), image=sprite, anchor=tk.CENTER)


    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Piece(type={self.piece_type})"


class Square:
    def __init__(self, board: tk.Canvas, i, size):
        self.i = i
        self.coordinate = chr(ord("a") + i % 8) + str(8 - i // 8)  # The standard chess coordinate
        self.size = size

        # Set up canvas square
        x, y = i % 8, i // 8
        color = shared.LIGHT_SQUARE_COLOR if (x + y) % 2 == 0 else shared.DARK_SQUARE_COLOR
        self.canvas_item = board.create_rectangle(x * size, y * size, (x + 1) * size, (y + 1) * size,
                                                  fill=color, outline="")

    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Square(i={self.i}, coordinate={self.coordinate})"

    def get_center(self):
        return (self.i % 8 + 0.5) * self.size, (self.i // 8 + 0.5) * self.size


class Board(tk.Canvas):
    def __init__(self, root, size, **kw):
        super(Board, self).__init__(root, width=size, height=size, highlightthickness=0, **kw)

        self.root = root
        self.board_size = int(size)
        self.square_size = self.board_size / 8

        self.squares = [Square(self, i, self.square_size) for i in range(64)]

        self.bind("<Button-1>", self.mouse_click)
        self.bind("<B1-Motion>", self.mouse_motion)
        self.bind("<ButtonRelease-1>", self.mouse_release)

        # Test stuff
        self.one_piece = Piece(self, "p", self.squares[0])

    def square_cursor(self, x, y):
        """
        Returns the square that the mouse cursor (or any xy coordinate) is currently on
        """
        sqx, sqy = int(x // self.square_size), int(y // self.square_size)
        return self.squares[sqx + sqy * 8]

    """
    Mouse event methods
    """
    def mouse_click(self, event):
        # print(f"Click x: {event.x}, y: {event.y}")
        print(self.square_cursor(event.x, event.y))

    def mouse_motion(self, event):
        # print(f"Motion x: {event.x}, y: {event.y}")
        # self.itemconfig(int(self.square_cursor(event.x, event.y)), fill="black")
        pass

    def mouse_release(self, event):
        # print(f"Release x: {event.x}, y: {event.y}")
        pass



class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        self.geometry("800x800")
        self.configure(bg=shared.BG_COLOR)
        self.wm_iconphoto(False, tk.PhotoImage(file="sprites/black pawn.png"))

        # self.wm_attributes("-fullscreen", True)  # Fullscreen
        self.state("zoomed")  # Maximized

        self.board = Board(self, size=self.winfo_screenheight() * 0.75)
        # self.board = Board(self, size=700)

        self.board.pack(anchor="center", expand=True)
