#! usr/bin python
# -*- coding: utf-8 -*-
# Description: Use the whole cell-line dataset, combine under- and over-sampling to form a training set.
# Author: Zhuofan Zhang
# Update date: 2022/05/04
import os
import argparse
import json
import pandas as pd
import numpy as np
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


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


with open(args.json, 'r') as json_file:
    json_data = json.load(json_file)

origin_data_dir = json_data['origin_data_dir']
origin_data = json_data['origin_data']

# Load file(s)
origin_data_key = ["pos_seq", "pos_atac", "neg_seq", "neg_atac"]
origin_data_file = []
origin_data_file.append(join_path(origin_data_dir, origin_data['pos_seq']))
origin_data_file.append(join_path(origin_data_dir, origin_data['pos_atac']))
origin_data_file.append(join_path(origin_data_dir, origin_data['neg_seq']))
origin_data_file.append(join_path(origin_data_dir, origin_data['neg_atac']))

origin_data_csv = {}
for idx, data_file in enumerate(origin_data_file):
    try:
        origin_data_csv[origin_data_key[idx]] = pd.read_csv(data_file, header=None, dtype='a')
    except ValueError:
        # origin_data_file[i] = None
        origin_data_csv[origin_data_key[idx]] = None

posFeatures = pd.concat(
    [origin_data_csv['pos_seq'], origin_data_csv['pos_atac']],
    axis=1, ignore_index=True
)
negFeatures = pd.concat(
    [origin_data_csv['neg_seq'], origin_data_csv['neg_atac']],
    axis=1, ignore_index=True
)

posLabels = [1 for x in range(len(posFeatures))]
negLabels = [0 for x in range(len(negFeatures))]


for config in json_data['config_lists']:
    # read the config-params
    over_rate = config['over_rate']
    under_rate = config['under_rate']
    random_state = config['seed']
    outdir = config['out_dir']
    if os.path.isdir(outdir) is not True:
        os.makedirs(outdir)

    originFeatures = pd.concat([posFeatures, negFeatures], axis=0, ignore_index=True)
    originLabels = np.array(posLabels + negLabels)

    # 1. over-sampling the minority-class and make Nr[minor]/N[major] ratio to over_rate
    # 2. under-sampling the majority-class and make Nr[minor]/Nr[major] ratio to under_rate
    overSampler = RandomOverSampler(sampling_strategy=over_rate, random_state=random_state)
    underSampler = RandomUnderSampler(sampling_strategy=under_rate, random_state=random_state)

    overFeatures, overLabels = overSampler.fit_resample(originFeatures, originLabels)
    resFeatures, resLabels = underSampler.fit_resample(overFeatures, overLabels)

    resFeatures = pd.DataFrame(resFeatures)
    resPosFeatures = resFeatures[resLabels == 1]
    resNegFeatures = resFeatures[resLabels == 0]

    # Dirty: do not include the situation of seq-only and atac-only situation
    resSeqPosFeatures = resPosFeatures.iloc[:, :origin_data_csv["pos_seq"].shape[1]]
    resATACPosFeatures = resPosFeatures.iloc[:, origin_data_csv["pos_seq"].shape[1]:]
    resSeqNegFeatures = resNegFeatures.iloc[:, :origin_data_csv["neg_seq"].shape[1]]
    resATACNegFeatures = resNegFeatures.iloc[:, origin_data_csv["neg_seq"].shape[1]:]

    # Write-out to the file
    resSeqPosFeatures.to_csv(join_path(outdir, f"trainPos.seq.full.csv"), header=False, index=False)
    resATACPosFeatures.to_csv(join_path(outdir, f"trainPos.atac.full.csv"), header=False, index=False)
    resSeqNegFeatures.to_csv(join_path(outdir, f"trainNeg.seq.full.csv"), header=False, index=False)
    resATACNegFeatures.to_csv(join_path(outdir, f"trainNeg.atac.full.csv"), header=False, index=False)
