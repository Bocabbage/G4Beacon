#! usr/bin python
# -*- coding: utf-8 -*-
# Description: divide feature files to train/test set
# Author: Zhuofan Zhang
# Update date: 2021/11/10

#### SAMPLING CONFIG
# under  : undersampling the neg-samples to get small balanced training-set
# over   : oversampling(resampling) the pos-samples to get big balanced training-set
# smote  : use SMOTE to oversampling the pos-samples to get big balanced training-set
# trivial: keep the imbalanced training-set without preprocessing [can be used by imbalanced-ensemble methods]

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
    mode = config['mode']    # 'under' or 'over'
    filt_list = join_path(origin_data_dir, config['filt_list'])

    outdir = config['out_dir']
    if os.path.isdir(outdir) is not True:
        os.makedirs(outdir)

    #### POSITIVE SAMPLES DIVISION ####
    # 2 Situation:
    # @1: shuffle_list is existed file -- use the given pos data directly
    # @2: shuffle list is not exsited -- do sampling to get shuffle_list and save it
    if os.path.isfile(config['pos_shuffle_list']):
        # Do not create any new file: just link(soft) the exist file to the output dir.
        # positive samples of training-set
        exist_dir = os.path.dirname(config['pos_shuffle_list'])
        exist_pos_seq = os.path.join(exist_dir, f"trainPos.{mode}.seq.csv")
        exist_pos_atac = os.path.join(exist_dir, f"trainPos.{mode}.atac.csv")
        exist_pos_bs = os.path.join(exist_dir, f"trainPos.{mode}.bs.csv")
        target_pos_seq = os.path.join(outdir, f"trainPos.{mode}.seq.csv")
        target_pos_atac = os.path.join(outdir, f"trainPos.{mode}.atac.csv")
        target_pos_bs = os.path.join(outdir, f"trainPos.{mode}.bs.csv")
        run_shell_cmd(f"ln -s {exist_pos_seq} {target_pos_seq}")
        run_shell_cmd(f"ln -s {exist_pos_atac} {target_pos_atac}")
        run_shell_cmd(f"ln -s {exist_pos_bs} {target_pos_bs}")

        # positive samples of test-set
        exist_pos_seq = os.path.join(exist_dir, f"testPos.{mode}.seq.csv")
        exist_pos_atac = os.path.join(exist_dir, f"testPos.{mode}.atac.csv")
        exist_pos_bs = os.path.join(exist_dir, f"testPos.{mode}.bs.csv")
        target_pos_seq = os.path.join(outdir, f"testPos.{mode}.seq.csv")
        target_pos_atac = os.path.join(outdir, f"testPos.{mode}.atac.csv")
        target_pos_bs = os.path.join(outdir, f"testPos.{mode}.bs.csv")
        run_shell_cmd(f"ln -s {exist_pos_seq} {target_pos_seq}")
        run_shell_cmd(f"ln -s {exist_pos_atac} {target_pos_atac}")
        run_shell_cmd(f"ln -s {exist_pos_bs} {target_pos_bs}")

        # link the shuffle_list
        target_shuffle_list = os.path.join(outdir, os.path.basename(config['pos_shuffle_list']))
        run_shell_cmd(f"ln -s {config['pos_shuffle_list']} {target_shuffle_list}")
    else:
        seed = config['seed']
        random.seed(seed)
        pos_shuffle_list = random.sample([x for x in range(pos_size)], k=pos_size)
        with open(config['pos_shuffle_list'], 'w+') as ofile:
            json.dump(pos_shuffle_list, ofile)
        train_pos_idx = pos_shuffle_list[:(pos_size // 2)]

        # Oversampling for positive samples of train-set
        if mode == 'over':
            train_pos_idx = random.choices(train_pos_idx, k=(neg_size // 2))
            with open(os.path.join(outdir, "pos_oversampling_idx_list.json"), 'w+') as ofile:
                # Save the oversampling result
                json.dump(train_pos_idx, ofile)
        test_pos_idx = pos_shuffle_list[(pos_size // 2):]

        # positive samples of training-set
        train_pos_seq = origin_data_csv[0].iloc[train_pos_idx]
        train_pos_atac = origin_data_csv[1].iloc[train_pos_idx]
        train_pos_bs = origin_data_csv[2].iloc[train_pos_idx]

        if mode != 'smote':
            # Special situation: SMOTE-oversampling
            # The smote need negative samples to work together
            # So here we only output train_pos data in undersampling or oversampling situation.
            # [!!!The smote output case is at the end of this script]
            train_pos_seq.to_csv(os.path.join(outdir, f"trainPos.{mode}.seq.csv"), header=False, index=False)
            train_pos_atac.to_csv(os.path.join(outdir, f"trainPos.{mode}.atac.csv"), header=False, index=False)
            train_pos_bs.to_csv(os.path.join(outdir, f"trainPos.{mode}.bs.csv"), header=False, index=False)

        # positive samples of test-set
        test_pos_seq = origin_data_csv[0].iloc[test_pos_idx]
        test_pos_atac = origin_data_csv[1].iloc[test_pos_idx]
        test_pos_bs = origin_data_csv[2].iloc[test_pos_idx]
        test_pos_seq.to_csv(os.path.join(outdir, f"testPos.{mode}.seq.csv"), header=False, index=False)
        test_pos_atac.to_csv(os.path.join(outdir, f"testPos.{mode}.atac.csv"), header=False, index=False)
        test_pos_bs.to_csv(os.path.join(outdir, f"testPos.{mode}.bs.csv"), header=False, index=False)

    #### NEGATIVE SAMPLES DIVISION ####
    if os.path.isfile(config['neg_shuffle_list']):
        with open(config['neg_shuffle_list'], 'r') as rfile:
            neg_shuffle_list = json.load(rfile)

        # negative samples of test-set
        exist_neg_seq = os.path.join(exist_dir, f"testNeg.{mode}.seq.csv")
        exist_neg_atac = os.path.join(exist_dir, f"testNeg.{mode}.atac.csv")
        exist_neg_bs = os.path.join(exist_dir, f"testNeg.{mode}.bs.csv")
        target_neg_seq = os.path.join(outdir, f"testNeg.{mode}.seq.csv")
        target_neg_atac = os.path.join(outdir, f"testNeg.{mode}.atac.csv")
        target_neg_bs = os.path.join(outdir, f"testNeg.{mode}.bs.csv")
        run_shell_cmd(f"ln -s {exist_neg_seq} {target_neg_seq}")
        run_shell_cmd(f"ln -s {exist_neg_atac} {target_neg_atac}")
        run_shell_cmd(f"ln -s {exist_neg_bs} {target_neg_bs}")
    else:
        seed = config['seed']
        random.seed(seed)
        neg_shuffle_list = random.sample([x for x in range(neg_size)], k=neg_size)
        with open(config['neg_shuffle_list'], 'w+') as ofile:
            json.dump(neg_shuffle_list, ofile)
        test_neg_idx = neg_shuffle_list[(neg_size // 2):]

        # negative samples of test-set
        test_neg_seq = origin_data_csv[3].iloc[test_neg_idx]
        test_neg_atac = origin_data_csv[4].iloc[test_neg_idx]
        test_neg_bs = origin_data_csv[5].iloc[test_neg_idx]
        test_neg_seq.to_csv(os.path.join(outdir, f"testNeg.{mode}.seq.csv"), header=False, index=False)
        test_neg_atac.to_csv(os.path.join(outdir, f"testNeg.{mode}.atac.csv"), header=False, index=False)
        test_neg_bs.to_csv(os.path.join(outdir, f"testNeg.{mode}.bs.csv"), header=False, index=False)

    # negative samples of training-set
    if mode != 'under':  # oversampling/trivial/smote
        train_neg_idx = neg_shuffle_list[:(neg_size // 2)]
    else:
        train_neg_idx = neg_shuffle_list[:(pos_size // 2)]
    if filt_list:
        filt_neg_idx = []
        with open(filt_list, 'r') as rfile:
            for line in rfile.readlines():
                filt_neg_idx.append(int(line.strip()) - 1)  # -1 for the index in filt_list starts from 1
        train_neg_idx_filted = []
        for idx in train_neg_idx:
            if idx not in filt_neg_idx:
                train_neg_idx_filted.append(idx)
        train_neg_seq = origin_data_csv[3].iloc[train_neg_idx_filted]
        train_neg_atac = origin_data_csv[4].iloc[train_neg_idx_filted]
        train_neg_bs = origin_data_csv[5].iloc[train_neg_idx_filted]
    else:
        train_neg_seq = origin_data_csv[3].iloc[train_neg_idx]
        train_neg_atac = origin_data_csv[4].iloc[train_neg_idx]
        train_neg_bs = origin_data_csv[5].iloc[train_neg_idx]
    train_neg_seq.to_csv(os.path.join(outdir, f"trainNeg.{mode}.seq.csv"), header=False, index=False)
    train_neg_atac.to_csv(os.path.join(outdir, f"trainNeg.{mode}.atac.csv"), header=False, index=False)
    train_neg_bs.to_csv(os.path.join(outdir, f"trainNeg.{mode}.bs.csv"), header=False, index=False)

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

        train_pos_seq_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.seq.csv"), header=False, index=False)
        train_pos_atac_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.atac.csv"), header=False, index=False)
        train_pos_bs_sm.to_csv(os.path.join(outdir, f"trainPos.{mode}.bs.csv"), header=False, index=False)
