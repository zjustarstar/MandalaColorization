# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 21:12:26 2020

@author: lenovo
"""

import itertools
import numpy as np
import random
import math

from util import distance


def sample_bins(img_pixel_cnt, bin_cnt=16):
    bin_range = 256 // bin_cnt # the pixel range each bin contain

    tmp = {}
    for x in itertools.product(range(bin_cnt),repeat=3):
        tmp[x] = {'val': np.array([0,0,0]), 'cnt': 0}
    for pixel, cnt in img_pixel_cnt.items():
        idx = tuple([c // bin_range for c in pixel])
        tmp[idx]['val'] += np.array(pixel) * cnt
        tmp[idx]['cnt'] += cnt

    res = {}
    for bin_item in tmp.values():
        if bin_item['cnt'] != 0:
            res[tuple((bin_item['val'] / bin_item['cnt']))] = bin_item['cnt']

    return res


def init_means(bins, k=5):

    def attenuation(color,last_mean):
        return 1 - math.exp(((distance(color, last_mean) / 80) ** 2) * -1)

    res = []
    bins = {k: v for k, v in sorted(bins.items(), key=lambda item: item[1], reverse=True)}
    # for color, cnt in bins.items():
    for _ in range(k):
        for color,cnt in bins.items():
            if color not in res: 
                res.append(color)
                break
        bins = {k: v * attenuation(k,res[-1]) for k, v in bins.items()}
        bins = {k: v for k, v in sorted(bins.items(), key=lambda item: item[1], reverse=True)}

    return res


def k_means(bins, k, init_mean=True, sortby='L', max_iter=1000, black=True):
    '''
    利用kmeans获得pallete
    :param bins:
    :param k:
    :param init_mean:
    :param max_iter:
    :param black: 增加一个额外的black类，但是最终不输出
    :param sortby: L 表示按照亮度从大到小输出，否则按照每个聚类的像素个数从大到小输出
    :return:
    '''
    blk = [0, 128, 128]
    if init_mean is False: means = random.sample(list(bins),k)
    else: means = init_means(bins, k)
    if black: means.append(blk)
    means = np.array(means)
    
    mean_cnt = means.shape[0]

    cluster_cnt = np.zeros(mean_cnt)
    for _ in range(max_iter):
        # print('\niter %d...' % _)
        cluster_sum = [np.array([0,0,0],dtype=float) for i in range(mean_cnt)]
        cluster_cnt = np.zeros(mean_cnt)
        for color, cnt in bins.items():
            color = np.array(color)	
            dists = [distance(color,mean) for mean in means]
            cluster_th = dists.index(min(dists))
            cluster_sum[cluster_th] += color * cnt
            cluster_cnt[cluster_th] += cnt

        new_means = [cluster_sum[i] / cluster_cnt[i] if cluster_cnt[i] > 0 else [0,0,0] for i in range(k)]
        if black: new_means.append(blk)
        new_means = np.array(new_means)
        if (new_means == means).all(): break
        else: means = new_means
        # print(means)

    #按照LAB空间的亮度(第一列)输出
    if sortby == 'L':
        arg_th = np.argsort(means[:k], axis=0)[:,0][::-1]
    else:
        arg_th = np.argsort(cluster_cnt[:k])[::-1]
    
    #print(means)
    return means[arg_th], cluster_cnt[arg_th]