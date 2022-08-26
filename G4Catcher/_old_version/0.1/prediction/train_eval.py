#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/08/10(unfinished)
# Author: Zhuofan Zhang
import os
import argparse
# import pandas as pd
# import lightgbm
from joblib import dump
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from dataset import g4SeqEnv

parser = argparse.ArgumentParser()
parser.add_argument('--vg4seq', type=str, default=None, help="Vg4 Sequence file.")
parser.add_argument('--ug4seq', type=str, default=None, help="Ug4 Sequence file.")
parser.add_argument('--vg4atac', type=str, default=None, help="Vg4 Env file.")
parser.add_argument('--ug4atac', type=str, default=None, help="Ug4 Env file.")
parser.add_argument('--vg4bs', type=str, default=None, help="Vg4 Env file.")
parser.add_argument('--ug4bs', type=str, default=None, help="Ug4 Env file.")

parser.add_argument('--mode', type=str, default='train', help="train/validation mode.")
parser.add_argument('--extend', type=int, default=None,
                    help="Seq extend parameter: select [mid-extend, mid+extend] from seq-features.")
parser.add_argument('--nocategory', action="store_false", default=True, dest="category")

parser.add_argument('--name', type=str, help="Saved model file name.")
parser.add_argument('--savedir', type=str, default='./', help="Directory to save trained models.")
parser.add_argument('--model', type=str, default='lightGBM', help="Model to use.")
parser.add_argument('--lr', type=float, default=0.1, help="Learning rate.")
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--nestims', type=int, default=1000, help="For Xgboost: n estimators.")

args = parser.parse_args()

# Load Data
g4Dataset = g4SeqEnv(
    args.vg4seq, args.ug4seq,
    args.vg4atac, args.ug4atac,
    args.vg4bs, args.ug4bs,
    args.extend)


if args.mode == 'train':
    if args.model == 'Xgboost':
        # Hyper-parameters
        xgb_params = {
            'seed': args.seed,
            'learning_rate': args.lr,
            'gamma': 0.3,
            'subsample': 0.7,
            'colsample_bytree': 0.8,
            'n_estimators': args.nestims
        }

        # trainData = pd.concat([g4Dataset.seqFeatures, g4Dataset.envFeatures], axis=1)
        trainData = g4Dataset.Features
        trainLabels = g4Dataset.Labels
        xgb = XGBClassifier()
        xgb.set_params(**xgb_params)
        xgb.fit(trainData.to_numpy(), trainLabels)
        modelSaveDir = os.path.join(
            args.savedir,
            '{}_XGBOOST_lr{}_{}estimators.checkpoint.joblib'.format(args.name, args.lr, args.nestims))
        dump(xgb, modelSaveDir)

    elif args.model == 'lightGBM':
        lgb_params = {
            'seed': args.seed,
            'learning_rate': args.lr,
            'objective': 'binary',
            'n_estimators': args.nestims
        }

        # trainData = pd.concat([g4Dataset.seqFeatures, g4Dataset.envFeatures], axis=1)
        trainData = g4Dataset.Features
        trainLabels = g4Dataset.Labels
        lgb = LGBMClassifier()
        lgb.set_params(**lgb_params)
        if args.category:
            lgb.fit(
                trainData.to_numpy(),
                trainLabels,
                # categorical_feature=[x for x in range(g4Dataset.Features.shape[1])]
            )
        else:
            lgb.fit(
                trainData.to_numpy(),
                trainLabels,
            )
        modelSaveDir = os.path.join(
            args.savedir,
            '{}_LGB_lr{}_{}estimators.checkpoint.joblib'.format(args.name, args.lr, args.nestims))
        dump(lgb, modelSaveDir)

    else:
        raise ValueError("--name option: lightGBM or Xgboost.")

elif args.mode == 'eval':
    pass
