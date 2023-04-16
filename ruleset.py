"""
ruleset.py

The Python module that handles chess positions and makes sure that all the piece moves follow the rules of chess.

Terms that are used throughout the module:

* Square index      : A number representation for every square in a chess board that can be between 0 and 63 inclusive.
                      From white's perspective, square 0 would be in the top left corner (the a8 square) and increments
                      from left to right, and then top to bottom. That means the black pieces would start at squares
                      0-15 and white pieces on squares 48-63.

* Offset            : A number that is added to the square index everytime the tracer of a piece goes a step. Every
                      offset number of a piece represents a direction a piece can move to. For example, the offsets of
                      a rook are 1 (right), -1 (left), 8 (down), and -8 (up).

* Tracer            : An imaginary thing that starts from a piece and goes to one straight direction, which is the
                      offset. While doing so, the tracer "traces" a path that represents where a piece can move to.
                      On code, the tracer saves the squares a piece can move to onto a list known as the tracer path
                      while still following the rules of piece moves such as checks, pins, etc.

* Tracer piece      : While tracing a path, the tracer can encounter another piece which could be an enemy piece or an
                      ally (same colored) piece. That piece is referred as a tracer piece.

* Tracer path       : One of the paths/lines a piece can move to that is generated by a tracer. Each offset has its own
                      tracer path. On code, the tracer path is represented by a list of square indexes the piece can
                      move to for the current offset of the tracer. All the squares a piece can move to are all the
                      tracer path lists combined.

* Pin suspect       : When the tracer encounters an enemy piece while the controlling_only parameter is set to True, it
                      doesn't immediately stop tracing. Instead, the tracer continues tracing, and the piece it has
                      encountered is referred to as a pin suspect. On code, the pin suspect's square index is saved to
                      a variable called pin_suspect. More of pin suspects on phantom tracers' explanation.

* Phantom tracer    : Phantom tracers are related to pin suspects. When the tracer encounters an enemy piece while the
                      controlling_only parameter is set to True, the tracer becomes a phantom tracer and continues
                      tracing. Phantom tracers don't append empty squares to the tracer path, instead it appends it to
                      another list called squares_behind_suspect. When a phantom tracer reaches the enemy king, the
                      previously saved pin suspect has been confirmed to be pinned to the king. When a phantom tracer
                      meets a piece other than the enemy king, it stops tracing. On code, a tracer is a phantom tracer
                      when the pin_suspect variable is not -1.

* En passantable    : When a pawn moves 2 squares forward from its starting position, the square directly behind that
                      pawn becomes an en passantable square. An enemy pawn can then capture diagonally to the en
                      passantable square, which results in an en passant capture of the pawn that moved 2 squares from
                      earlier. Every position can only have 1 en passantable square, and if the move that is made for a
                      position wasn't a 2 square pawn push, then there is no en passantable square for the position
                      afterwards.

* En passant pin    : En passant pins are extremely rare cases where an en passant move discovers an attack from the
                      enemy that puts the king in check, making the move illegal.

* And many more chess terms...
"""
import copy
import time

import shared

"""
=======================
Chess ruleset constants
=======================
"""

PIECE_TYPES = ["P", "R", "N", "B", "Q", "K",
               "p", "r", "n", "b", "q", "k"]
"""
Piece types:

P = Pawn
R = Rook
N = Knight
B = Bishop
Q = Queen
K = King

Uppercase = White
Lowercase = Black
"""

STARTING_BOARD = list("rnbqkbnr") + ["p"] * 8 + [""] * 32 + ["P"] * 8 + list("RNBQKBNR")

