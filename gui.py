import tkinter as tk
from PIL import Image, ImageTk
import os

import shared


class Piece(tk.Label):
    def __init__(self, board, piece_type, **kw):
        super().__init__(board, **kw)

        if piece_type not in shared.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        # Mouse related variables
        self.dragging = False  # True if piece is being dragged by the mouse
        self.position_before = (0, 0)  # Position before being dragged

        # Load image
        piece_size = board.board_size // 8
        image = Image.open("sprites/black pawn.png").resize((piece_size, piece_size))
        self.sprite = ImageTk.PhotoImage(image)

        self.configure(image=self.sprite)

        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<B1-Motion>", self.on_move)

    def place_center(self, x, y, **kw):
        # Calculate the top left coordinate
        tl_x = x - self.winfo_width() // 2
        tl_y = y - self.winfo_height() // 2

        self.place(x=tl_x, y=tl_y, **kw)

    def on_click(self, event):
        self.dragging = True
        self.position_before = (self.winfo_rootx(), self.winfo_rooty())

        print("click", event.x, event.y)

        x, y = event.x, event.y
        self.position_before = x, y
        self.place_center(x=x, y=y)

    def on_release(self, event):
        print("release")
        self.dragging = False

    def on_move(self, event):
        x, y = event.x, event.y

        self.place_center(x=x, y=y)


class Square(tk.Frame):
    def __init__(self, board, i, size, **kw):
        super().__init__(board, **kw)

        self.i = i
        self.coordinate = chr(ord("a") + i % 8) + str(8 - i // 8)

        color = shared.LIGHT_SQUARE_COLOR if (i + i // 8) % 2 == 0 else shared.DARK_SQUARE_COLOR
        self.configure(bg=color, width=size, height=size)

        self.bind("<Button-1>", self.on_click)

        self.grid(column=i % 8, row=i // 8)

    def __repr__(self):
        return f"Square(i={self.i}, coordinate={self.coordinate})"

    def on_click(self, event):
        print(self.__repr__())


class Board(tk.Frame):
    def __init__(self, root, size, **kw):
        super(Board, self).__init__(root, width=size, height=size, **kw)

        self.squares = [Square(self, i, size=int(size) // 8) for i in range(64)]
        self.root = root
        self.board_size = int(size)

        piece_test = Piece(self, "Q")
        x, y = self.squares[40].winfo_x(), self.squares[40].winfo_y()
        piece_test.place(x=x, y=y)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        # self.geometry("800x800")
        self.configure(bg=shared.BG_COLOR)
        # self.wm_attributes("-fullscreen", True)  # Fullscreen

        self.board = Board(self, size=self.winfo_screenheight() * 0.8)
        self.board.pack(anchor="center", expand=True)
