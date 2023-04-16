import time
import colorsys


def func_timer(func):
    # A decorator to measure the time taken to run a function
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)  # Call function
        time_taken = time.perf_counter() - time_before

        print(f"{func.__name__} took {time_taken} seconds to run")
        return ret

    return wrapper


def hsv_factor(rgb, hf, sf, vf):
    """
    :param rgb: The RGB value in tuple or #RRGGBB format
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
