#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/09/28
# Author: Zhuofan Zhang
from numpy.core.defchararray import index
from pandas.io.parsers import read_csv
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import os
import json
import numpy as np
import pandas as pd
import argparse
import joblib
import matplotlib
import matplotlib.pyplot as plt
from dataset import g4SeqEnv
from sklearn.metrics import accuracy_score, recall_score, precision_score, auc, roc_curve
from sklearn.metrics import precision_recall_curve, average_precision_score, PrecisionRecallDisplay, RocCurveDisplay
matplotlib.use('Agg')


def join_path(firstpath, secondpath):
    try:
        path = os.path.join(firstpath, secondpath)
    except TypeError:
        path = None
    return path


def plot_roc(ax, y, y_pred, name):
    y_pred = y_pred[:, 1]
    fpr, tpr, _ = roc_curve(y, y_pred)
    roc_auc = auc(fpr, tpr)
    viz = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name=name)
    viz.plot(ax=ax, name=name)

    ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05], title="ROC Curve")
    ax.legend(loc="lower right")


def plot_pr(ax, y, y_pred, name):
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


def get_fp_fn(outdir, features, y, y_pred, name):
    fpFile = open(os.path.join(outdir, "fp_{}.csv".format(name)), 'w+')
    fnFile = open(os.path.join(outdir, "fn_{}.csv".format(name)), 'w+')

    fpProbaFile = open(os.path.join(outdir, "fpProba_{}.csv".format(name)), 'w+')
    fnProbaFile = open(os.path.join(outdir, "fnProba_{}.csv".format(name)), 'w+')

    fpIdx = []
    fnIdx = []

    y_p = np.argmax(y_pred, axis=1)
    for idx in range(len(y_p)):
        if y[idx] == 0 and y_p[idx] == 1:
            # fp
            fpIdx.append(idx)
            fpProbaFile.write("idx{}: {}\n".format(idx, y_pred[idx]))
        elif y[idx] == 1 and y_p[idx] == 0:
            # fn
            fnIdx.append(idx)
            fnProbaFile.write("idx{}: {}\n".format(idx, y_pred[idx]))

    features.iloc[fpIdx, :].to_csv(fpFile, index=False, header=False)
    features.iloc[fnIdx, :].to_csv(fnFile, index=False, header=False)


def eval_result(outdir, y, y_pred, name):
    y_pred = np.argmax(y_pred, axis=1)
    print("{}, {}".format(len(y), len(y_pred)))
    recall = recall_score(y, y_pred)
    precision = precision_score(y, y_pred)
    accuracy = accuracy_score(y, y_pred)

    with open(os.path.join(outdir, "evalResult_{}.txt".format(name)), 'w+') as ofile:
        ofile.write("Model Name: {}\n".format(name))
        ofile.write("Accuracy: {}\n".format(accuracy))
        ofile.write("Recall: {}\n".format(recall))
        ofile.write("Precision: {}\n".format(precision))
        ofile.write("Predict Positive Samples Number: {}\n".format((y_pred == 1).sum()))
        ofile.write("True Positive Samples Number: {}\n".format((y == 1).sum()))
        ofile.write("True Negative Samples Number: {}\n".format((y == 0).sum()))


parser = argparse.ArgumentParser()
# parser.add_argument('--vg4seq', type=str, default=None, help="Positive test-set seq data.")
# parser.add_argument('--ug4seq', type=str, default=None, help="Negative test-set seq data.")
# parser.add_argument('--vg4atac', type=str, default=None, help="Positive test-set env data.")
# parser.add_argument('--ug4atac', type=str, default=None, help="Negative test-set env data.")
# parser.add_argument('--vg4bs', type=str, default=None, help="Positive test-set env data.")
# parser.add_argument('--ug4bs', type=str, default=None, help="Negative test-set env data.")
parser.add_argument('--json', type=str, help="Input predict config file.")
parser.add_argument('--extend', type=int, default=None,
                    help="Seq extend parameter: select [mid-extend, mid+extend] from seq-features.")
# parser.add_argument('--model', type=str, default="lightGBM", help="Xgboost/lightGBM.")
# parser.add_argument('--checkpoint', type=str, help="Model checkpoint PATH.")
# parser.add_argument('--outdir', type=str, default='./', help="Eval result output directory.")

args = parser.parse_args()

roc_fig, roc_ax = plt.subplots(figsize=(10, 10))
roc_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)

pr_fig, pr_ax = plt.subplots(figsize=(10, 10))
pr_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)

jsonFile = open(args.json, 'r')
jsonData = json.load(jsonFile)

datasetDir = jsonData['dataset_dir']
outdir = jsonData['out_dir']

if os.path.isdir(outdir) is not True:
    os.makedirs(outdir)

for data in jsonData['data_list']:
    vg4seq = join_path(datasetDir, data['vg4seq'])
    ug4seq = join_path(datasetDir, data['ug4seq'])
    vg4atac = join_path(datasetDir, data['vg4atac'])
    ug4atac = join_path(datasetDir, data['ug4atac'])
    vg4bs = join_path(datasetDir, data['vg4bs'])
    ug4bs = join_path(datasetDir, data['ug4bs'])
    g4Dataset = g4SeqEnv(
        vg4seq, ug4seq,
        vg4atac, ug4atac,
        vg4bs, ug4bs,
        args.extend
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

    del g4Dataset, testData, testLabels
roc_fig.savefig(os.path.join(outdir, "roc.png"))
pr_fig.savefig(os.path.join(outdir, "pr.png"))
