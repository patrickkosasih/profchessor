import time
import colorsys


DEBUG_LEVEL = 1
"""
DEBUG_LEVEL is a constant that can be changed by the developer before running the program to enable and disable certain
debugging tools without repeatedly commenting and uncommenting parts of the code.

Currently, different debug levels do the following:
0: Debug off, fullscreen mode
1: Windowed, minimized, and visible index numbers on squares
2: Print legal moves and enemy controlled squares on the console
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


def hsv_factor(rgb, hf, sf, vf):
    """
    Takes a 24 bit RGB value and changes it according to the given HSV factors (hue, saturation, and value)

    :param rgb: The RGB value can be in tuple (e.g. (255, 255, 255)) or a string with the "#RRGGBB" format

    :param hf: Hue factor
    :param sf: Saturation factor
    :param vf: Value (brightness) factor
    """

    if type(rgb) is str:
        hex_rgb = rgb
        rgb = (int(hex_rgb[i : i + 2], base=16) for i in range(1, 7, 2))

    r, g, b = (x / 255.0 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    new_hsv = h * hf, s * sf, v * vf
    new_hsv = tuple(max(0, min(1, x)) for x in new_hsv)  # Clamp values between 0-1
    new_rgb = colorsys.hsv_to_rgb(*new_hsv)
    int_rgb = tuple(int(x * 255) for x in new_rgb)  # Convert RGB values from 0.0 - 1.0 to 0 - 255

    return int_rgb