MOVE_OFFSETS = {
    "P": [-8, -7, -9],  # White pawn
    "p": [8, 7, 9],     # Black pawn

    "R": [1, -1, 8, -8],
    "B": [7, -7, 9, -9],
    "N": [6, -6, 10, -10, 15, -15, 17, -17],
    "Q": [1, -1, 8, -8, 7, -7, 9, -9],
    "K": [1, -1, 8, -8, 7, -7, 9, -9]
}
"""
MOVE_OFFSETS is a dictionary containing the offset values of all the pieces.
Offset is the number that is added to the square index (the number of the square between 0-63) of a piece to generate
the squares it can move to.

Each offset of a piece is put into a "tracer", which is an imaginary thing that goes to one direction and "traces" a
line (marking the squares) that represent the squares a piece can move to

The king and knight only move 1 step at a time while the rook, bishop, and queen can move in a straight line that goes
as far as it can until it meets another piece or the edge or the board. Therefore, the tracer of a rook, bishop, and
queen is added by the offset values over and over again until it stops.

Unlike other pieces, the offsets of pawns are dependent on their colors ("P" and "p").

Pawns have 3 offsets for each color:
  p     P
* 8 or -8   : Pawn push
* 7 or -7   : Pawn capture
* 9 or -9   : Pawn capture
"""

CASTLING_SQUARES = {
    "K": [60, 61, 62, 63],
    "Q": [60, 59, 58, 56, 57],
    "k": [4, 5, 6, 7],
    "q": [4, 3, 2, 0, 1]
}
"""
CASTLING_SQUARES is a dictionary containing the key squares that is used on calculating castling moves and whether the
king can castle or not.

The letters on the dictionaries' key refer to the color and the side of castling. For example, "Q" is white queenside
castling and "k" is black kingside castling.

The numbers inside the lists refer to the following:
* Index 0: The king's original square
* Index 1: The square the king "passes through" when castling and the square the rook will end up on after castling
* Index 2: The square the king will end up on after castling
* Index 3: The rook's original square
* Index 4: The queenside knight's original square (exclusive to queenside castling ("Q" and "q"))
"""

class MoveResults:
    """
    MoveResults is a class containing the constants to classify a move result, which is returned by the move method on
    the Position class.

    This class only acts as a namespace and should not be instantiated as an object instance
    """
    ILLEGAL = 0
    MOVE = 1
    CAPTURE = 2
    CASTLE = 3
    EN_PASSANT = 4
    PROMOTION = 5
    PROMPT_PROMOTION = 6


"""
====================
Conversion functions
====================
"""
def i_to_xy(i: int):
    return i % 8, i // 8

def offset_to_xy(i: int):
    x, y = i % 8, i // 8
    if x > 4:
        x = x % -8
        y += 1

    return x, y

