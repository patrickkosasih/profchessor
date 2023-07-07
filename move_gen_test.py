"""
move_gen_test.py

A module that contains tools for testing and debugging the move generation of the rules engine (`rules.py`).
"""

import copy
import time

import rules


class PositionDebugger(rules.Position):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self):
        """
        Overrides the original copy method. The original copy method always returns a Position instance, while the copy
        method of DebuggerPosition needs to return its own instance, not a Position instance.
        """
        return copy.deepcopy(self)

    def search(self, depth: int):
        """
        Returns how many positions (leaf nodes) there are in a recursive move generation tree of a given depth.
        """

        # Faster: Only counts leaf nodes
        # if depth <= 1:
        #     return sum(len(x) for x in self.legal_moves.values())

        # Slower: Calls leaf nodes
        if depth <= 0:
            return 1

        count = 0
        for old in self.legal_moves:
            for new in self.legal_moves[old]:
                new_copy, move_result = self.copy_and_move(old, new)

                if move_result & rules.MoveResult.PROMOTION:
                    # If the move is a promotion move, branch out for every piece it can promote to

                    for x in "QRBN":
                        promotion_new_copy, _ = self.copy_and_move(old, new, promote_to=x)
                        count += promotion_new_copy.search(depth - 1)
                else:
                    count += new_copy.search(depth - 1)

        return count

    def test_each_depths(self, depth=6):
        """
        Run the search method for different depths, starting from 1 ply and working its way up.
        """
        for i in range(1, depth + 1):
            time_before = time.perf_counter()
            print(f"depth: {i}, result: {self.search(i)}, time: {time.perf_counter() - time_before} seconds")

    def test_each_moves(self, depth=3):
        """
        Run the search method for all the legal moves in a position. Similar to the "go perft" command in Stockfish.
        """
        total = 0

        for old in self.legal_moves:
            for new in self.legal_moves[old]:
                moved, _ = self.copy_and_move(old, new)
                search_result = moved.search(depth - 1)
                total += search_result

                old_coor = rules.i_to_coordinate(old)
                new_coor = rules.i_to_coordinate(new)
                print(f"{old_coor}{new_coor}: {search_result}")

        print(f"Total: {total}")

def main():
    # Write the debugging code here

    position = PositionDebugger()

    # position.move(52, 36)
    # position.move(12, 28)
    # position.move(59, 31)
    # position.move(8, 24)

    # position.test_each_moves(3)
    position.test_each_depths(5)
