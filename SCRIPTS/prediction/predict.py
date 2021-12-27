#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/12/20
# Author: Zhuofan Zhang
import os
import json
import numpy as np
import argparse
import joblib
import matplotlib
import matplotlib.pyplot as plt
from dataset import g4SeqEnv
from sklearn.metrics import accuracy_score, recall_score, precision_score, auc, roc_curve
from sklearn.metrics import precision_recall_curve, average_precision_score, PrecisionRecallDisplay, RocCurveDisplay
from commonUtils import join_path
matplotlib.use('Agg')


# ------------ Function Def ------------ #

def plot_roc(ax, y, y_pred, name: str) -> None:
    y_pred = y_pred[:, 1]
    fpr, tpr, _ = roc_curve(y, y_pred)
    roc_auc = auc(fpr, tpr)
    viz = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name=name)
    viz.plot(ax=ax, name=name)

    ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05], title="ROC Curve")
    ax.legend(loc="lower right")


def plot_pr(ax, y, y_pred, name: str) -> None:
    y_pred = y_pred[:, 1]
    precision, recall, _ = precision_recall_curve(y, y_pred)
    average_precision = average_precision_score(y, y_pred)
    viz = PrecisionRecallDisplay(
        precision=precision,
        recall=recall,
        average_precision=average_precision,
        estimator_name=name
    )
    viz.plot(ax=ax, name=name)

    ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05], title="Precision-Recall Curve")
    ax.legend(loc="lower right")


def get_tfp_tfn(outdir: str, features, y, y_pred, name: str) -> None:
    r'''
        Take the true-labels and predict-labels as input,
        write tp/fp/tn/fn sample features into divided files.
    '''
    ## Hash map of y and y_p
    ## Notice that as Python3.6 kept the key-order, this map is not neccesary.
    ## Calculate mathod: (y << 1) + y_p
    hash_y2s = ['tn', 'fp', 'fn', 'tp']

    file_dict = {
        'tn': {'feature_file': None, 'proba_file': None},
        'fp': {'feature_file': None, 'proba_file': None},
        'fn': {'feature_file': None, 'proba_file': None},
        'tp': {'feature_file': None, 'proba_file': None},
    }

    for key in file_dict.keys():
        file_dict[key]['feature_file'] = open(join_path(outdir, f"{key}_{name}.csv"), 'w+')
        file_dict[key]['proba_file'] = open(join_path(outdir, f"{key}Proba_{name}.txt"), 'w+')

    # Log the index of each sample in different types(tp/tn/fp/fn)
    indices = {
        'tn': [],
        'fp': [],
        'fn': [],
        'tp': [],
    }

    y_p = np.argmax(y_pred, axis=1)
    for idx in range(len(y_p)):
        result_type = hash_y2s[(y[idx] << 1) + y_p[idx]]
        indices[result_type].append(idx)
        file_dict[result_type]['proba_file'].write(f"idx{idx}: {y_pred[idx]}\n")

    for key in indices.keys():
        features.iloc[indices[key], :].to_csv(
            file_dict[key]['feature_file'],
            index=False,
            header=False
        )


def eval_result(outdir: str, y, y_pred, name: str) -> None:
    y_pred = np.argmax(y_pred, axis=1)
    # print("{}, {}".format(len(y), len(y_pred)))
    recall = recall_score(y, y_pred)
    precision = precision_score(y, y_pred)
    accuracy = accuracy_score(y, y_pred)

    with open(os.path.join(outdir, "evalResult_{}.txt".format(name)), 'w+') as ofile:
        output_str = f"Model Name: {name}\n"
        output_str = output_str + f"Accuracy: {accuracy}\n"
        output_str = output_str + f"Recall: {recall}\n"
        output_str = output_str + f"Precision: {precision}\n"
        output_str = output_str + f"Predict Positive Samples Number: {(y_pred == 1).sum()}\n"
        output_str = output_str + f"TP number: {(y == 1).sum()}\n"
        output_str = output_str + f"TN number: {(y == 0).sum()}\n"
        ofile.write(output_str)


# ---------------------- main ---------------------- #

parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, help="Input predict config file.")
args = parser.parse_args()

## Build figure(s)
roc_fig, roc_ax = plt.subplots(figsize=(10, 10))
roc_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)
pr_fig, pr_ax = plt.subplots(figsize=(10, 10))
pr_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)

## Read JSON-config
jsonFile = open(args.json, 'r')
jsonData = json.load(jsonFile)

datasetDir = jsonData['dataset_dir']
outdir = jsonData['out_dir']
tfp_tfn = jsonData['tfp_tfn']
if os.path.isdir(outdir) is not True:
    os.makedirs(outdir)

for data in jsonData['data_list']:
    ## Load Data
    vg4seq = join_path(datasetDir, data['vg4seq'])
    ug4seq = join_path(datasetDir, data['ug4seq'])
    vg4atac = join_path(datasetDir, data['vg4atac'])
    ug4atac = join_path(datasetDir, data['ug4atac'])
    vg4bs = join_path(datasetDir, data['vg4bs'])
    ug4bs = join_path(datasetDir, data['ug4bs'])
    norm = data["normalization"]

    g4Dataset = g4SeqEnv(
        vg4seq, ug4seq,
        vg4atac, ug4atac,
        vg4bs, ug4bs,
        norm
    )
    testData = g4Dataset.Features
    testLabels = g4Dataset.Labels

    checkpoint = data['checkpoint']
    name = data['name']
    clf = joblib.load(checkpoint)
    y_pred = clf.predict_proba(testData.to_numpy())
    eval_result(outdir, testLabels, y_pred, name)
    plot_pr(pr_ax, testLabels, y_pred, name)
    plot_roc(roc_ax, testLabels, y_pred, name)

    if tfp_tfn:
        tfp_tfn_outdir = join_path(outdir, f"{name}_tfp_tfn")
        try:
            os.makedirs(tfp_tfn_outdir)
            print(f"TRUE NAME: {name}")
        except FileExistsError:
            print(f"NAME: {name}")
            exit(-1)
        get_tfp_tfn(tfp_tfn_outdir, g4Dataset.Features, testLabels, y_pred, name)

    del g4Dataset, testData, testLabels
roc_fig.savefig(os.path.join(outdir, "roc.png"))
pr_fig.savefig(os.path.join(outdir, "pr.png"))
