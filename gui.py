import tkinter as tk

import shared


class Piece(tk.Label):  # Still uses letters to represent the piece type
    def __init__(self, master, piece_type, **kwargs):
        super().__init__(master, **kwargs)

        if piece_type not in shared.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        self.configure(text=piece_type, font=("Arial", 24))


class Square(tk.Frame):
    def __init__(self, master, i, size, **kw):
        super().__init__(master, **kw)

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
    def __init__(self, master, size, **kw):
        super(Board, self).__init__(master, width=size, height=size, **kw)

        self.squares = [Square(self, i, size=size // 8) for i in range(64)]

        Piece(self.squares[0], "Q").pack()


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        # self.geometry("800x800")
        self.configure(bg=shared.BG_COLOR)
        #self.wm_attributes("-fullscreen", True)  # Fullscreen

        self.board = Board(self, size=self.winfo_screenheight() * 0.8)
        self.board.pack(anchor="center", expand=True)
