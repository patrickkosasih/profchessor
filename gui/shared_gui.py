from PIL import Image, ImageTk
import colorsys


def rgb_hex_to_int(hex_rgb: str) -> tuple:
    """
    Converts a hex RGB string into three 8-bit values in a tuple

    e.g. "#ffe4ad" -> (255, 228, 173)
    """

    return tuple(int(hex_rgb[i: i + 2], base=16) for i in range(1, 7, 2))


def translucent_rectangle(opacity: float, width, height, color=(0, 0, 0)) -> ImageTk.PhotoImage:
    """
    Generates a PhotoImage object with the set width and height that contains a solid color with a set opacity.
    Used to draw translucent rectangles in a Tkinter canvas or window
    """

    if type(color) is str:
        color = rgb_hex_to_int(color)

    image = Image.new("RGBA", (width, height), (*color, int(opacity * 255)))
    photoimage = ImageTk.PhotoImage(image)

    return photoimage


def hsv_factor(rgb, hf=0, sf=1, vf=1) -> tuple:
    """
    Takes a 24 bit RGB value and changes it according to the given HSV factors (hue, saturation, and value)

    :param rgb: The RGB value can be in tuple (e.g. (255, 255, 255)) or a string with the "#RRGGBB" format

    :param hf: Hue factor
    :param sf: Saturation factor
    :param vf: Value (brightness) factor
    """

    if type(rgb) is str:
        rgb = rgb_hex_to_int(rgb)

    r, g, b = (x / 255.0 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    new_hsv = h + hf, s * sf, v * vf
    new_hsv = tuple(max(0, min(1, x)) for x in new_hsv)  # Clamp values between 0-1
    new_rgb = colorsys.hsv_to_rgb(*new_hsv)
    int_rgb = tuple(int(x * 255) for x in new_rgb)  # Convert RGB values from 0.0 - 1.0 to 0 - 255

    return int_rgb
