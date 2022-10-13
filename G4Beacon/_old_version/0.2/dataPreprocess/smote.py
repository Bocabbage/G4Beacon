#! usr/bin python
# -*- coding: utf-8 -*-
# Description: oversampling the positive train samples with SMOTE
# Author: Zhuofan Zhang
# Update date: 2021/08/15
import os
import numpy as np
import argparse
import pandas as pd
from imblearn.over_sampling import SMOTE

parser = argparse.ArgumentParser()
parser.add_argument('-p', type=str, help="positive training atac data.")
parser.add_argument('-n', type=str, help="negative training atac data.")
parser.add_argument('--name', type=str, default="atac", help="feature types: seq/atac/bs.")
parser.add_argument('--seed', type=int, default=42, help="random sampling seed.")
parser.add_argument('--outdir', type=str, default='./', help="output file dir.")
args = parser.parse_args()

sm = SMOTE(random_state=args.seed)

if os.path.isdir(args.outdir) is not True:
    os.makedirs(args.outdir)

epData = pd.read_csv(args.p, dtype='a', header=None)
enData = pd.read_csv(args.n, dtype='a', header=None)

eData = pd.concat([epData, enData])
eLabel = [1 for i in range(epData.shape[0])] + [0 for i in range(enData.shape[0])]
eDataSmote, eLabelSmote = sm.fit_resample(eData, eLabel)
posIdx = []
for idx in range(len(eLabelSmote)):
    if eLabelSmote[idx] == 1:
        posIdx.append(idx)

epDataSmote = eDataSmote.iloc[posIdx]

# Set the result name
trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.smote".format(args.seed))
epDataSmote.to_csv(trainPosPrefix + ".{}.csv".format(args.name), header=False, index=False)
