#! usr/bin python
# -*- coding: utf-8 -*-
# Description: Use the whole cell-line dataset, do under/over/smote sampling to form a training set.
# Author: Zhuofan Zhang
# Update date: 2021/11/16

#### SAMPLING CONFIG
# under  : undersampling the neg-samples to get small balanced training-set
# over   : oversampling(resampling) the pos-samples to get big balanced training-set
# smote  : use SMOTE to oversampling the pos-samples to get big balanced training-set

#### INPUT JSON FORMAT
# @origin_data_dir
# @origin_data
# @config_lists

import os
import random
import subprocess
import argparse
import pandas as pd
import json
from commonUtils import run_shell_cmd
from imblearn.over_sampling import SMOTE
# from pandas.core.algorithms import mode


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


json_file = open(args.json, 'r')
json_data = json.load(json_file)

origin_data_dir = json_data['origin_data_dir']
origin_data = json_data['origin_data']

# Load file(s)
origin_data_file = []
origin_data_file.append(join_path(origin_data_dir, origin_data['pos_seq']))
origin_data_file.append(join_path(origin_data_dir, origin_data['pos_atac']))
origin_data_file.append(join_path(origin_data_dir, origin_data['pos_bs']))
origin_data_file.append(join_path(origin_data_dir, origin_data['neg_seq']))
origin_data_file.append(join_path(origin_data_dir, origin_data['neg_atac']))
origin_data_file.append(join_path(origin_data_dir, origin_data['neg_bs']))

origin_data_csv = []
for data_file in origin_data_file:
    try:
        origin_data_csv.append(pd.read_csv(data_file, header=None, dtype='a'))
    except ValueError:
        # origin_data_file[i] = None
        origin_data_csv.append(None)


# Get the size of pos/neg dataset
# !!!!! [DIRTY]
pos_size = int(subprocess.check_output(["wc", "-l", origin_data_file[1]]).decode('utf-8').split(" ")[0])
neg_size = int(subprocess.check_output(["wc", "-l", origin_data_file[4]]).decode('utf-8').split(" ")[0])

for config in json_data['config_lists']:
    # Read the config and data path
    mode = config['mode']    # 'under' / 'over' / 'smote'
    outdir = config['out_dir']
    if os.path.isdir(outdir) is not True:
        os.makedirs(outdir)

    #### POSITIVE SAMPLES DIVISION ####
    seed = config['seed']
    random.seed(seed)
    train_pos_idx = random.sample([x for x in range(pos_size)], k=pos_size)
    with open(config['pos_shuffle_list'], 'w+') as ofile:
        json.dump(train_pos_idx, ofile)

    # Oversampling for positive samples of train-set
    if mode == 'over':
        train_pos_idx = random.choices(train_pos_idx, k=neg_size)
        with open(os.path.join(outdir, "pos_oversampling_idx_list.json"), 'w+') as ofile:
            # Save the oversampling result
            json.dump(train_pos_idx, ofile)

    # positive samples of training-set
    train_pos_seq = origin_data_csv[0].iloc[train_pos_idx]
    train_pos_atac = origin_data_csv[1].iloc[train_pos_idx]
    train_pos_bs = origin_data_csv[2].iloc[train_pos_idx]

    if mode != 'smote':
        # Special situation: SMOTE-oversampling
        # The smote need negative samples to work together
        # So here we only output train_pos data in undersampling or oversampling situation.
        # [!!!The smote output case is at the end of this script]
        train_pos_seq.to_csv(os.path.join(outdir, f"trainPos.{mode}.seq.full.csv"), header=False, index=False)
        train_pos_atac.to_csv(os.path.join(outdir, f"trainPos.{mode}.atac.full.csv"), header=False, index=False)
        train_pos_bs.to_csv(os.path.join(outdir, f"trainPos.{mode}.bs.full.csv"), header=False, index=False)

    #### NEGATIVE SAMPLES DIVISION ####
    seed = config['seed']
    random.seed(seed)
    neg_shuffle_list = random.sample([x for x in range(neg_size)], k=neg_size)
    with open(config['neg_shuffle_list'], 'w+') as ofile:
        json.dump(neg_shuffle_list, ofile)

    # negative samples of training-set
    if mode != 'under':  # oversampling / smote
        train_neg_idx = neg_shuffle_list[:neg_size]
    else:
        train_neg_idx = neg_shuffle_list[:pos_size]

    train_neg_seq = origin_data_csv[3].iloc[train_neg_idx]
    train_neg_atac = origin_data_csv[4].iloc[train_neg_idx]
    train_neg_bs = origin_data_csv[5].iloc[train_neg_idx]
    train_neg_seq.to_csv(os.path.join(outdir, f"trainNeg.{mode}.seq.full.csv"), header=False, index=False)
    train_neg_atac.to_csv(os.path.join(outdir, f"trainNeg.{mode}.atac.full.csv"), header=False, index=False)
    train_neg_bs.to_csv(os.path.join(outdir, f"trainNeg.{mode}.bs.full.csv"), header=False, index=False)

    # SMOTE-oversampling training-set output
    if mode == 'smote':
        sm = SMOTE(random_state=seed)
        train_seq = pd.concat([train_pos_seq, train_neg_seq])
        train_atac = pd.concat([train_pos_atac, train_neg_atac])
        train_bs = pd.concat([train_pos_bs, train_neg_bs])
        train_feature = pd.concat([train_seq, train_atac, train_bs], axis=1)
        train_label = [1 for i in range(len(train_pos_idx))] + [0 for i in range(len(train_neg_idx))]
        train_feature_sm, train_label_sm = sm.fit_resample(train_feature.to_numpy(), train_label)
        train_feature_sm = pd.DataFrame(train_feature_sm)
        pos_idx = []
        for idx in range(len(train_label_sm)):
            if train_label_sm[idx] == 1:
                pos_idx.append(idx)
        train_pos_seq_sm = train_feature_sm.iloc[pos_idx, :train_seq.shape[1]]
        train_pos_atac_sm = train_feature_sm.iloc[pos_idx, train_seq.shape[1]:train_seq.shape[1] + train_atac.shape[1]]
        train_pos_bs_sm = train_feature_sm.iloc[pos_idx, train_seq.shape[1] + train_atac.shape[1]:]

        train_pos_seq_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.seq.full.csv"), header=False, index=False)
        train_pos_atac_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.atac.full.csv"), header=False, index=False)
        train_pos_bs_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.bs.full.csv"), header=False, index=False)
