#! usr/bin python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2022/01/21
import os
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')


def join_path(firstpath, secondpath):
    try:
        path = os.path.join(firstpath, secondpath)
    except TypeError:
        # One or both of the path(s) is/are None
        path = None
    return path


parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, help="Input division configuration.")
args = parser.parse_args()

#### Load config-json file
with open(args.json, 'r') as json_file:
    json_data = json.load(json_file)

dataDirs = json_data['data-dirs']

for dataDir in dataDirs:
    dataPath = dataDir['data-path']
    for data in dataDir['data-list']:
        features = pd.read_csv(join_path(dataPath, data['csv']), dtype='a', header=None)
        features = features.to_numpy(dtype="float32")
        firstDiffFeatures = np.diff(features, axis=1)
        np.savetxt(join_path(dataPath, data['first-diff-csv']), firstDiffFeatures, delimiter=',')

        if 'plot' in data.keys():
            fig, ax = plt.subplots(figsize=(12, 10))
            mean_firstDiffFeatures = np.mean(firstDiffFeatures, axis=0)
            ax.plot(mean_firstDiffFeatures)
            ax.set_ylim([-5, 5])
            fig.savefig(join_path(dataPath, data['plot']))
