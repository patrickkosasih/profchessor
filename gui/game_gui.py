import tkinter as tk

import gui.audio
import rules
import debug
from gui import sprites, shared_gui
from gui.animations.move import *

BG_COLOR = "#2b3030"
DARK_SQUARE_COLOR = "#855313"
LIGHT_SQUARE_COLOR = "#ffe4ad"
DEFAULT_FADER_COLOR = "#14110a"


class Piece:
    psg = sprites.PieceSpriteGroup("data/sprites/pieces/piece_map.json")

    def __init__(self, board: tk.Canvas, piece_type, square, bind_to_square=True):
        if piece_type not in rules.PIECE_TYPES:
            raise ValueError(f"invalid piece type \"{piece_type}\"")

        self.piece_type = piece_type
        self.board = board
        self.square = square

        if bind_to_square:
            self.square.piece = self

        Piece.psg.piece_size = int(self.square.size * 0.9)
        sprite = Piece.psg.piece_to_sprite(piece_type)
        self.canvas_item = board.create_image(*square.get_center(), image=sprite, anchor=tk.CENTER)

        self.animation = None

    def __int__(self):
        return self.canvas_item

    def __str__(self):
        return f"Piece(type={self.piece_type})"

    def move(self, x, y, duration=0, interpolation=Interpolations.quadratic):
        if duration == 0:
            # Direct movement
            self.board.coords(self.canvas_item, x, y)
        else:
            # Animated movement
            self.animation = MovePieceAnimation(duration, self.board, self.canvas_item, (), (x, y), interpolation)
            self.animation.start()

    def move_to_square(self, new_square, duration=0):
        self.move(*new_square.get_center(), duration)

        if new_square is self.square:
            return

        old_square = self.square

        new_square.remove_piece()
        self.square = new_square

        new_square.piece = self
        old_square.piece = None

    def set_piece_type(self, piece_type):
        self.piece_type = piece_type

        sprite = Piece.psg.piece_to_sprite(piece_type)
        self.board.itemconfig(self.canvas_item, image=sprite)

    def set_hidden(self, hidden):
        self.board.itemconfig(self.canvas_item, state="hidden" if hidden else "normal")


class Square:
    def __init__(self, board: tk.Canvas, i, size):
        self.board = board
        self.i = i
        self.coordinate = rules.i_to_coordinate(i)
        self.size = size
        self.piece = None

        # Set up canvas square
        x, y = i % 8, i // 8
        self.default_color = LIGHT_SQUARE_COLOR if (x + y) % 2 == 0 else DARK_SQUARE_COLOR
        self.canvas_item = board.create_rectangle(x * size, y * size, (x + 1) * size, (y + 1) * size,
                                                  fill=self.default_color, outline="")

        # Debug text that shows the index of the square
        if debug.DEBUG_LEVEL:
            board.create_text(x * size + 10, y * size + 10, text=i)

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


class PromotionPrompt:
    WHITE_PIECES = ("Q", "R", "N", "B")
    BLACK_PIECES = ("q", "r", "n", "b")

    LIGHT_FRAME_COLOR = "#e8ddc3"
    DARK_FRAME_COLOR = "#544123"

    def __init__(self, board, new_square: Square, pawn: Piece):
        assert pawn.piece_type in ("P", "p"), "piece must be a pawn"
        assert new_square.i // 8 in (0, 7), "pawn must be in the topmost or bottommost rank"

        """
        Attributes from passed in arguments
        """
        self.board = board
        self.new_square = new_square
        self.pawn = pawn

        """
        Configure board
        """
        self.pawn.set_hidden(True)
        board.set_fader(0.3)
        board.enable_drag_and_drop = False

        """
        Piece buttons
        """
        # Determine the color of the piece buttons and the offset
        if pawn.piece_type.isupper():
            # White
            pieces_by_color = PromotionPrompt.WHITE_PIECES
            frame_color = PromotionPrompt.DARK_FRAME_COLOR
            offset = 8
        else:
            # Black
            pieces_by_color = PromotionPrompt.BLACK_PIECES
            frame_color = PromotionPrompt.LIGHT_FRAME_COLOR
            offset = -8

        self.button_frame_photo = shared_gui.translucent_rectangle(0.9, board.square_size,board.square_size, frame_color)
        self.pieces = {}
        self.button_frames = {}  # The button frames are just faded rectangles

        for i, piece in zip(range(new_square.i, new_square.i + offset * 4, offset), pieces_by_color):
            self.button_frames[i] = board.create_image(*board.squares[i].get_center(),
                                                       image=self.button_frame_photo, anchor=tk.CENTER)
            self.pieces[i] = Piece(board, piece, board.squares[i], bind_to_square=False)

    def mouse_click(self, clicked_square: Square):
        if clicked_square and clicked_square.i in self.pieces:
            new_piece_type = self.pieces[clicked_square.i].piece_type

            """
            Make the move on the ChessGame
            """
            move_result_int = self.board.game.move(old=self.pawn.square.i, new=self.new_square.i,
                                                   promote_to=new_piece_type)
            self.board.move_sfx(rules.MoveResult(move_result_int))

            """
            Configure the pawn GUI:
            Move the GUI pawn, turn it into the new piece type, and unhide it
            """
            self.pawn.move_to_square(self.new_square)
            self.pawn.set_piece_type(new_piece_type)
            self.pawn.set_hidden(False)

        else:
            """
            The mouse clicks outside the promotion buttons: Cancel the promotion move
            """
            self.pawn.set_hidden(False)

        """
        Delete all the buttons of the promotion prompt
        """
        for frame, piece in zip(self.button_frames.values(), self.pieces.values()):
            self.board.delete(frame)
            self.board.delete(piece.canvas_item)

        """
        Configure board
        """
        self.board.set_fader(0)
        self.board.enable_drag_and_drop = True
        self.board.promotion_prompt = None  # "Delete" self