def i_to_coordinate(i: int):  # Standard chess coordinate
    return chr(ord("a") + i % 8) + str(8 - i // 8)


def coordinate_to_i(coor: str):
    if len(coor) != 2 or coor[0] not in "abcdefgh" or not 1 <= int(coor[1]) <= 8:
        raise ValueError(f"invalid coordinate \"{coor}\"")

    return ord(coor[0]) - ord("a") + (8 - int(coor[1]))


def hash_board(board: list):
    pass


"""
==============
Misc functions
==============
"""

def is_tracer_at_edge(tracer, offset):
    """
    This function is used on generating moves on a piece

    On sliding pieces (rooks, bishops, and queens), when the current "tracer" is on the edge of a board, and it goes out
    of bound if added a certain offset value, this function returns False and serves as a cue for the tracer to stop
    generating moves for the current direction of tracing

    On jumping pieces (knights and kings), if the square it is on added by the offset value is outside the board, this
    function returns False, indicating that the destination square is invalid and shouldn't be added to the legal moves
    list
    """
    tracer_xy = i_to_xy(tracer)
    offset_xy = offset_to_xy(offset)

    x, y = tracer_xy[0] + offset_xy[0], tracer_xy[1] + offset_xy[1]
    return not (0 <= x <= 7 and 0 <= y <= 7)


"""
==============================
Position and ChessGame classes
==============================
"""
class Position:
    """
    Position is a class that describes a chess position. It contains methods that are used to generate legal moves,
    make a move on the current position, load a FEN string, and more.
    """

    ATTRIBUTES = []
    """
    A list containing all the names of the attributes of this class. Used for copying.
    """

    def __init__(self, fen=None, load_from=None):
        """"""

        """
        Standard chess position properties (according to FEN)
        """
        self.board = STARTING_BOARD.copy()
        self.turn = True  # True: white's turn, False: black's turn
        self.move_num = 1
        self.halfmove_clock = 0
        self.en_passantable = -1
        self.castling_rights = {"K": True, "k": True, "Q": True, "q": True}

        """
        More chess position properties
        """
        self.transposition_table = {}  # For detecting draws by repetition

        """
        Legal move generation attributes
        """
        self.legal_moves = {}
        self.enemy_moves = {}  # A dictionary that contains the squares that are controlled by the opposite side of the
                               # current turn
        self.attacked_squares = {}  # A set that contains the items of the self.enemy_moves dictionary

        """
        Absolute pin related attributes
        """
        self.pins = []  # A list of squares that form a line which corresponds to the absolute pin (pin to the king) of
                        # the current position.
        self.pinned_pieces = []  # The indexes of self.pin and self.pinned_pieces are related to each other
                                 # For example: The pinned piece of self.pins[0] is self.pinned_pieces[0]
        self.en_passant_pinned = -1

        """
        Check related attributes
        """
        self.check = False
        self.checking_piece = -1  # The checking piece that can be captured to avoid check
                                  # -1 if king is not on check and -2 if it's a double check
        self.checking_path = []  # The squares a piece can move to in order to block the check

        if not Position.ATTRIBUTES:
            # Only run once when the first Position object is created to save the attributes of the Position class
            Position.ATTRIBUTES = list(vars(self).keys())

        if fen:
            self.load_fen(fen)
        elif load_from:
            self.load_position(load_from)
        else:
            self.update_moves()

    def generate_piece_moves(self, square: int, controlling_only=False):
        """
        Generate the legal squares a piece can move to

        Calculating regular moves is mostly based on piece offsets and the "tracer"
        The tracer is an imaginary thing that goes from a piece to one straight direction (the offset) while marking the
        squares a piece can go to ("tracing" a line)

        :param square: The square index of the piece

        :param controlling_only: A special parameter used to calculate enemy moves.
        If controlling_only is True then it will only return the squares that a piece controls (defends or attacks).
        Pawn pushes are then excluded and other same color pieces that are defended by the given piece are included.
        Checks and absolute pins are also calculated for calculating legal moves later.

        :return: The squares the given piece can go to

        WARNING: This function is currently a logic hell
        """

        ret = []
        piece = self.board[square]
        piece_type = piece if piece == "p" else piece.upper()
        # Piece type is always uppercase unless it's a pawn because the pawn's offset is dependent on its color

        must_evade_check = self.check and not controlling_only
        # If true then the move must evade the check
        # If controlling_only is true then checks don't matter because the given piece is an enemy piece

        if piece not in PIECE_TYPES:
            raise ValueError(f"invalid piece \"{piece}\"")

        for offset in MOVE_OFFSETS[piece_type]:
            """
            `for offset in MOVE_OFFSETS[piece_type]:`

            For every piece, there is a number of set offsets. The entire block of code inside this loop represents one
            tracer with its own offset and the path that's being traced by it.
            """

            tracer = square + offset
            tracer_path = []

            pawn_push = piece_type in ("P", "p") and abs(offset) == 8
            pawn_capture = piece_type in ("P", "p") and abs(offset) != 8
            # pawn_push is True if the current offset is calculating a pawn push
            # pawn_capture is True if the current offset is calculating a pawn capture

            if is_tracer_at_edge(square, offset) or (pawn_push and controlling_only):
                # The starting position of the tracer is out of bounds
                # or
                # controlling_only is True but the current offset is a pawn push offset
                continue

            # Variables that are used to calculate absolute pins
            pin_suspect = -1
            squares_behind_suspect = []
            searching_ep_pin = False

            # Determine how far the tracer goes
            if piece_type in ("N", "K") or pawn_capture:
                # Kings and knights can't move as far as they want
                # Pawns can only capture 1 space diagonally in front of them
                trace_distance = 1
            elif pawn_push:
                # Pawns can either move 1 or 2 squares forward if they are on the 2nd or 7th rank and 1 square otherwise
                trace_distance = 2 if square // 8 in (1, 6) else 1
            else:
                # Queens, rooks, and bishops can move as far as they want
                trace_distance = 7

            for _ in range(trace_distance):
                """
                `for _ in range(trace_distance):`
                
                The block of code being run inside this loop represents the path of the tracer being traced, or the
                tracer going from its starting square to its end step by step
                
                For every step of a tracer, different scenarios can happen:
                1. The tracer encounters another piece
                2. The tracer steps onto an empty square
                3. The tracer reaches the end of the board
                """

                tracer_piece = self.board[tracer]

                if tracer_piece:
                    """
                    ========================================
                    The tracer has encountered another piece
                    ========================================
                    
                    Continue tracing if the tracer piece is the enemy king and controlling_only is true, otherwise,
                    stop tracing
                    
                    Determine whether the tracer piece should be appended to the return value or not:
                    
                    1. Opposite color pieces can be captured.
                    2. Same color pieces can't be captured, but if controlling_only is true, the tracer piece is added
                       to the return value.
                    3. Pawns only can capture if the current offset is a pawn capture offset.
                    4. Kings can only capture an enemy piece that is not defended by another piece
                    
                    5. If the piece is pinned to the king, it can only capture the pinning piece.
                    6. When the tracer passes an enemy piece, the tracer becomes a "phantom tracer" to detect for pins.
                       If the tracer is on its phantom tracer state, the piece is not appended.
                    
                    7. While on check:
                        a. Pieces (except the king) cannot capture an enemy piece unless the piece captured is the one
                           who is checking the king.
                        b. The king can capture another piece while on check whether it's the checking piece or another
                           enemy piece, as long as that piece is not protected by another piece.
                           
                    Determine whether to stop tracing or not:
                    
                    1. If the tracer piece is the enemy king (controlling_only must be true), continue tracing, because
                       the squares behind the enemy king are also attacked and the enemy king cannot go there.
                    2. If the tracer piece is an enemy piece, the tracer continues tracing and becomes a "phantom
                       tracer" by having pin_suspect set to a number other than -1.
                    """
                    different_color = tracer_piece.isupper() != piece.isupper()
                    stop_tracing = True

                    # old stuff
                    # if (square not in self.pinned_pieces or tracer in self.pins) and controlling_only or \
                    #         (not must_evade_check and different_color and ((piece_type != "K" and not pawn_push) or
                    #          piece_type == "K" and different_color and tracer not in self.attacked_squares)) or \
                    #         (must_evade_check and ((piece_type != "K" and tracer == self.checking_piece) or
                    #          (piece_type == "K" and tracer not in self.attacked_squares and different_color))):

                    if (square not in self.pinned_pieces or tracer in self.pins) and \
                        (controlling_only or (different_color and not pawn_push and (
                            (piece_type != "K" and (not must_evade_check or tracer == self.checking_piece)) or
                            (piece_type == "K" and tracer not in self.attacked_squares)
                        ))):

                        if tracer_piece in ("K", "k") and different_color:
                            """
                            The tracer has reached the enemy king
                            
                            1. No pin suspects                  : Check
                            2. Pin suspect (phantom tracer)     : Absolute pin
                            """

                            if pin_suspect == -1:
                                """
                                Check
                                
                                If one/two of the enemy pieces is attacking the king (the tracer reaches the enemy king)
                                then it's a check
                                """

                                assert controlling_only, "one of the legal moves is capturing the king"
                                # If one of the legal moves is directly capturing the king then something went wrong

                                self.check = True

                                if self.checking_piece >= 0:
                                    # If there is already another checking piece, then it's a double check
                                    self.checking_piece = -2
                                    self.checking_piece = []
                                else:
                                    self.checking_piece = square
                                    self.checking_path = tracer_path.copy()

                                stop_tracing = False
                                # The squares behind the king are also attacked by the current piece
                                # Therefore, the king cannot move to those squares

                            else:
                                """
                                Absolute pin
                                
                                If the piece that is behind the pin suspect is the enemy king (the tracer reaches the
                                enemy king while on its phantom tracer state) then it is an absolute pin
                                """
                                if not searching_ep_pin:
                                    self.pins.append([square] + tracer_path + squares_behind_suspect)
                                    self.pinned_pieces.append(pin_suspect)
                                    # print("Absolute pin", self.pins, self.pinned_pieces)
                                else:
                                    self.en_passant_pinned = pin_suspect

                        if pin_suspect == -1:
                            tracer_path.append(tracer)

                            if controlling_only and different_color and tracer_piece not in ("K", "k"):
                                """
                                Absolute pin detection
                                
                                To search for absolute pins, the tracer will become a "phantom tracer", continue
                                tracing behind the piece, and the tracer piece is saved to the pin_suspect variable.
                                If the first piece behind the pin suspect is the enemy king, then that tracer piece is
                                pinned and cannot move. If the first piece behind the tracer piece is not the enemy king,
                                then it's not an absolute pin and the tracer can stop tracing.
                                """
                                pin_suspect = tracer
                                stop_tracing = False

                            if self.en_passantable != -1 and tracer_piece in ("P", "p") and \
                                    square // 8 in (3, 4) and abs(offset) == 1:
                                """
                                En passant absolute pin detection
                                
                                En passant pins are extremely rare cases where an en passant move causes the king to be
                                exposed to an enemy attack, making the move illegal. If the tracer meets 2 different
                                colored pawns that  are side to side on the 4th or 5th rank, and one of the two pawns
                                can be captured by en passant, the tracer will continue tracing. If the first piece
                                behind the two pawns is the enemy king, then the pawn cannot perform en passant as it
                                will discover an attack to the king
                                """

                                front_pawn_square = tracer
                                front_pawn = tracer_piece

                                tracer += offset

                                back_pawn_square = tracer
                                back_pawn = self.board[tracer]

                                stop_tracing = False
                                searching_ep_pin = True

                                if back_pawn in ("P", "p") and front_pawn.isupper() != back_pawn.isupper():
                                    if abs(front_pawn_square - self.en_passantable) == 8:
                                        pin_suspect = back_pawn_square

                                    elif abs(back_pawn_square - self.en_passantable) == 8:
                                        pin_suspect = front_pawn_square

                                    else:
                                        stop_tracing = True

                    if stop_tracing:
                        break

                elif not pawn_capture or controlling_only or (tracer == self.en_passantable and
                                                              square != self.en_passant_pinned):
                    """
                    ============================
                    Tracer is on an empty square
                    ============================
                    
                    1. Tracer is on an available empty square
                    2. The current offset is a pawn capture offset and controlling_only is True
                    3. The current offset is a pawn capture offset and the tracer is on the en passantable square
                    4. The king can only move to a square that isn't attacked by the enemy pieces
                    
                    5. If the tracer is a phantom tracer (tracing the squares behind an enemy piece), then the empty
                       squares are appended to squares_behind_suspect instead of tracer_path
                    6. If the piece is pinned to the king, then it can only move to the squares that doesn't break the
                       pin. If one of the moves break a pin on a given offset, then the tracing path of that offset is
                       already invalid.
                    
                    7. While on check:
                        a. A piece (other than the king) can only move to an empty square that blocks the checking path.
                           For every offset of a piece, there is only a maximum of 1 possible blocking move.
                        b. The king can move to an empty square as long as that square isn't attacked by the enemy
                           pieces
                    """

                    if pin_suspect != -1:
                        squares_behind_suspect.append(tracer)

                    elif square in self.pinned_pieces and tracer not in self.pins[self.pinned_pieces.index(square)]:
                        break

                    elif (not must_evade_check and piece_type != "K") or \
                            (controlling_only and not pawn_push) or \
                            (piece_type == "K" and tracer not in self.attacked_squares):
                        tracer_path.append(tracer)

                    elif must_evade_check and piece_type != "K" and tracer in self.checking_path:
                        tracer_path.append(tracer)
                        break

                if is_tracer_at_edge(tracer, offset) and not pawn_capture:
                    # The tracer has reached the edge of the board
                    break

                # Continue tracing
                tracer += offset

            ret += tracer_path

        # Add castling moves for kings
        if piece_type == "K" and not controlling_only and not self.check:
            for side, castling_squares in CASTLING_SQUARES.items():
                if square == castling_squares[0] and self.can_castle(side):
                    ret.append(castling_squares[2])

        return ret

    def can_castle(self, side):
        """
        Returns True if a king can castle to the given side and color

        Castling conditions:
        1. The king is not in check
        2. The king and the rook of the castling side both haven't moved yet
        3. The squares between the king and the rook are empty
        4. The square the king "goes through" while castling and the square it ends up on after castling is not attacked
           by the enemy
        """
        assert side in CASTLING_SQUARES, f"invalid side \"{side}\""

        squares_after_castling = CASTLING_SQUARES[side][1:3]
        squares_in_between = squares_after_castling.copy()
        if side in ("Q", "q"):
            squares_in_between.append(CASTLING_SQUARES[side][4])

        return not self.check and \
               self.castling_rights[side] and \
               all(not self.board[square] for square in squares_in_between) and \
               all(square not in self.attacked_squares for square in squares_after_castling)

    # @shared.func_timer
    def update_moves(self):
        # A position is not on check and doesn't have pins until proven otherwise
        self.check = False
        self.checking_piece = -1
        self.checking_path = []

        self.pins = []
        self.pinned_pieces = []

        # Get the indexes of the pieces of each color
        white = [i for i, x in enumerate(self.board) if x.isupper()]
        black = [i for i, x in enumerate(self.board) if x.islower()]

        self.enemy_moves = {square: self.generate_piece_moves(square, controlling_only=True)
                            for square in (black if self.turn else white)}
        self.attacked_squares = {x for piece_moves in self.enemy_moves.values() for x in piece_moves}

        self.legal_moves = {square: self.generate_piece_moves(square) for square in (white if self.turn else black)}

        # print()
        # print("Legal moves", self.legal_moves)
        # print("Attacked", self.enemy_moves)

    def move(self, old: int, new: int, promote_to=None):
        if old not in self.legal_moves or new not in self.legal_moves[old]:
            return MoveResults.ILLEGAL

        piece = self.board[old]
        captured_piece = self.board[new]

        if piece in ("P", "p") and new // 8 in (0, 8) and promote_to is None:
            # If the pawn reached the other side, then it's a pawn promotion. If the move is a pawn promotion and the
            # piece to promote to is still not determined, then the move is not made
            return MoveResults.PROMPT_PROMOTION

        # Move the piece
        self.board[new] = piece
        self.board[old] = ""

        """
        En passant
        """
        new_en_passantable = False
        if piece in ("P", "p"):
            if abs(new - old) == 16:
                # If a pawn moved two squares on its first move, then mark the square behind that pawn as en passantable
                self.en_passantable = old + (8 if piece == "p" else -8)
                new_en_passantable = True

            elif new == self.en_passantable:
                # If a pawn captures an en passantable square, capture the pawn behind
                en_passanted_square = new + (-8 if piece == "p" else 8)

                captured_piece = self.board[en_passanted_square]
                self.board[en_passanted_square] = ""

        if not new_en_passantable:
            self.en_passantable = -1

        """
        Castling
        """
        for side, squares in CASTLING_SQUARES.items():
            if old == squares[0] or old == squares[3] or new == squares[3]:
                # If the king or rook moves, or a piece captures the enemy rook,
                # then the king loses its castling rights to the given side(s)
                self.castling_rights[side] = False

        if piece in ("K", "k") and abs(new - old) == 2:
            # If the king moves 2 squares to the side then it's a castling move
            # The rook is then moved to the correct square according to the side of castling

            for squares in CASTLING_SQUARES.values():
                if new == squares[2]:
                    rook_old, rook_new = squares[3], squares[1]
                    self.board[rook_new] = self.board[rook_old]
                    self.board[rook_old] = ""

        """
        Update turn, halfmove clock, and move number
        """
        if piece in ("P", "p") or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.turn = not self.turn

        if self.turn:
            self.move_num += 1

        """
        Update moves
        """
        self.update_moves()

        # Testing stuff
        # if self.check:
        #     print("Check!")

        # if all(len(x) == 0 for x in self.legal_moves.values()):
        #     if self.check:
        #         winner = "black" if self.turn else "white"
        #         print(f"Checkmate! {winner} wins!")
        #     else:
        #         print("Draw by stalemate")


        # print(self.legal_moves)
        # print(self.checking_path)

        return 1

    def load_fen(self, fen: str):
        board_raw, turn, castling_rights, en_passantable, halfmove_clock, move_num = fen.split()

        # 1. Piece placement on board
        decoded_board = []
        rows = board_raw.split("/")

        if len(rows) != 8:
            raise ValueError(f"board only consists of {rows} rows (expected: 8)")

        for row in rows:
            decoded_row = []
            for x in row:
                if x in PIECE_TYPES:
                    decoded_row.append(x)
                elif x.isdigit():
                    decoded_row += [""] * int(x)
                else:
                    raise ValueError(f"invalid FEN piece character \"{x}\" on row {row}")

            if len(decoded_row) != 8:
                raise ValueError(f"row {row} is only {len(decoded_row)} long (expected: 8)")

            decoded_board += decoded_row

        self.board = decoded_board

        # 2. Active color (turn)
        if turn in "w":
            self.turn = True
        elif turn == "b":
            self.turn = False
        else:
            raise ValueError(f"invalid active color character \"{turn}\"")

        # 3. Castling rights
        for x in "KQkq":
            self.castling_rights[x] = x in castling_rights

        # 4. En passantable
        self.en_passantable = coordinate_to_i(en_passantable) if en_passantable != "-" else -1

        # 5. Halfmove clock
        self.halfmove_clock = int(halfmove_clock)

        # 6. Fullmove number
        self.move_num = int(move_num)

        self.update_moves()

    def load_position(self, load_from):
        """
        Copies all the attributes from load_from to self
        """
        for attr in Position.ATTRIBUTES:
            setattr(self, attr, copy.deepcopy(getattr(load_from, attr)))

    def copy(self):
        return Position(load_from=self)

    # @shared.func_timer
    def search(self, depth: int):
        if depth <= 1:
            return sum(len(x) for x in self.legal_moves.values())

        count = 0
        for old in self.legal_moves:
            for new in self.legal_moves[old]:
                new_copy = self.copy()
                new_copy.move(old, new)
                count += new_copy.search(depth - 1)

        return count



class ChessGame(Position):
    """
    ChessGame is the subclass of Position that is used directly to the GUI of the app
    There will be more additions to come, such as undoing, redoing, and self moves by the computer or online matches
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_gui = None

        self.position_history = []
        self.move_history = []

        # Testing stuff
        # for i in range(1, 9):
        #     time_before = time.perf_counter()
        #     print(f"depth: {i}, result: {self.search(i)}, time: {time.perf_counter() - time_before} seconds")

    def move(self, old: int, new: int, promote_to=None):
        move_result = super().move(old, new, promote_to)

        if self.board_gui:
            self.board_gui.reset_board(self.board)  # Soon to be replaced when gui.Board.output_move works

        return move_result


# Testing stuff

# thing1 = ChessGame()
# thing2 = thing1.copy()
#
# print(thing1)
# print(thing2)
# print(thing2.__dict__)
