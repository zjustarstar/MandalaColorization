from PIL import Image
import cv2
import copy
import numpy as np
import os
import time

import get_color_theme as gct


def find_similar_regions_byrect(img, bi_img, pattern_style):
    '''
    利用联通区域最小外接矩形相似性查找相同区域
    :param img: 原图
    :param bi_img: 二值图
    :param pattern_style: 表示线框图的对称模式. C表示中心对称， NC表示非中心对称
    :return: 用于标示每个像素所属的联通区域编号label，且与原图img相同尺寸的矩阵
    '''
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bi_img, connectivity=8)
    new_labels = copy.deepcopy(labels)

    centerY, centerX = img.shape[0]/2.0, img.shape[1]/2.0

    # 查找每个label区域的大小;
    region_info = []
    for i in range(num_labels):
        region_i = np.where(np.array(labels) == i)
        region_i_xy = list(zip(*region_i))
        # ret[0]返回中心点, ret[1]返回外接rect长和宽
        ret = cv2.minAreaRect(np.array(region_i_xy))
        # 离圆心的距离
        dist = ((ret[0][0] - centerX) ** 2 + (ret[0][1] - centerY) ** 2)**0.5
        # 如果离圆心很近，表示这是个围绕圆心一圈的空心图形,按照其长宽计算
        if abs(ret[0][0] - centerX)<20 and abs(ret[0][1] - centerY)<20:
            dist = (ret[1][0]**2 + ret[1][1]**2)**0.5
        w, h = min(ret[1]), max(ret[1])
        region_info.append([dist, w, h])

    # num=0时为黑色区域
    flag_num_labels = [True] * num_labels
    for i in range(1, num_labels):
        if flag_num_labels[i] == False:
            continue
        center_xy1, w1, h1 = region_info[i]
        thresh_size = max(w1, h1)/7
        thresh_dist = center_xy1 * 0.1
        #对于过小的面积，放宽阈值
        if max(w1, h1) < 50:
            thresh_size = 10
        if center_xy1 < 100:
            thresh_dist = 10

        for j in range(i + 1, num_labels):
            # 如果已经比较过了
            if flag_num_labels[j] == False:
                continue

            # 如果两个外接rect相似, 则赋予相同的标签号;
            center_xy2, w2, h2 = region_info[j]
            dist = abs(center_xy1 - center_xy2)
            # 如果是圆环状线稿图，考虑离中心点的距离是相近的
            if pattern_style == 'C':
                cond = max(abs(w1-w2),abs(h1-h2)) < thresh_size and dist < thresh_dist
            else:
                cond = max(abs(w1 - w2), abs(h1 - h2)) < thresh_size
            if cond:
                new_labels[labels == j] = i
                flag_num_labels[j] = False

    return num_labels, new_labels, region_info


