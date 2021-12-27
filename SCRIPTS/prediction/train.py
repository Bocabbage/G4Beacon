#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/12/10
# Author: Zhuofan Zhang
import os
import json
import argparse
from joblib import dump
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier, Dataset
from imbalanced_ensemble.ensemble import SelfPacedEnsembleClassifier
from dataset import g4SeqEnv
from commonUtils import join_path

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default='train', help="train/validation mode.")
parser.add_argument('--json', type=str, help="training configuration json file.")
args = parser.parse_args()

with open(args.json, 'r') as jfile:
    jsonData = json.load(jfile)
dataset_dir = jsonData['dataset_dir']
outdir = jsonData['out_dir']

if os.path.isdir(outdir) is not True:
    os.makedirs(outdir)

if args.mode == 'train':
    for config in jsonData['config_list']:
        vg4seq = join_path(dataset_dir, config['vg4seq'])
        ug4seq = join_path(dataset_dir, config['ug4seq'])
        vg4atac = join_path(dataset_dir, config['vg4atac'])
        ug4atac = join_path(dataset_dir, config['ug4atac'])
        vg4bs = join_path(dataset_dir, config['vg4bs'])
        ug4bs = join_path(dataset_dir, config['ug4bs'])

        norm = config['normalization']

        # Load Data
        g4_dataset = g4SeqEnv(
            vg4seq, ug4seq,
            vg4atac, ug4atac,
            vg4bs, ug4bs,
            norm
        )

        model = config['model']
        model_param = config['model_config']
        if model == 'Xgboost':
            clf = XGBClassifier()
        elif model == 'lightGBM':
            model_param = config['model_config']
            clf = LGBMClassifier()

            # Use Dataset API
            lgbm_dataset = Dataset(
                g4_dataset.Features.to_numpy(),
                label=g4_dataset.Labels
            )

        elif model == 'SPE':
            basic_model = config['basic_model']
            if basic_model == 'lightGBM':
                basic_clf = LGBMClassifier()
                basic_model_config = config['basic_model_config']
                basic_clf.set_params(**basic_model_config)
                clf = SelfPacedEnsembleClassifier(base_estimator=basic_clf)
            else:  # Default: DecisionTree
                clf = SelfPacedEnsembleClassifier()
        else:
            clf = None  # Will raise an error

        if 'categorical_feature' in config.keys():
            # Old version (for 20211118_01train_full-under.json):
            # model_param['categorical_feature'] = categorical_feature_idx
            # clf.set_params(**model_param)
            start, end = config['categorical_feature']
            categorical_feature_idx = [i for i in range(start, end)]
        else:
            categorical_feature_idx = 'auto'

        train_features = g4_dataset.Features
        train_labels = g4_dataset.Labels
        clf.set_params(**model_param)
        clf.fit(
            train_features.to_numpy(),
            train_labels,
            categorical_feature=categorical_feature_idx
        )

        # Save models
        name = config['name']
        model_save_name = join_path(outdir, f"{name}_{model}.checkpoint.joblib")
        dump(clf, model_save_name)
else:
    pass
