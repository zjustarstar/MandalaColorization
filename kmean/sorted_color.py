import cv2
import numpy as np
import os

def sorted_color(color,labels,k_palette):
    center_counts = {}
    for i in range(k_palette):
        center_counts[i] = labels[i];
    # print(center_counts);

    centers_index_sorted = [center[0] for center in
                            sorted(center_counts.items(), key=lambda center: center[1], reverse=True)]
    centers_index_sorted = np.array(centers_index_sorted);
    color_new = [];
    for center_index in centers_index_sorted:
        color_new.append(color[center_index]);
    color_res = color_new;
    return color_res;


def save_picture(colors,color2,file_name,j):
    n_channels = 3;
    result = []
    result_width = 200
    result_height_per_center = 80
    number = len(colors)
    for i in range(number):
        result.append(
            np.full((result_width * result_height_per_center, n_channels), colors[i], dtype=int))
    result = np.array(result)
    result = result.reshape((result_height_per_center * (number), result_width, n_channels))

    dir1 = 'D:/pycharmFilePicture/five_color/'
    j = str(j);
    filename_five_ori = dir1 + file_name + '___'+j+'_ori.jpg'
    file_name01 = filename_five_ori
    cv2.imwrite(file_name01, result)

    result1 = [];
    number1 = len(color2)
    for i in range(number1):
        result1.append(
            np.full((result_width * result_height_per_center, n_channels), color2[i], dtype=int))
    result1 = np.array(result1)
    result1 = result1.reshape((result_height_per_center * (number1), result_width, n_channels))
    j = str(j);
    filename_five_res = dir1 + file_name + '___'+j+'_res.jpg'
    file_name02 = filename_five_res
    cv2.imwrite(file_name02, result1)


def save_picture_1(colors,file_name,num):
    n_channels = 3;
    result = []
    result_width = 200
    result_height_per_center = 80
    number = len(colors)
    for i in range(number):
        result.append(
            np.full((result_width * result_height_per_center, n_channels), colors[i], dtype=int))
    result = np.array(result)
    result = result.reshape((result_height_per_center * (number), result_width, n_channels))
    dir1 = './five_color/'
    if num == 1:
        prefix = str('A_');
    else:
        if num == 2:
            prefix = str('B_');
        else:
            if num == 3:
                prefix = str('C_');

    if not os.path.exists(dir1):
        os.mkdir(dir1)
    dir2 = './five_color/'+file_name+"/"
    if not os.path.exists(dir2):
        os.mkdir(dir2)
    filename_five_ori = dir2 + prefix + file_name + '_ori.jpg'
    file_name01 = filename_five_ori
    cv2.imwrite(file_name01, result)

def save_picture_2(colors,file_name,j,num):
    n_channels = 3;
    result = []
    result_width = 200
    result_height_per_center = 80
    number = len(colors)
    for i in range(number):
        result.append(
            np.full((result_width * result_height_per_center, n_channels), colors[i], dtype=int))
    result = np.array(result)
    result = result.reshape((result_height_per_center * (number), result_width, n_channels))
    dir1 = './five_color/' + file_name + "/";
    if num == 1:
        prefix = str('A_');
    else:
        if num == 2:
            prefix = str('B_');
        else:
            if num == 3:
                prefix = str('C_');
    if not os.path.exists(dir1):
        os.mkdir(dir1)
    j = str(j);
    filename_five_ori = dir1 + prefix + file_name + '___'+j+'_res.jpg'
    file_name01 = filename_five_ori
    cv2.imwrite(file_name01, result)

