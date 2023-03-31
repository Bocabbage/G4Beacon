#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import os
import json
import argparse
from joblib import dump
from lightgbm import LGBMClassifier
from .dataset import g4SeqEnv
from .commonUtils import joinPath


def train(config):
    vg4seq = config['vg4seq']
    ug4seq = config['ug4seq']
    vg4atac = config['vg4atac']
    ug4atac = config['ug4atac']

    # Load Data
    g4_dataset = g4SeqEnv(
        vg4seq, ug4seq,
        vg4atac, ug4atac,
        None, None,
        None, None,
        False
    )
    train_features = g4_dataset.Features
    train_labels = g4_dataset.Labels

    clf = LGBMClassifier()
    model_param = config['model_config']
    clf.set_params(**model_param)

    if 'categorical_feature' in config.keys():
        start, end = config['categorical_feature']
        categorical_feature_idx = [i for i in range(start, end)]
    else:
        categorical_feature_idx = 'auto'

    clf.fit(
        train_features.to_numpy(),
        train_labels,
        categorical_feature=categorical_feature_idx
    )

    # Save models
    outdir = config["outdir"]
    name = config["name"]
    model_save_name = joinPath(outdir, f"{name}.checkpoint.joblib")
    dump(clf, model_save_name)


def trainOwnData_main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--vg4seqCSV', type=str, help="Positive seq feature file path (CSV).")
    parser.add_argument('--ug4seqCSV', type=str, help="Negative seq feature file path (CSV).")
    parser.add_argument('--vg4atacCSV', type=str, help="Positive atac feature file path (CSV).")
    parser.add_argument('--ug4atacCSV', type=str, help="Negative atac feature file path (CSV).")
    parser.add_argument('--outdir', type=str, help="result output trained-model (JOBLIB).")
    parser.add_argument('--oname', type=str, help="result output trained-model (JOBLIB).")
    args = parser.parse_args(args)

    #### Tmp json-file generation
    config = {
        "name": args.oname,
        "out_dir": args.outdir,
        "vg4seq": args.vg4seqCSV,
        "ug4seq": args.ug4seqCSV,
        "vg4atac": args.vg4atacCSV,
        "ug4atac": args.ug4atacCSV,
        "model_config":
        {
            "seed": 42,
            "learning_rate": 0.1,
            "n_estimators": 1000,
            "objective": "binary"
        },
        "normalization": args.norm
    }

    train(config)