def find_similar_regions_bycontour(img, bi_img):
    '''
    利用联通区域外框相似性查找相同区域
    :param img: 原图
    :param bi_img: 二值图
    :return: 用于标示每个像素所属的联通区域编号label，且与原图img相同尺寸的矩阵
    '''
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bi_img, connectivity=8)
    new_labels = copy.deepcopy(labels)

    contour_seq = []
    for lable in range(num_labels):
        new_img = np.zeros(bi_img.shape, dtype=np.uint8)
        new_img[labels == lable] = 255
        contours, hierarchy = cv2.findContours(new_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contour_seq.append(contours)

    print("finish extracting contours, total contours={0}".format(len(contour_seq)))
    # 标记哪些区域已经label已经被修改
    sim_thre = 0.005
    flag_num_labels = [True] * num_labels
    # i=0时为黑色边界
    for i in range(1, num_labels):
        if flag_num_labels[i] == False:
            continue
        cur_contour = contour_seq[i]
        for j in range(i+1, num_labels):
            # 如果已经比较过了
            if flag_num_labels[j] == False:
                continue

            # 如果两个边界相似, 则赋予相同的标签号;
            compare_contour = contour_seq[j]
            similarity = cv2.matchShapes(cur_contour[0], compare_contour[0], cv2.CONTOURS_MATCH_I1, 0)
            if similarity < sim_thre:
                new_labels[labels==j] = i
                flag_num_labels[j] = False
                # print("{0},{1}:similarity={2}".format(i,j,similarity))

    # new_img = np.zeros(bi_img.shape, dtype=np.uint8)
    # new_img[labels==22] = 255
    # contours3, hierarchy = cv2.findContours(new_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    #
    # new_img = np.zeros(bi_img.shape, dtype=np.uint8)
    # new_img[labels==77] = 255
    # contours1, hierarchy = cv2.findContours(new_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    #
    # similarity = cv2.matchShapes(contours3[0], contours1[0], cv2.CONTOURS_MATCH_I1, 0)
    # print("similarity:{}".format(similarity))
    #
    # # 第三个参数指定绘制轮廓list中的哪条轮廓，如果是-1，则绘制其中的所有轮廓。
    # cv2.drawContours(img, contours1, -1, (0, 0, 255), 1)
    # cv2.drawContours(img, contours3, -1, (255, 0, 0), 1)
    # cv2.imshow("img", img)
    # cv2.waitKey(0)
    # cv2.imwrite("con.jpg",img)

    return num_labels, new_labels, []


def colorize_based_theme(color_theme, theme_size, theme_name, all_labels, img_labels, save_path):
    '''
    基于颜色集对图像进行上色
    :param color_theme: 颜色集。里面包括theme_size种配色，以及这size种配色的正排序、逆排序配色等多余的2大种类
    :param theme_size: 颜色集中有多少种配色方案.
    :param theme_name: 配色集的名字
    :param all_labels: 所有的编号，且编号可能根据不同的规则进行过排序
    :param img_labels: 与原图像大小一样，每个像素表示label编号
    :param save_path: 上色后的图像保存在哪里
    :return: 保存后的上色图像的路径
    '''
    output = np.zeros((img_labels.shape[0], img_labels.shape[1], 3), np.uint8)
    saved_files = []
    # 有多组不同的色彩搭配
    for c_index in range(len(color_theme)):
        cur_color_theme = color_theme[c_index]
        print("using {0}-th theme which includes {1} colors".format(c_index + 1, len(cur_color_theme)))
        j = 0  # 当前的颜色循环使用
        for i in all_labels:
            mask = img_labels == i
            clr = cur_color_theme[j % len(cur_color_theme)]
            output[:, :, 0][mask] = clr[2]
            output[:, :, 1][mask] = clr[1]
            output[:, :, 2][mask] = clr[0]
            j = j + 1
        type = c_index // theme_size
        num = c_index % theme_size
        filename = "color_" + str(theme_name[type]) + "_" + str(num) + ".jpg"
        filename = os.path.join(save_path, filename)
        filename = os.path.join(os.getcwd(), filename)
        cv2.imwrite(filename, output)

        saved_files.append(filename)

    return saved_files


def colorization_main(filename, params):
    output_path = params['output_path']
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    save_path = output_path + "/" + shotname  # 保存迁移颜色至同名文件夹
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    im = Image.open(filename)  # 输入曼陀罗线框图路径
    if im.mode == 'RGBA':
        im = np.array(im)
        rgb_info = im[:, :, :3]
        a_info = im[:, :, 3]
        rgb_info[a_info == 0] = [255, 255, 255]
        im = Image.fromarray(rgb_info)
    im = im.convert("L")
    # 转为opencv格式
    img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bi_img = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY)

    # 查找相似的区域
    print("start to extract region info")
    style = params['recolor_sketch_style']
    num_labels, labels, region_info = find_similar_regions_byrect(img, bi_img, style)
    print("total regions={0}".format(num_labels))

    # 去掉重复编号以后，所有区域的编号
    all_labels = set(labels.flatten().tolist())
    all_labels = list(all_labels)
    # 去掉黑色的，黑色的不用上色
    all_labels.remove(0)
    print("{} regions are clssified".format(len(all_labels)))

    # 对应这些label的区域到中心点的距离
    region_dist = []
    for label in all_labels:
        dist = region_info[label][0]
        region_dist.append(dist)

    # 利用区域信息对上色标签排序. 根据离图像中心点的距离大小进行排序
    if len(region_info):
        sortby = np.array(region_dist)
        # 基于距离进行重排序
        sorted_labels = sorted(all_labels, key=lambda x: sortby[all_labels.index(x)])
        all_labels = sorted_labels

    # 获得颜色集
    start_time = time.time()
    color_theme, color_theme_size, color_theme_title = gct.get_color_theme_main(params)
    end_time = time.time()
    time1 = round(end_time - start_time)
    print("color theme extraction:", time1, "s")

    # 不同的连通域赋予不同的颜色
    print("start to colorize....")
    output_file = colorize_based_theme(color_theme, color_theme_size, color_theme_title, all_labels, labels, save_path)
    for f in output_file:
        print("colorized file:{} is created".format(f))


