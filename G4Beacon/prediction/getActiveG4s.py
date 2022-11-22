#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2022/10/17
# Author: Zhuofan Zhang
import os
import json
import numpy as np
import argparse
import joblib
from torch import load
from dataset import g4SeqEnv
from model import SeqEnvCNN
from commonUtils import join_path

# ---------------------- main ---------------------- #
parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, help="Input predict config file.")
args = parser.parse_args()

# Read JSON-config
jsonFile = open(args.json, 'r')
jsonData = json.load(jsonFile)

datasetDir = jsonData['dataset_dir']
outdir = jsonData['out_dir']
# tfp_tfn = jsonData['tfp_tfn']
if outdir != '' and os.path.isdir(outdir) is not True:
    os.makedirs(outdir)

for data in jsonData['data_list']:
    # Load Data
    vg4seq = join_path(datasetDir, data['vg4seq'])
    ug4seq = join_path(datasetDir, data['ug4seq'])
    vg4atac = join_path(datasetDir, data['vg4atac'])
    ug4atac = join_path(datasetDir, data['ug4atac'])
    vg4bs = join_path(datasetDir, data['vg4bs'])
    ug4bs = join_path(datasetDir, data['ug4bs'])
    vg4atacFd = join_path(datasetDir, data['vg4atac-fd'])
    ug4atacFd = join_path(datasetDir, data['ug4atac-fd'])
    norm = data["normalization"]
    #### New option
    originBed = join_path(datasetDir, data['origin-bed'])
    resultFile = join_path(outdir, data['result-file'])

    g4Dataset = g4SeqEnv(
        vg4seq, ug4seq,
        vg4atac, ug4atac,
        vg4atacFd, ug4atacFd,
        vg4bs, ug4bs,
        norm
    )
    testData = g4Dataset.Features
    testLabels = g4Dataset.Labels

    checkpoint = data['checkpoint']
    name = data['name']
    if "pth" in checkpoint:
        cpt = load(checkpoint)  # torch-load
        clf = SeqEnvCNN(shape=data['shape'])
        clf.load_state_dict(cpt['model_state_dict'])
        y_pred = clf.predict_proba(testData.to_numpy().astype(np.float32))
    else:
        clf = joblib.load(checkpoint)
        y_pred = clf.predict_proba(testData.to_numpy())

    y_pred_proba = y_pred
    # y_pred = np.argmax(y_pred, axis=1)
    assert(len(y_pred) == len(testData))
    with open(originBed, 'r') as rfile:
        with open(resultFile, 'w+') as wfile:
            for idx, line in enumerate(rfile.readlines()):
                line = f"{line.strip()}\t{y_pred_proba[idx][1]:.5f}\n"
                wfile.write(line)
                # if y_pred[idx] == 1:
                #     wfile.write(line)
