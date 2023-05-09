from gui import game_gui
import debug
import move_gen_test


def main():
    if debug.DEBUG_LEVEL < 1000:
        game_gui.MainWindow().mainloop()
    else:
        move_gen_test.main()


if __name__ == '__main__':
    main()
