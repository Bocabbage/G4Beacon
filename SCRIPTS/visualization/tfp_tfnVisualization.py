#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/12/20
# Author: Zhuofan Zhang
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
from sklearn.preprocessing import normalize
from commonUtils import join_path
use('Agg')

# ----------------- main ----------------- #

parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str)
args = parser.parse_args()

## Load json-config
with open(args.json, 'r') as jfile:
    json_data = json.load(jfile)

data_list = json_data['data_list']
file_dir = json_data['file_dir']
output_file = json_data['output_file']
nrows, ncols = json_data['subplots_layout']
normalization = json_data['normalization']
title = json_data['title']

## draw pics in data_list configs
fig, axes = plt.subplots(nrows, ncols, figsize=(12, 12))
for idx, data in enumerate(data_list):
    # Select the fig
    ridx = idx // ncols
    cidx = idx % ncols
    try:
        ax = axes[ridx, cidx]
    except IndexError:
        # 1-D situation
        ax = axes[idx]

    for key in data['files'].keys():
        feature = np.genfromtxt(join_path(file_dir, data['files'][key]), delimiter=',')
        if normalization:
            feature = normalize(feature, norm='l2')
        feature = np.mean(feature, axis=0)
        ax.plot(feature, label=key)

    ax.legend(loc="lower right")
    ax.set_title(data['subtitle'], size=10)

fig.suptitle(title, fontsize=14)
fig.savefig(output_file)
