from colormath.color_objects import sRGBColor, HSVColor
from colormath.color_conversions import convert_color


# 输入rgb范围是[0, 255]。如果输入是[0, 1]则需要将is_upscaled设为false
# 返回的hsv范围是：h=[0, 360], s=[0, 1], v=[0, 1]
def rgb2hsv(r, g, b):
    rgb = sRGBColor(r, g, b, is_upscaled=True)
    hsv = convert_color(rgb, HSVColor)
    h, s, v = hsv.get_value_tuple()
    return h, s, v


if __name__ == '__main__':
    r, g, b = 0, 15, 100
    h, s, v = rgb2hsv(r, g, b)
    print(h, s, v)

