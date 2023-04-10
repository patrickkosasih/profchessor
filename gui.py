import tkinter as tk

import ruleset
import sprites

BG_COLOR = "#2b3030"
DARK_SQUARE_COLOR = "#855313"
LIGHT_SQUARE_COLOR = "#ffe4ad"


class Piece:
    psg = sprites.PieceSpriteGroup("sprites/pieces/piece_map.json")

    def __init__(self, board: tk.Canvas, piece_type, square):
        if piece_type not in ruleset.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        self.piece_type = piece_type
        self.board = board
        self.square = square

        self.square.piece = self

        Piece.psg.piece_size = int(self.square.size * 0.9)
        sprite = Piece.psg.piece_to_sprite(piece_type)
        self.canvas_item = board.create_image(*square.get_center(), image=sprite, anchor="center")

    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Piece(type={self.piece_type})"

    def move_center(self, x, y):
        # ctr_x = x - self.square.size / 2
        # ctr_y = y - self.square.size / 2
        # self.board.moveto(self.canvas_item, ctr_x, ctr_y)
        self.board.coords(self.canvas_item, x, y)

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
        self.coordinate = ruleset.i_to_coordinate(i)
        self.size = size
        self.piece = None

        # Set up canvas square
        x, y = i % 8, i // 8
        self.default_color = LIGHT_SQUARE_COLOR if (x + y) % 2 == 0 else DARK_SQUARE_COLOR
        self.canvas_item = board.create_rectangle(x * size, y * size, (x + 1) * size, (y + 1) * size,
                                                  fill=self.default_color, outline="")

        # Debug text that shows the index of the square
        # board.create_text(x * size + 10, y * size + 10, text=i)

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

        self.game = game
        self.root = root
        self.board_size = int(size)
        self.square_size = self.board_size / 8

        self.squares = [Square(self, i, self.square_size) for i in range(64)]

        # Drag and drop stuff
        self.dragging = None  # Piece that's currently being dragged
        self.legal_move_markers = []

        self.reset_board(self.game.board)

        # Mouse events
        self.bind("<Button-1>", self.mouse_click)
        self.bind("<B1-Motion>", self.mouse_motion)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.bind("<Button-3>", self.right_mouse_click)

        # Test stuff
        # self.one_piece = Piece(self, "B", self.squares[0])

    def reset_board(self, board_data: list[64]):
        if self.dragging:
            self.delete(self.dragging.canvas_item)
            self.dragging = None

        for piece_type, gui_square in zip(board_data, self.squares):
            if gui_square.piece:
                self.delete(gui_square.piece.canvas_item)
                gui_square.piece = None

            if piece_type:
                Piece(self, piece_type, gui_square)

    def output_move(self, piece, new_square):
        # Coming soon: move a piece without the player's control when playing against the computer or another player
        pass

    """
    Drag and drop related methods
    """
    def get_square_on_pos(self, x, y):
        """
        Returns the square that is on a specified position relative to the board
        Returns None if position is out of bounds
        """
        if not (0 < x < self.board_size and 0 < y < self.board_size):
            return None

        sqx, sqy = int(x // self.square_size), int(y // self.square_size)
        return self.squares[sqx + sqy * 8]

    def move_piece(self, new_square):
        if self.dragging:
            self.dragging.move_to_square(new_square)
            self.dragging = None

    def cancel_move(self):
        if self.dragging:
            self.dragging.move_to_square(self.dragging.square)
            self.dragging = None

    def mark_legal_moves(self, square: int):
        r = 5

        if square in self.game.legal_moves:
            for move_to in self.game.legal_moves[square]:
                x, y = self.squares[move_to].get_center()
                marker = self.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="black")

                self.legal_move_markers.append(marker)

    def unmark_legal_moves(self):
        for x in self.legal_move_markers:
            self.delete(x)

        self.legal_move_markers = []

    """
    Mouse event methods
    """
    def mouse_click(self, event):
        self.dragging = self.get_square_on_pos(event.x, event.y).piece

        if self.dragging:
            self.dragging.move_center(event.x, event.y)
            self.mark_legal_moves(self.dragging.square.i)
            self.lift(self.dragging.canvas_item)  # Order dragging piece to the topmost layer

    def mouse_motion(self, event):
        if self.dragging:
            self.dragging.move_center(event.x, event.y)

    def mouse_release(self, event):
        cancel_move = True
        self.unmark_legal_moves()

        if self.dragging:
            new_square = self.get_square_on_pos(event.x, event.y)

            if new_square:
                move_result = self.game.move(self.dragging.square.i, new_square.i)

                if move_result != 0:
                    self.move_piece(new_square)
                    cancel_move = False

        if cancel_move:
            self.cancel_move()


    def right_mouse_click(self, event):
        self.unmark_legal_moves()

        if self.dragging:
            self.cancel_move()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        self.geometry("800x800")
        self.configure(bg=BG_COLOR)
        self.wm_iconphoto(False, tk.PhotoImage(file="sprites/pieces/black pawn.png"))

        self.wm_attributes("-fullscreen", True)  # Fullscreen
        # self.state("zoomed")  # Maximized

        # Testing stuff
        fen = ""
        # fen = "r4k2/p1pnqp2/1p1b3p/8/2pP2Q1/1P3NP1/P3r2P/R1B2RK1 w - - 1 23"
        # fen = "8/8/8/8/8/pk2n3/8/K7 b - - 3 65"
        # fen = "8/8/8/8/3q1k2/8/2n5/5K2 b - - 13 74"
        # fen = "7k/5p2/8/K3P1r1/8/8/8/8 b - - 0 1"
        # fen = "7k/3p4/8/K3P1r1/8/8/8/8 b - - 0 1"

        self.game = ruleset.ChessGame(fen)

        self.board = Board(self, self.game, size=self.winfo_height() * 0.8)
        self.game.board_gui = self.board
        # self.board = Board(self, size=700)

        self.board.pack(anchor="center", expand=True)
