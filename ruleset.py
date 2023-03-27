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
MOVE_OFFSETS is a dictionary containing the offset values of all the pieces
Offset is what number should be added to the position index of a piece to get the legal squares it can move to

The king and knight only move 1 step at a time while the rook, bishop, and queen can move in a straight line that goes
as far as it can until it meets another piece or the edge or the board. Therefore, the position of a rook, bishop, and
queen is added by the offset values over and over again until it stops.

The pawn has 4 different offsets according to its color and depending on if it's a move or a capture
"""

CASTLING_SQUARES = {
    "K": [60, 61, 62, 63],
    "Q": [60, 59, 58, 56, 57],
    "k": [4, 5, 6, 7],
    "q": [4, 3, 2, 0, 1]
}
"""
CASTLING_SQUARES is a dictionary containing the key squares that is used on calculating whether the king can castle or
not.

The letters on the dictionaries' key refer to the color and the side of castling. For example, "Q" is white queenside
castling and "k" is black kingside castling.

The numbers inside the lists refer to the following:
* Index 0 = The king's original square
* Index 1 = The square the king "passes through" when castling and the square the rook will end up on after castling
* Index 2 = The square the king will end up on after castling
* Index 3 = The rook's original square
* Index 4 = The queenside knight's original square (only for queenside castling ("Q" and "q") because that square must
            also be empty for a king to castle queenside)
