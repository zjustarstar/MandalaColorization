import os
import copy
import pandas as pd
import numpy as np
import get_color_from_img as gci
import color_space as cs

# 获得颜色组; 暂时用固定的palettes
def get_color_theme_test():
    palettes = [["#47bbb0", "#8ddaca", "#c8e6cc", "#f6a5ac", "#f54773"],
                ["#E36600", "#F5AB34", "#FFE14A", "#6BC7F2", "#004097"],
                ["#CF7B75", "#EBAAAF", "#F6D5BD", "#C3B67B", "#83853a"],
                ["#BCE0E0", "#5EAEAF", "#640F0A", "#9A6543", "#D1B298"]]
    colors_theme = []
    for i, colors in enumerate(palettes):
        rgb_theme = []
        try:
            for c in colors:
                r = int(c[1:3], 16)
                g = int(c[3:5], 16)
                b = int(c[5:7], 16)
                rgb_theme.append((r, g, b))
        except(Exception):
            continue

        colors_theme.append(rgb_theme)

    return colors_theme


# 获得颜色组;column_name表示存放颜色的列名
def get_color_theme_fromexcel(filename, column_name):
    if not os.path.exists(filename):
        print("{0} does not exist".format(filename))
        return []

    data = pd.read_excel(filename)
    theme = data[column_name]
    palettes = []
    for i in range(len(theme)):
        clr_string = theme[i]
        clr_c = clr_string.split(',')
        # 去掉可能的字符串前后空格
        clr = [c.strip() for c in clr_c]
        palettes.append(clr)

    colors_theme = []
    for i, colors in enumerate(palettes):
        rgb_theme = []
        try:
            for c in colors:
                r = int(c[1:3], 16)
                g = int(c[3:5], 16)
                b = int(c[5:7], 16)
                rgb_theme.append((r, g, b))
        except Exception as e:
            print(e)
            continue

        colors_theme.append(rgb_theme)

    return colors_theme


def reorder_color_theme(color_themes, mode=2, asc=True):
    '''
    对色彩组重排序, asc表示升序
    color_themes的格式是:[[(c0, c1, c2),(c0,c1,c2)...][(d0, d1, d2),(d0,d1,d2)...]],表示多个颜色主题
    :param color_themes: 输入的色彩组
    :param mode: 0、1、2三种模式，分别表示hsv色度、饱和度、亮度
    :param asc: True表示升序
    :return:
    '''
    new_color_themes = []
    # thme是color_thems中的某一种配色集
    for theme in color_themes:
        hsv_list = []
        # 配色集中的每一种颜色
        for c in theme:
            h, s, v = cs.rgb2hsv(c[0], c[1], c[2])
            hsv_list.append([h, s, v])
        # 根据什么排序
        hsv_array = np.array(hsv_list)
        sortby = hsv_array[:, mode].tolist()
        sorted_theme = sorted(theme, key=lambda x: sortby[theme.index(x)])
        if not asc:
            sorted_theme.reverse()
        new_color_themes.append(sorted_theme)

    return new_color_themes


# 基于亮度对color重排序, asc表示升序
# color_themes的格式是:[[(c0, c1, c2),(c0,c1,c2)...][(d0, d1, d2),(d0,d1,d2)...]],表示多个颜色主题
def reorder_color_theme_by_L(color_themes, asc=True):
    new_color_themes = []
    for theme in color_themes:
        L_list = []
        for c in theme:
            l = c[0] + c[1] + c[2]
            L_list.append(l)
        sorted_theme = sorted(theme, key=lambda x: L_list[theme.index(x)])
        if not asc:
            sorted_theme.reverse()
        new_color_themes.append(sorted_theme)

    return new_color_themes


def get_color_theme_main(params):
    if not params['recolor_by_transfer']:
        print("get color themes from file")
        # 从excel文件中读取颜色集
        color_theme_file = params['recolor_colortheme_file']
        color_theme = get_color_theme_fromexcel(color_theme_file, 'ColorTheme')
        color_theme_size = len(color_theme)

        temp_clr_theme = copy.deepcopy(color_theme)
        # hsv模式下的排序
        for i in range(3):
            color_theme_asc = reorder_color_theme(temp_clr_theme, mode=i)
            color_theme_desc = reorder_color_theme(temp_clr_theme, mode=i, asc=False)
            color_theme = color_theme + color_theme_asc + color_theme_desc
        color_theme_title = ["ori","hue_asc","hue_desc","sat_asc","sat_desc","val_asc","val_desc"]
        if len(color_theme) == 0:
            print("!!!!color theme is empty!!!!")
            return
        else:
            print("{} color themes will be applied".format(len(color_theme)))
    else:
        print("get color themes by transfering")
        tfile = params['recolor_transfer_file']
        k = params['recolor_transfer_k']
        # 返回的结果按面积从大到小
        colors_rgb, clr_cluster_cnt = gci.get_palette_from_img_by_kmeans(tfile, k, debug=False)
        # 按照面积从小到大
        colors_rgb_asc = copy.deepcopy(colors_rgb)
        colors_rgb_asc.reverse()

        color_theme = [colors_rgb_asc, colors_rgb]
        color_theme_size = 1

        # hsv模式下的排序
        temp_clr_theme = copy.deepcopy([colors_rgb])
        for i in range(3):
            colors_rgb_asc = reorder_color_theme_by_L(temp_clr_theme)
            colors_rgb_desc = reorder_color_theme(temp_clr_theme, mode=i, asc=False)
            color_theme = color_theme + colors_rgb_asc + colors_rgb_desc

        color_theme_title = ["area_asc", "area_desc", "hue_asc", "hue_desc", "sat_asc", "sat_desc", "val_asc", "val_desc"]

    return color_theme, color_theme_size, color_theme_title


if __name__ == '__main__':
    clr_theme = get_color_theme_test()
    print(clr_theme)
    new_clr_theme = reorder_color_theme(clr_theme)
    print(new_clr_theme)

