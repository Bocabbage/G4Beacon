#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/08/29
# Author: Zhuofan Zhang
from numpy.core.defchararray import index
from pandas.io.parsers import read_csv
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import os
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
parser.add_argument('--vg4seq', type=str, default=None, help="Positive test-set seq data.")
parser.add_argument('--ug4seq', type=str, default=None, help="Negative test-set seq data.")
parser.add_argument('--vg4atac', type=str, default=None, help="Positive test-set env data.")
parser.add_argument('--ug4atac', type=str, default=None, help="Negative test-set env data.")
parser.add_argument('--vg4bs', type=str, default=None, help="Positive test-set env data.")
parser.add_argument('--ug4bs', type=str, default=None, help="Negative test-set env data.")
parser.add_argument('--extend', type=int, default=None,
                    help="Seq extend parameter: select [mid-extend, mid+extend] from seq-features.")
parser.add_argument('--model', type=str, default="lightGBM", help="Xgboost/lightGBM.")
parser.add_argument('--checkpoint', type=str, help="Model checkpoint PATH.")
parser.add_argument('--outdir', type=str, default='./', help="Eval result output directory.")

args = parser.parse_args()

if os.path.isdir(args.outdir) is not True:
    os.makedirs(args.outdir)


if args.model == 'Xgboost':
    clf = XGBClassifier()
else:
    clf = LGBMClassifier()

roc_fig, roc_ax = plt.subplots(figsize=(10, 10))
roc_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)

pr_fig, pr_ax = plt.subplots(figsize=(10, 10))
pr_ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=0.8)

if os.path.isdir(args.checkpoint):
    fileList = sorted(os.listdir(args.checkpoint), key=lambda x: len(x))
    for file in fileList:
        # Load data
        name = file.split('_')[0]
        if "seq" in name:
            # For K-mer
            kmer = name.split('-')[0]
            if kmer is name:
                # No K-mer prefix
                vg4seq = args.vg4seq
                ug4seq = args.ug4seq
            else:
                vg4seqName = os.path.splitext(args.vg4seq)[0]
                ug4seqName = os.path.splitext(args.ug4seq)[0]
                vg4seq = "{}{}f.csv".format(vg4seqName, kmer)
                ug4seq = "{}{}f.csv".format(ug4seqName, kmer)
        else:
            vg4seq = None
            ug4seq = None

        if "atac" in name:
            vg4atac = args.vg4atac
            ug4atac = args.ug4atac
        else:
            vg4atac = None
            ug4atac = None

        if "bs" in name:
            vg4bs = args.vg4bs
            ug4bs = args.ug4bs
        else:
            vg4bs = None
            ug4bs = None

        g4Dataset = g4SeqEnv(
            vg4seq, ug4seq,
            vg4atac, ug4atac,
            vg4bs, ug4bs,
            args.extend
        )
        testData = g4Dataset.Features
        testLabels = g4Dataset.Labels

        checkpoint = os.path.join(args.checkpoint, file)
        clf = joblib.load(checkpoint)
        y_pred = clf.predict_proba(testData.to_numpy())
        eval_result(args.outdir, testLabels, y_pred, name)
        plot_pr(pr_ax, testLabels, y_pred, name)
        plot_roc(roc_ax, testLabels, y_pred, name)

        del g4Dataset, testData, testLabels
    roc_fig.savefig(os.path.join(args.outdir, "roc.png"))
    pr_fig.savefig(os.path.join(args.outdir, "pr.png"))
else:
    g4Dataset = g4SeqEnv(
        args.vg4seq, args.ug4seq,
        args.vg4atac, args.ug4atac,
        args.vg4bs, args.ug4bs,
        args.extend)
    # testData = pd.concat([g4Dataset.seqFeatures, g4Dataset.envFeatures], axis=1)
    testData = g4Dataset.Features
    testLabels = g4Dataset.Labels

    clf = joblib.load(args.checkpoint)
    y_pred = clf.predict_proba(testData.to_numpy())
    name = clf.__class__.__name__
    get_fp_fn(args.outdir, testData, testLabels, y_pred, name)
    eval_result(args.outdir, testLabels, y_pred, name)
    plot_pr(pr_ax, testLabels, y_pred, name)
    plot_roc(roc_ax, testLabels, y_pred, name)
    roc_fig.savefig(os.path.join(args.outdir, "roc.png"))
    pr_fig.savefig(os.path.join(args.outdir, "pr.png"))
