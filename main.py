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