class Board(tk.Canvas):
    def __init__(self, root, game, size, **kw):
        super(Board, self).__init__(root, width=size, height=size, highlightthickness=0, **kw)

        """
        Attributes from the passed in arguments
        """
        self.game = game
        self.root = root
        self.board_size = int(size)
        self.square_size = self.board_size // 8

        """
        General GUI attributes
        """
        self.squares = [Square(self, i, self.square_size) for i in range(64)]
        self.flipped = False

        self.sg = sprites.SpriteGroup()
        self.fader = None
        self.promotion_prompt = None

        self.game_over_text = self.create_text(size / 2, size * 0.425, text="", font=("Calibri", int(size * 0.125)),
                                               fill="white", anchor=tk.CENTER)
        self.game_over_subtext = self.create_text(size / 2, size * 0.575, text="", font=("Calibri", int(size * 0.05)),
                                                  fill="white", anchor=tk.CENTER)

        """
        Drag and drop attributes
        """
        self.enable_drag_and_drop = True
        self.dragging = None  # Piece that's currently being dragged
        self.move_markers = []

        """
        Bind mouse events
        """
        self.bind("<Button-1>", self.mouse_down)
        self.bind("<B1-Motion>", self.mouse_motion)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.bind("<Button-3>", self.right_mouse_click)

        self.reset_board(self.game.board)

        # Test stuff
        # pixel_thing = self.sg.open("sprites/translucent pixel thing.png", size=2 * (self.board_size,))
        # self.fg_thing = self.create_image(0, 0, image=pixel_thing, anchor="nw")

    """
    General GUI methods
    """
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

    def game_over_screen(self):
        if not self.game.game_result:
            return

        self.set_fader(0.5)
        self.enable_drag_and_drop = False

        match self.game.game_result.winner:
            case rules.GameResult.WHITE_WINS:
                winner = "White Wins!"
            case rules.GameResult.BLACK_WINS:
                winner = "Black Wins!"
            case rules.GameResult.DRAW:
                winner = "Draw!"
            case _:
                winner = "wtf?"

        details = rules.GameResult.DETAILS_STR[self.game.game_result.details]
        details = details[0].upper() + details[1:]  # Capitalize first letter

        self.itemconfig(self.game_over_text, text=winner)
        self.itemconfig(self.game_over_subtext, text=details)
        self.lift(self.game_over_text)
        self.lift(self.game_over_subtext)

    def set_fader(self, opacity):
        translucent_fg = self.sg.add_photo("translucent_fg",
                                           shared_gui.translucent_rectangle(opacity, self.board_size,
                                                                            self.board_size, DEFAULT_FADER_COLOR))
        self.fader = self.create_image(0, 0, image=translucent_fg, anchor="nw")

    def move_sfx(self, move_result: rules.MoveResult):
        # Primary SFX
        if move_result.capture:
            gui.audio.play_sound("capture.wav")

        elif move_result.special:
            gui.audio.play_sound("castle.wav")

        elif move_result.move_made:
            gui.audio.play_sound("move.wav")

        # Secondary SFX
        if move_result.move_made:
            if move_result.check:
                if move_result.game_over:
                    gui.audio.play_sound("checkmate.wav")
                else:
                    gui.audio.play_sound("check.wav")

            if move_result.promotion:
                gui.audio.play_sound("promotion.wav")


    """
    Mouse actions
    """
    def move_piece(self, piece: Piece, new_square: Square):
        """
        Moves a piece. Before moving a piece, this method checks the GUI conditions for a piece to move, and then runs
        the move method in the ChessGame instance with the correct arguments. Based on the move results, if the move is
        legal, then the gui piece is moved, and if the move result is to ask the promoting piece, a promotion prompt
        is created.
        """

        cancel_move = True
        self.unmark_moves()

        if self.dragging and new_square:
            move_result = self.game.move(self.dragging.square.i, new_square.i)

            if move_result.move_made:
                """
                Make the move
                """
                self.dragging.move_to_square(new_square, duration=0.1)

                cancel_move = False
                self.dragging = None

                if move_result.game_over:
                    self.game_over_screen()

            elif move_result.promotion:
                """
                Create a promotion prompt
                """
                self.promotion_prompt = PromotionPrompt(self, new_square, piece)

            if cancel_move:
                self.cancel_move()  # Put back piece to original square and self.dragging = None

            """
            Sound effects
            """
            self.move_sfx(move_result)

    def get_square_on_pos(self, x, y):
        """
        Returns the square that is on a specified position relative to the board
        Returns None if position is out of bounds
        """
        if not (0 < x < self.board_size and 0 < y < self.board_size):
            return None

        sqx, sqy = int(x // self.square_size), int(y // self.square_size)
        return self.squares[sqx + sqy * 8]

    def cancel_move(self):
        if self.dragging:
            self.dragging.move_to_square(self.dragging.square, duration=0.2)
            self.dragging = None

    def mark_moves(self, square: int):
        size = int(self.square_size)

        if square in self.game.legal_moves:
            for move_to in self.game.legal_moves[square]:
                x, y = self.squares[move_to].get_center()

                if self.squares[move_to].piece:
                    image = self.sg.open("data/sprites/capture marker.png", size=(size, size))
                else:
                    image = self.sg.open("data/sprites/move marker.png", size=(size, size))

                marker = self.create_image(x, y, image=image, anchor="center")

                self.move_markers.append(marker)

    def unmark_moves(self):
        for x in self.move_markers:
            self.delete(x)

        self.move_markers = []

    """
    Mouse event methods
    """
    def mouse_down(self, event):
        if self.enable_drag_and_drop:
            self.dragging = self.get_square_on_pos(event.x, event.y).piece

            if self.dragging:
                self.dragging.move(event.x, event.y)
                self.mark_moves(self.dragging.square.i)
                self.lift(self.dragging.canvas_item)  # Order dragging piece to the topmost layer

    def mouse_motion(self, event):
        if self.dragging:
            self.dragging.move(event.x, event.y)

    def mouse_release(self, event):
        """
        Releasing the mouse while dragging a piece makes a move on the chess board
        """
        square_on_cursor = self.get_square_on_pos(event.x, event.y)

        if self.promotion_prompt:
            self.promotion_prompt.mouse_click(square_on_cursor)
        else:
            self.move_piece(self.dragging, square_on_cursor)

    def right_mouse_click(self, event):
        self.unmark_moves()
        self.cancel_move()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profchessor")
        self.geometry("800x800")
        self.configure(bg=BG_COLOR)
        self.iconbitmap("data/sprites/icon.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)

        if not debug.DEBUG_LEVEL:
            self.wm_attributes("-fullscreen", True)  # Fullscreen
            # self.state("zoomed")  # Maximized

        # Testing stuff
        fen = ""
        # fen = "r4k2/p1pnqp2/1p1b3p/8/2pP2Q1/1P3NP1/P3r2P/R1B2RK1 w - - 1 23"
        # fen = "8/8/8/8/8/pk2n3/8/K7 b - - 3 65"
        # fen = "8/8/8/8/3q1k2/8/2n5/5K2 b - - 13 74"
        # fen = "7k/5p2/8/K3P1r1/8/8/8/8 b - - 0 1"
        # fen = "7k/3p4/8/K3P1r1/8/8/8/8 b - - 0 1"
        # fen = "r2qkbnr/pp1npppp/2p1b3/3p4/7N/1P2P3/PBPP1PPP/RN1QKB1R w KQkq - 3 6"
        # fen = "r1b3k1/pp3pp1/3B4/3p1P1p/8/1P1P1N1P/P2P1qP1/4R2K w - - 2 26"
        # fen = "7k/pr4p1/2n1N2p/b2N1Q2/2BP4/P3P2P/5RP1/2KR4 w - - 1 29"
        # fen = "5K2/P7/8/8/8/8/7p/5k2 w - - 0 1"

        self.game = rules.ChessGame(fen)

        self.board = Board(self, self.game, size=self.winfo_height() * 0.8)
        self.game.board_gui = self.board
        # self.board = Board(self, size=700)

        self.board.pack(anchor="center", expand=True)

    def close(self):
        gui.audio.p.terminate()
        self.destroy()
