#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import os
import random
import pandas as pd
import argparse


def trainingsetBalance(config):
    r"""
        Positive-sample oversampling.
    """
    # Read config-params
    origin_data_file = []
    origin_data_file.append(config["origin_data"]['pos_seq'])
    origin_data_file.append(config["origin_data"]['pos_atac'])
    origin_data_file.append(config["origin_data"]['neg_seq'])
    origin_data_file.append(config["origin_data"]['neg_atac'])

    outdir = config["out_dir"]
    if os.path.isdir(outdir) is not True:
        os.makedirs(outdir)

    seed = config['seed']
    random.seed(seed)

    # Load file(s)
    origin_data_csv = []
    for data_file in origin_data_file:
        try:
            origin_data_csv.append(pd.read_csv(data_file, header=None, dtype='a'))
        except ValueError:
            origin_data_csv.append(None)
    pos_size = len(origin_data_csv[1])
    neg_size = len(origin_data_csv[3])

    # Positive sample oversampling
    train_pos_idx = random.sample([x for x in range(pos_size)], k=pos_size)
    train_pos_idx = random.choices(train_pos_idx, k=neg_size)
    train_pos_seq = origin_data_csv[0].iloc[train_pos_idx]
    train_pos_atac = origin_data_csv[1].iloc[train_pos_idx]
    train_pos_seq.to_csv(os.path.join(outdir, f"trainPos.seq.full.csv"), header=False, index=False)
    train_pos_atac.to_csv(os.path.join(outdir, f"trainPos.atac.full.csv"), header=False, index=False)

    # Negative sample shuffling
    neg_shuffle_list = random.sample([x for x in range(neg_size)], k=neg_size)
    train_neg_idx = neg_shuffle_list[:neg_size]
    train_neg_seq = origin_data_csv[2].iloc[train_neg_idx]
    train_neg_atac = origin_data_csv[3].iloc[train_neg_idx]
    train_neg_seq.to_csv(os.path.join(outdir, f"trainNeg.seq.full.csv"), header=False, index=False)
    train_neg_atac.to_csv(os.path.join(outdir, f"trainNeg.atac.full.csv"), header=False, index=False)


def trainingsetConstruct_main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--vg4seqCSV', type=str, help="Positive seq feature file path (CSV).")
    parser.add_argument('--ug4seqCSV', type=str, help="Negative seq feature file path (CSV).")
    parser.add_argument('--vg4atacCSV', type=str, help="Positive atac feature file path (CSV).")
    parser.add_argument('--ug4atacCSV', type=str, help="Negative atac feature file path (CSV).")
    parser.add_argument('--outdir', type=str, default="./", help="output file dir.")
    parser.add_argument('--seed', type=int, default=42, help="Random-seed for sampling.")

    args = parser.parse_args(args)
    config = {
        "seed": 42,
        "out_dir": args.outdir,
        "origin_data":
        {
            "pos_seq": args.vg4seqCSV,
            "neg_seq": args.ug4seqCSV,
            "pos_atac": args.vg4atacCSV,
            "neg_atac": args.ug4atacCSV
        },
    }

    trainingsetBalance(config)
