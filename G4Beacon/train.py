#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/05/09
import os
import random
import argparse
from .commonUtils import runShellCmd
from .seqFeatureConstruct import seqFeatureConstruct_main
from .atacFeatureConstruct import atacFeatureConstruct_main
from .trainingsetConstruct import trainingsetConstruct_main
from .trainOwnData import trainOwnData_main


def train_main(args):
    parser = argparse.ArgumentParser()
    # Essential params
    parser.add_argument('--atac', type=str, default=None, help=r"cellular-specific ATAC-seq data(hg19-ref).")
    parser.add_argument('--vg4', type=str, default=None, help=r"")
    parser.add_argument('-fi', type=str, default=None, help=r"reference-genome fasta file dir(hg19).")
    parser.add_argument('--model', type=str, default=None, help=r"output trained-model dir.")

    # Optional configuration params
    randId = random.randint(0, 40000000)
    parser.add_argument('--workdir', type=str, default=os.path.join(os.path.expanduser('~'), f"{randId}-g4beacon"), help=r"tmp-file dir (default: $HOME).")
    parser.add_argument('-p', type=int, default=1, help=r"process-num for using multi-process to accelerate the progress (default: 1).")
    parser.add_argument('--seed', type=int, default=42, help=r"random-seed setting. (default: 42)")

    args = parser.parse_args(args)

    if not os.path.isdir(args.workdir):
        os.makedirs(args.workdir)

    # Pos/neg sample division
    print("----- pos/neg sample division START -----")
    origin_minus_bed = os.path.join(os.path.dirname(__file__), "data/", "GSM3003539_minus.g4seqFirst.F0.1.ex1000.origin.bed")
    origin_plus_bed = os.path.join(os.path.dirname(__file__), "data/", "GSM3003539_plus.g4seqFirst.F0.1.ex1000.origin.bed")
    runShellCmd(
        (f"bedtools intersect -a {origin_minus_bed} -b {args.vg4}"
         "-wa -F 0.1 | sort -k1,1 -k2,2n -u > "
         f"{os.path.join(args.workdir, 'minus.g4seqFirst.F0.1.bed')}"))
    runShellCmd(
        (f"bedtools intersect -a {origin_minus_bed} -b {args.vg4}"
         "-v -F 0.1 | sort -k1,1 -k2,2n -u > "
         f"{os.path.join(args.workdir, 'minus_v.g4seqFirst.F0.1.bed')}"))
    runShellCmd(
        (f"bedtools intersect -a {origin_plus_bed} -b {args.vg4}"
         "-wa -F 0.1 | sort -k1,1 -k2,2n -u > "
         f"{os.path.join(args.workdir, 'plus.g4seqFirst.F0.1.bed')}"))
    runShellCmd(
        (f"bedtools intersect -a {origin_plus_bed} -b {args.vg4}"
         "-v -F 0.1 | sort -k1,1 -k2,2n -u > "
         f"{os.path.join(args.workdir, 'plus_v.g4seqFirst.F0.1.bed')}"))
    print("----- pos/neg sample division FINISH -----")

    # Sequence feature construction
    print("----- sequece feature construction START -----")
    seq_feature_configs = [
        [
            "-i", os.path.join(args.workdir, "minus.g4seqFirst.F0.1.bed"),
            "-oseq", os.path.join(args.workdir, "minus.g4seqFirst.F0.1.seq.csv"),
            "-obi", os.path.join(args.workdir, "minus.g4seqFirst.F0.1.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
        ],
        [
            "-i", os.path.join(args.workdir, "minus_v.g4seqFirst.F0.1.bed"),
            "-oseq", os.path.join(args.workdir, "minus_v.g4seqFirst.F0.1.seq.csv"),
            "-obi", os.path.join(args.workdir, "minus_v.g4seqFirst.F0.1.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
        ],
        [
            "-i", os.path.join(args.workdir, "plus.g4seqFirst.F0.1.bed"),
            "-oseq", os.path.join(args.workdir, "plus.g4seqFirst.F0.1.seq.csv"),
            "-obi", os.path.join(args.workdir, "plus.g4seqFirst.F0.1.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
            "--reverse",
        ],
        [
            "-i", os.path.join(args.workdir, "plus_v.g4seqFirst.F0.1.bed"),
            "-oseq", os.path.join(args.workdir, "plus_v.g4seqFirst.F0.1.seq.csv"),
            "-obi", os.path.join(args.workdir, "plus_v.g4seqFirst.F0.1.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
            "--reverse",
        ],
    ]
    for config in seq_feature_configs:
        seqFeatureConstruct_main(config)

    runShellCmd(
        (f"cat {os.path.join(args.workdir, 'minus.g4seqFirst.F0.1.seq.csv')} "
         f"{os.path.join(args.workdir, 'plus.g4seqFirst.F0.1.seq.csv')} > "
         f"{os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.seq.csv')}"))

    runShellCmd(
        (f"cat {os.path.join(args.workdir, 'minus_v.g4seqFirst.F0.1.seq.csv')} "
         f"{os.path.join(args.workdir, 'plus_v.g4seqFirst.F0.1.seq.csv')} > "
         f"{os.path.join(args.workdir, 'CATmp_v.g4seqFirst.F0.1.seq.csv')}"))
    print("----- sequece feature construction FINISH -----")

    # Atac-seq feature construction
    print("----- atac-seq feature construction START -----")
    atac_feature_configs = [
        [
            "-p", f"{args.p}",
            "--g4Input", os.path.join(args.workdir, 'minus.g4seqFirst.F0.1.bed'),
            "--atacInput", args.atac,
            "--csvOutput", os.path.join(args.workdir, "minus.g4seqFirst.F0.1.atac.csv"),
        ],
        [
            "-p", f"{args.p}",
            "--g4Input", os.path.join(args.workdir, 'minus_v.g4seqFirst.F0.1.bed'),
            "--atacInput", args.atac,
            "--csvOutput", os.path.join(args.workdir, "minus_v.g4seqFirst.F0.1.atac.csv"),
        ],
        [
            "-p", f"{args.p}",
            "--g4Input", os.path.join(args.workdir, 'plus.g4seqFirst.F0.1.bed'),
            "--atacInput", args.atac,
            "--csvOutput", os.path.join(args.workdir, "plus.g4seqFirst.F0.1.atac.csv"),
        ],
        [
            "-p", f"{args.p}",
            "--g4Input", os.path.join(args.workdir, 'plus_v.g4seqFirst.F0.1.bed'),
            "--atacInput", args.atac,
            "--csvOutput", os.path.join(args.workdir, "plus_v.g4seqFirst.F0.1.atac.csv"),
        ],
    ]
    for config in atac_feature_configs:
        atacFeatureConstruct_main(config)

    runShellCmd(
        (f"cat {os.path.join(args.workdir, 'minus.g4seqFirst.F0.1.atac.csv')} "
         f"{os.path.join(args.workdir, 'plus.g4seqFirst.F0.1.atac.csv')} > "
         f"{os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.atac.csv')}"))

    runShellCmd(
        (f"cat {os.path.join(args.workdir, 'minus_v.g4seqFirst.F0.1.atac.csv')} "
         f"{os.path.join(args.workdir, 'plus_v.g4seqFirst.F0.1.atac.csv')} > "
         f"{os.path.join(args.workdir, 'CATmp_v.g4seqFirst.F0.1.atac.csv')}"))
    print("----- atac-seq feature construction FINISH -----")

    # Training-set construction
    print("----- training-set construction START -----")
    trainingset_dir = os.path.join(args.workdir, f"trainingset/")
    os.makedirs(trainingset_dir)
    trainingset_construct_config = [
        "--vg4seqCSV", os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.seq.csv'),
        "--ug4seqCSV", os.path.join(args.workdir, 'CATmp_v.g4seqFirst.F0.1.seq.csv'),
        "--vg4atacCSV", os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.atac.csv'),
        "--ug4atacCSV", os.path.join(args.workdir, 'CATmp_v.g4seqFirst.F0.1.atac.csv'),
        "--outdir", trainingset_dir,
        "--seed", args.seed,
    ]
    trainingsetConstruct_main(trainingset_construct_config)
    print("----- training-set construction FINISH -----")

    # Model training
    print("----- training START -----")
    train_config = [
        "--vg4seqCSV", os.path.join(trainingset_dir, "trainPos.seq.full.csv"),
        "--ug4seqCSV", os.path.join(trainingset_dir, "trainNeg.seq.full.csv"),
        "--vg4atacCSV", os.path.join(trainingset_dir, "trainPos.atac.full.csv"),
        "--ug4atacCSV", os.path.join(trainingset_dir, "trainNeg.atac.full.csv"),
        "--outdir", os.path.dirname(args.model),
        "--oname", os.path.basename(args.model),
    ]
    trainOwnData_main(train_config)
    print("----- training FINISH -----")
