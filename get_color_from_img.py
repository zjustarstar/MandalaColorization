import PIL.Image as Image
import numpy as np
import time

# kmeans方法
from kmean.deal_before import pre_process
from kmean.get_info import get_rgb
from kmean.palette import k_means


# palette是array格式. 如果是list, 需要先转换为array
def get_bigger_palette_to_show(palette):
    ##### palette shape is M*3
    c=50
    palette2=np.ones((1*c, len(palette)*c, 3))
    for i in range(len(palette)):
        palette2[:,i*c:i*c+c,:]=palette[i,:].reshape((1,1,-1))
    return palette2


def get_palette_from_img_by_kmeans(filename, k, debug=False):
    image = Image.open(filename)
    if image.mode == 'P' or image.mode=='RGBA':
        image = image.convert('RGBA')
    else:
        image = image.convert('RGB')

    image = image.resize((512, 512))
    if debug:
        image.show("image")
    #多一位黑色
    img_lab, n_pixels, n_channels = pre_process(image)
    centers, cluster_count = k_means(img_lab, k, init_mean=True, sortby='C', max_iter=1000, black=True)

    # 将Lab转为rgb
    colors_rgb = get_rgb(centers)
    cluster_count = cluster_count / n_pixels

    # 去除比较黑的颜色
    new_colors_rgb, new_cluster_count = [], []
    for idx, c in enumerate(colors_rgb):
        if not (c[0] + c[1] + c[2] < 30*3):
            new_colors_rgb.append(c)
            new_cluster_count.append(cluster_count[idx])

    return new_colors_rgb, new_cluster_count


# unit test
if __name__ == '__main__':
    filename = "./transfer/circle.png"

    start = time.time()
    colors_rgb, color_cluster = get_palette_from_img_by_kmeans(filename, 25, debug=True)

    # 显示提取出的颜色分布
    palette_img = get_bigger_palette_to_show(np.array(colors_rgb))
    pimg = Image.fromarray((palette_img).round().astype(np.uint8))
    pimg.show("pallete")

    print(np.array(colors_rgb))
    print(color_cluster)
    end = time.time()

    print(end-start, 's')
    # ttest()