"""


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
===============
ChessGame class
===============
"""
class ChessGame:
    def __init__(self):
        self.board = STARTING_BOARD
        self.turn = True  # True: white's turn, False: black's turn
        self.move_num = 1
        self.halfmove_clock = 0
        self.en_passantable = -1
        self.castling_rights = {"K": True, "k": True, "Q": True, "q": True}

        self.legal_moves = {}
        self.enemy_moves = {}  # The squares that is controlled by the opposite side of the current turn
        self.attacked_squares = {}  # A set that contains the items of the self.enemy_moves dictionary
        self.update_moves()

        self.board_gui = None

        # print(self.legal_moves)

    def generate_piece_moves(self, square: int, attacking_only=False):
        """
        Generate the legal squares a piece can move to

        Calculating regular moves is mostly based on piece offsets and the "tracer"

        The tracer is an imaginary thing that goes from a piece to one straight direction (the offset) while marking the
        available squares a piece can go ("tracing" a line)

        If controlling_only is True then it will only return the squares that a piece attack, so a pawn push is excluded
        """

        ret = []
        piece = self.board[square]
        piece_type = piece if piece == "p" else piece.upper()
        # Piece type is always uppercase unless it's a pawn because the pawn's offset is dependent on its color

        assert piece in PIECE_TYPES, f"invalid piece \"{piece}\""

        for offset in MOVE_OFFSETS[piece_type]:
            tracer = square + offset
            pawn_capture = piece_type in ["P", "p"] and abs(offset) != 8
            # pawn_capture is True if the current offset is calculating a pawn capture

            if is_tracer_at_edge(square, offset) or (pawn_capture and attacking_only):
                # The starting position of the tracer is out of bounds
                # or
                # The current offset is only calculating attacks but the current offset is a pawn push offset
                continue

            if piece_type in ["N", "K"] or pawn_capture:
                # Kings and knights can't move as far as they want
                # Pawns can only capture 1 space diagonally in front of them
                repeats = 1
            elif piece_type in ["P", "p"]:
                # Pawns can either move 1 or 2 squares forward if they are on the 2nd or 7th rank and 1 square otherwise
                repeats = 2 if square // 8 in [1, 6] else 1
            else:
                # Queens, rooks, and bishops can move as far as they want
                repeats = 7

            for _ in range(repeats):
                if self.board[tracer] and tracer != square:
                    # The tracing square has reached another piece

                    if self.board[tracer].isupper() != piece.isupper() and \
                       (piece_type not in ["P", "p"] or pawn_capture):
                        # Opposite color piece can be captured
                        # Pawns only can capture if the current offset is a pawn capture offset
                        ret.append(tracer)

                    break

                elif is_tracer_at_edge(tracer, offset):
                    # Tracer goes has reached the edge of the board
                    ret.append(tracer)
                    break

                elif tracer != square and not pawn_capture or \
                        pawn_capture and (tracer == self.en_passantable or attacking_only):
                    # Tracer is on an available empty square
                    # or
                    # Tracer is on the en passantable square and the pawn can capture the pawn beside it
                    # or
                    # The current offset is a pawn capture offset and attacking_only is True
                    ret.append(tracer)

                # Continue tracing
                tracer += offset

        # Add castling moves for kings
        if piece_type == "K" and not attacking_only:
            for side, c_squares in CASTLING_SQUARES.items():
                if square == c_squares[0] and self.can_castle(side):
                    ret.append(c_squares[2])

        return ret

    def can_castle(self, side):
        """
        Returns True if a king can castle to the given side

        Castling conditions:
        1. The king is not in check - will be implemented after the checking system is finished
        2. The king and the rook of the castling side haven't moved yet
        3. The squares between the king and the rook are empty
        4. The square the king "goes through" while castling and the square ends up on after castling is not attacked
           by the enemy
        """
        squares_after_castling = CASTLING_SQUARES[side][1:3]
        squares_in_between = squares_after_castling.copy()
        if side in ["Q", "q"]:
            squares_in_between.append(CASTLING_SQUARES[side][4])

        return self.castling_rights[side] and \
               all(not self.board[square] for square in squares_in_between) and \
               all(square not in self.attacked_squares for square in squares_after_castling)

    # @shared.func_timer
    def update_moves(self):
        white = [i for i, x in enumerate(self.board) if x.isupper()]
        black = [i for i, x in enumerate(self.board) if x.islower()]

        self.enemy_moves = {square: self.generate_piece_moves(square, attacking_only=True)
                       for square in (black if self.turn else white)}
        self.attacked_squares = {x for piece_moves in self.enemy_moves.values() for x in piece_moves}

        self.legal_moves = {square: self.generate_piece_moves(square) for square in (white if self.turn else black)}

        print()
        print("Legal moves", self.legal_moves)
        print("Attacked", self.enemy_moves)

    def move(self, old: int, new: int):
        if old not in self.legal_moves or new not in self.legal_moves[old]:
            return 0  # Illegal move

        piece = self.board[old]
        self.board[new] = piece
        self.board[old] = ""

        self.turn = not self.turn
        if self.turn:
            self.move_num += 1

        """
        En passant
        """
        new_en_passantable = False
        if piece in ["P", "p"]:
            if abs(new - old) == 16:
                # If a pawn moved two squares on its first move, then mark the square behind that pawn as en passantable
                self.en_passantable = old + (8 if piece == "p" else -8)
                new_en_passantable = True

            elif new == self.en_passantable:
                # If a pawn captures an en passantable square, capture the pawn behind
                self.board[new + (-8 if piece == "p" else 8)] = ""
                if self.board_gui:
                    self.board_gui.reset_board(self.board)   # Soon to be replaced when gui.Board.output_move works

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

        if piece in ["K", "k"] and abs(new - old) == 2:
            # If the king moves 2 squares to the side then it's a castling move
            # The rook is then moved to the correct square according to the side of castling

            for squares in CASTLING_SQUARES.values():
                if new == squares[2]:
                    rook_old, rook_new = squares[3], squares[1]
                    self.board[rook_new] = self.board[rook_old]
                    self.board[rook_old] = ""
                    self.board_gui.reset_board(self.board)  # Soon to be replaced when gui.Board.output_move works

        self.update_moves()

        return 1

    def load_fen(self, fen: str):
        board_raw, turn, castling_rights, en_passantable, halfmove_clock, move_num = fen.split()

        # 1. Piece placement on board
        decoded_board = []
        for row in board_raw.split("/"):
            decoded_row = []
            for x in row:
                if x in PIECE_TYPES:
                    decoded_row.append(x)
                elif x.isdigit():
                    decoded_row += [""] * int(x)
                else:
                    raise ValueError(f"invalid FEN piece character \"{x}\" on row {row}")

            if len(decoded_row) != 8:
                raise ValueError(f"row {row} is not 8 squares long")

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
