"""
main.py

Welcome to the Profchessor source code!

This is the main gateway of running the entire program of Profchessor. To start Profchessor, simply run this Python
script from your IDE, file explorer, or command line. To compile the entirety of Profchessor, run Pyinstaller by having
this file as the file (-f) parameter.
"""

from gui.game_gui import MainWindow
import debug
import move_gen_test


def main():
    if debug.DEBUG_LEVEL < 1000:
        MainWindow().mainloop()
    else:
        move_gen_test.main()


if __name__ == '__main__':
    main()
