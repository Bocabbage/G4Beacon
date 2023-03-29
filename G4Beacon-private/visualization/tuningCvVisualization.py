#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/12/17
# Author: Zhuofan Zhang
import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
from commonUtils import join_path
use('Agg')

parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str)
args = parser.parse_args()

with open(args.json, 'r') as jfile:
    json_data = json.load(jfile)

#### Load json-config / grid-search cv result file ####
params_grid = json_data['params_grid']
work_dir = json_data['work_dir']
gscv = np.load(join_path(work_dir, json_data['gscv_result']))
criterion = ['acc', 'pre', 'rec', 'f1score', 'auroc', 'AP']


## check hyer-params' length
for idx, key in enumerate(params_grid.keys()):
    assert(gscv.shape[idx] == len(params_grid[key]))

#### write best-on-each-criteria log ####
with open(join_path(work_dir, "best-of-criterion.txt"), 'w+') as ofile:
    for criteria in criterion:
        mat = gscv[criteria]
        argmax_idices = np.unravel_index(mat.argmax(), mat.shape)
        best_res = mat[argmax_idices]
        ofile.write(f"Best {criteria}: {best_res}\t[")
        for i, key in enumerate(params_grid.keys()):
            ofile.write(f"{key}:{params_grid[key][argmax_idices[i]]}\t")
        ofile.write("]\n")


#### for each hyper-params, write box plot ####
for i, key in enumerate(params_grid.keys()):
    fig, axes = plt.subplots(2, 3, figsize=(12, 12))  # rol2, col3
    swapaxes_gscv = np.swapaxes(gscv, 0, i)
    for idx, criteria in enumerate(criterion):
        # select the subplot
        axi = idx // 3
        axj = idx % 3
        ax = axes[axi, axj]

        mat = swapaxes_gscv[criteria]
        data = []
        xlabels = []
        for k in range(mat.shape[0]):
            data.append(mat[k].ravel())
            xlabels.append(params_grid[key][k])

        ax.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
        ax.set(
            axisbelow=True,  # Hide the grid behind plot objects
            xlabel=f'{key}',
            ylabel=f"{criteria}",
            yticks=[0.1 * x for x in range(11)]
        )
        ax.set_xticklabels(
            xlabels,
        )
        ax.set_title(f"{criteria} results for {key} tuning", size=10)

    # axes[-1, -1].axis('off')  # Don't show the last empty subplot
    fig.suptitle(f"CV results for {key} tuning", fontsize=14)
    fig.savefig(join_path(work_dir, f"{key}-tuning-boxplots.png"))
    fig.savefig(join_path(work_dir, f"{key}-tuning-boxplots.pdf"))
