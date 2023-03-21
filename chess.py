STARTING_BOARD = list("rnbqkbnr") + ["p"] * 8 + [""] * 32 + ["P"] * 8 + list("RNBQKBNR")


class ChessGame:
    def __init__(self):
        self.board = STARTING_BOARD