import tkinter as tk

import chess
import shared
import sprites

BG_COLOR = "#2b3030"
DARK_SQUARE_COLOR = "#855313"
LIGHT_SQUARE_COLOR = "#ffe4ad"

PIECE_SPRITE_GROUP = sprites.PieceSpriteGroup("sprites/pieces/piece_map.json")


class Piece:
    def __init__(self, board: tk.Canvas, piece_type, square):
        if piece_type not in chess.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        self.piece_type = piece_type
        self.board = board
        self.square = square

        self.square.piece = self

        # self.canvas_item = canvas.create_rectangle(69, 69, 420, 420, fill="green")
        sprite = PIECE_SPRITE_GROUP.piece_to_sprite(piece_type)
        self.canvas_item = board.create_image(*square.get_center(), image=sprite, anchor="center")

    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Piece(type={self.piece_type})"

    def move_center(self, x, y):
        ctr_x = x - self.square.size / 2
        ctr_y = y - self.square.size / 2
        self.board.moveto(self.canvas_item, ctr_x, ctr_y)

    def move_to_square(self, new_square):
        self.move_center(*new_square.get_center())

        if new_square is self.square:
            return

        old_square = self.square

        new_square.remove_piece()
        self.square = new_square

        new_square.piece = self
        old_square.piece = None


class Square:
    def __init__(self, board: tk.Canvas, i, size):
        self.board = board
        self.i = i
        self.coordinate = chr(ord("a") + i % 8) + str(8 - i // 8)  # The standard chess coordinate
        self.size = size
        self.piece = None

        # Set up canvas square
        x, y = i % 8, i // 8
        color = LIGHT_SQUARE_COLOR if (x + y) % 2 == 0 else DARK_SQUARE_COLOR
        self.canvas_item = board.create_rectangle(x * size, y * size, (x + 1) * size, (y + 1) * size,
                                                  fill=color, outline="")

    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Square(i={self.i}, coordinate={self.coordinate})"

    def remove_piece(self):
        if self.piece:
            self.piece.square = None
            self.board.delete(int(self.piece))
            self.piece = None

    def get_center(self):
        return (self.i % 8 + 0.5) * self.size, (self.i // 8 + 0.5) * self.size


class Board(tk.Canvas):
    def __init__(self, root, game, size, **kw):
        super(Board, self).__init__(root, width=size, height=size, highlightthickness=0, **kw)

        self.root = root
        self.board_size = int(size)
        self.square_size = self.board_size / 8

        self.squares = [Square(self, i, self.square_size) for i in range(64)]

        self.dragging = None  # Piece that's currently being dragged

        self.game = game
        self.load_board(self.game.board)

        # Mouse events
        self.bind("<Button-1>", self.mouse_click)
        self.bind("<B1-Motion>", self.mouse_motion)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.bind("<Button-3>", self.right_mouse_click)

        # Test stuff
        # self.one_piece = Piece(self, "B", self.squares[0])

    def load_board(self, board_data: list[64]):
        for piece_type, gui_square in zip(board_data, self.squares):
            if piece_type:
                gui_square = Piece(self, piece_type, gui_square)

    def output_move(self, piece, new_square):
        pass

    def get_square_on_pos(self, x, y):
        """
        Returns the square that is on a specified position relative to the board
        Returns None if position is out of bounds
        """
        if not (0 < x < self.board_size and 0 < y < self.board_size):
            return None

        sqx, sqy = int(x // self.square_size), int(y // self.square_size)
        return self.squares[sqx + sqy * 8]

    """
    Drag and drop methods
    """
    def move_piece(self, new_square):
        self.dragging.move_to_square(new_square)
        self.dragging = None

    def cancel_move(self):
        self.dragging.move_to_square(self.dragging.square)
        self.dragging = None

    """
    Mouse event methods (directly bound to mouse)
    """
    def mouse_click(self, event):
        self.dragging = self.get_square_on_pos(event.x, event.y).piece
        if self.dragging:
            self.dragging.move_center(event.x, event.y)

    def mouse_motion(self, event):
        if self.dragging:
            self.dragging.move_center(event.x, event.y)

    def mouse_release(self, event):
        square = self.get_square_on_pos(event.x, event.y)

        if self.dragging and square:
            # Move piece
            self.move_piece(square)
        else:
            self.cancel_move()

    def right_mouse_click(self, event):
        if self.dragging:
            self.cancel_move()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        self.geometry("800x800")
        self.configure(bg=BG_COLOR)
        self.wm_iconphoto(False, tk.PhotoImage(file="sprites/pieces/black pawn.png"))

        # self.wm_attributes("-fullscreen", True)  # Fullscreen
        self.state("zoomed")  # Maximized

        self.game = chess.ChessGame()
        self.board = Board(self, self.game, size=self.winfo_height() * 0.75)
        # self.board = Board(self, size=700)

        self.board.pack(anchor="center", expand=True)
