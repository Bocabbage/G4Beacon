#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import joblib
import argparse
from dataset import g4SeqEnv


def predict(config):
    vg4seq = config['vg4seq']
    ug4seq = config['ug4seq']
    vg4atac = config['vg4atac']
    ug4atac = config['ug4atac']
    vg4bs = config['vg4bs']
    ug4bs = config['ug4bs']
    vg4atacFd = config['vg4atac-fd']
    ug4atacFd = config['ug4atac-fd']
    norm = config["normalization"]
    #### New option
    originBed = config['origin-bed']
    resultFile = config['result-file']

    g4Dataset = g4SeqEnv(
        vg4seq, ug4seq,
        vg4atac, ug4atac,
        vg4atacFd, ug4atacFd,
        vg4bs, ug4bs,
        norm
    )
    testData = g4Dataset.Features

    checkpoint = config['checkpoint']
    clf = joblib.load(checkpoint)
    y_pred = clf.predict_proba(testData.to_numpy())

    y_pred_proba = y_pred
    assert(len(y_pred) == len(testData))
    with open(originBed, 'r') as rfile:
        with open(resultFile, 'w+') as wfile:
            for idx, line in enumerate(rfile.readlines()):
                line = f"{line.strip()}\t{y_pred_proba[idx][1]:.5f}\n"
                wfile.write(line)


def getActiveG4s_main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--seqCSV', type=str, help="Seq feature file path (CSV).")
    parser.add_argument('--atacCSV', type=str, help="Atac feature file path (CSV).")
    parser.add_argument('--originBED', type=str, help="origin-bed file generated from the pre-process step.")
    parser.add_argument('--model', type=str, help="Trained G4Catcher model file (checkpoint, JOBLIB).")
    parser.add_argument('-o', type=str, help="result output path (BED).")
    parser.add_argument('--norm', action="store_true", default=False, help="Apply normalization on ATAC-features.")

    args = parser.parse_args(args)

    config = {
        "vg4seq": args.seqCSV,
        "ug4seq": None,
        "vg4atac": args.atacCSV,
        "ug4atac": None,
        "vg4atac-fd": None,
        "ug4atac-fd": None,
        "vg4bs": None,
        "ug4bs": None,
        "origin-bed": args.originBED,
        "result-file": args.o,
        "checkpoint": args.model,
        "model": "lightGBM",
        "normalization": args.norm
    }

    predict(config)
