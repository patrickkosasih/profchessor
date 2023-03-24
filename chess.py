import shared

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

# Test stuff
# STARTING_BOARD = list("rnbqkbnr") + ["p"] * 8 + [""] * 32 + [""] * 8 + list("RNBQKBNR")
# STARTING_BOARD[27] = "Q"

MOVE_OFFSETS = {
    "P": [-8],       # White pawn
    "p": [8],        # Black pawn
    "Pc": [-7, -9],  # White pawn capture
    "pc": [7, 9],    # Black pawn capture

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


"""
Conversion functions
"""
def i_to_xy(i: int):
    return i % 8, i // 8

def offset_to_xy(i: int):
    x, y = (i % 8, i // 8)
    if x > 4:
        x = x % -8
        y += 1

    return x, y

def i_to_coordinate(i: int):  # Standard chess coordinate
    return chr(ord("a") + i % 8) + str(8 - i // 8)


def coordinate_to_i(coor: str):
    return ord(coor[0]) - ord("a") + (8 - int(coor[1]))


"""
Misc functions
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
ChessGame class
"""
class ChessGame:
    def __init__(self):
        self.board = STARTING_BOARD
        self.turn = True  # True: white's turn, False: black's turn
        self.legal_moves = {}

        self.update_legal_moves()

        # print(self.legal_moves)

    def generate_piece_moves(self, square: int):
        """
        Generate the legal squares a piece can move to
        The only moves generated are regular moves such as moving or capturing a piece
        """
        assert self.board[square]  # Error if square is empty

        ret = []
        piece = self.board[square]
        piece_type = piece if piece == "p" else piece.upper()
        # Piece type is always uppercase unless it's a pawn because the pawn's offset is dependent on its color

        for offset in MOVE_OFFSETS[piece_type]:
            tracer = square
            # The tracer is an imaginary thing that goes from a piece to one straight direction (the offset) while
            # marking the available squares a piece can go

            if piece_type in ["N", "K"]:
                # Kings and knights can't move as far as they want
                repeats = 2
            elif piece_type in ["P", "p"]:
                # Pawns can move 1 or 2 squares forward if they are on the 2nd or 7th rank
                repeats = 3 if square // 8 in [1, 6] else 2
            else:
                # Queens, rooks, and bishops can move as far as they want
                repeats = 8

            for _ in range(repeats):
                if tracer != square:
                    ret.append(tracer)

                if self.board[tracer] and tracer != square:
                    # The tracing square has reached another piece
                    if self.board[tracer].isupper() == piece.isupper():
                        # Same color piece (cannot be captured)
                        ret.pop(-1)
                        break
                    else:
                        # Opposite color piece (can be captured)
                        if piece_type.upper() == "P":
                            ret.pop(-1)
                        break

                elif is_tracer_at_edge(tracer, offset):
                    # Tracer goes has reached the edge of the board
                    break

                # Continue tracing
                tracer += offset

        return ret

    def update_legal_moves(self):
        self.legal_moves = {}

        # Get the indexes of the pieces filtered by whose turn it is
        isturn = str.isupper if self.turn else str.islower
        current_turn_pieces = [i for i, square in enumerate(self.board) if isturn(square)]

        for square in current_turn_pieces:  # i : square index of current piece
            self.legal_moves[square] = self.generate_piece_moves(square)


    def move(self, old: int, new: int):
        if old not in self.legal_moves or new not in self.legal_moves[old]:
            return 0  # Illegal move

        self.board[new] = self.board[old]
        self.board[old] = ""

        self.turn = not self.turn
        self.update_legal_moves()

# # Some testing and stuff
# tests = {
#     1: (1, 0),
#     8: (0, 1),
#     -1: (-1, 0),
#     -8: (0, -1),
#
#     7: (-1, 1),
#     9: (1, 1),
#     -7: (1, -1),
#     -9: (-1, -1),
#
#     6: (-2, 1),
#     -6: (2, -1),
#     10: (2, 1),
#     -10: (-2, -1),
#     15: (-1, 2),
#     -15: (1, -2),
#     17: (1, 2),
#     -17: (-1, -2)
# }
#
# for arg, expected in tests.items():
#     if offset_to_xy(arg) == expected:
#         print(f"input: {arg} - Test passed")
#     else:
#         print(f"input: {arg} - Test failed, expected: {expected}, output: {offset_to_xy(arg)}")
