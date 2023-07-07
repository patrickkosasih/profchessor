"""
debug.py

A small module that contains tools for debugging the internal Python code and a constant for easy switching between
debug levels (`DEBUG_LEVEL`).
"""

import time


DEBUG_LEVEL = 0
"""
DEBUG_LEVEL is a constant that can be changed by the developer before running the program to enable and disable certain
debugging tools without repeatedly commenting and uncommenting parts of the code.

Currently, different debug levels do the following:
0: Debug off, fullscreen mode
1: Windowed, visible index numbers on squares
2: Print legal moves and enemy controlled squares on the console
1000: Call move_gen_test.main() and run a move generation test without showing the usual GUI window
"""


def func_timer(func):
    """
    A decorator function that measures the time taken to run a function
    """
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)  # Call function
        time_taken = time.perf_counter() - time_before

        print(f"{func.__name__} took {time_taken} seconds to run")
        return ret

    return wrapper
