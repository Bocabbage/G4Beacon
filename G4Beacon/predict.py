#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/05/09
import random
import os
import argparse
from .seqFeatureConstruct import seqFeatureConstruct_main
from .atacFeatureConstruct import atacFeatureConstruct_main
from .getActiveG4s import getActiveG4s_main
from .commonUtils import runShellCmd, isWritable


def predict_main(args):
    parser = argparse.ArgumentParser()
    # Essential params
    parser.add_argument('--atac', type=str, default=None, help=r"cellular-specific ATAC-seq data(hg19-ref).")
    parser.add_argument('-o', type=str, default=None, help=r"output file path (BEDGRAPH file)")
    parser.add_argument('-fi', type=str, default=None, help=r"reference-genome fasta file dir(hg19).")
    parser.add_argument('--model', type=str, default=os.path.join(
        os.path.dirname(__file__),
        "models/",
        "seq+atac_over_lightGBM_nofilt_lightGBM.checkpoint.joblib"
    ), help=r"trained-model dir.")

    # Optional configuration params
    randId = random.randint(0, 40000000)
    parser.add_argument('--workdir', type=str, default=os.path.join(os.path.expanduser('~'), f"{randId}-g4beacon"), help=r"tmp-file dir (default: $HOME).")
    parser.add_argument('-p', type=int, default=1, help=r"process-num for using multi-process to accelerate the progress (default: 1).")
    parser.add_argument('--store_cache', action="store_true", default=False, help=r"store the generated seq-feature csv files as cache or not. (default: false)")

    # Optional origin data
    parser.add_argument('--minusOrigin', type=str, default=None)
    parser.add_argument('--plusOrigin', type=str, default=None)
    parser.add_argument('--catmpOrigin', type=str, default=None)

    args = parser.parse_args(args)

    if args.minusOrigin is None:
        origin_minus_bed = os.path.join(os.path.dirname(__file__), "data/", "GSM3003539_minus.g4seqFirst.F0.1.ex1000.origin.bed")
    else:
        origin_minus_bed = args.minusOrigin

    if args.plusOrigin is None:
        origin_plus_bed = os.path.join(os.path.dirname(__file__), "data/", "GSM3003539_plus.g4seqFirst.F0.1.ex1000.origin.bed")
    else:
        origin_plus_bed = args.plusOrigin

    if args.catmpOrigin is None:
        origin_catmp_bed = os.path.join(os.path.dirname(__file__), "data/", "GSM3003539_CATmp.g4seqFirst.F0.1.ex1000.origin.bed")
    else:
        origin_catmp_bed = args.catmpOrigin

    if not os.path.isdir(args.workdir):
        os.makedirs(args.workdir)

    # Construct the configuration-list for the prediction-progress
    configs = {
        "minus_seq_feature_construct": [
            "-i", origin_minus_bed,
            "-oseq", os.path.join(args.workdir, "minus.g4seqFirst.F0.1.ex1000.seq.csv"),
            "-obi", os.path.join(args.workdir, "tmp.minus.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
        ],
        "plus_seq_feature_construct": [
            "-i", origin_plus_bed,
            "-oseq", os.path.join(args.workdir, "plus.g4seqFirst.F0.1.ex1000.seq.csv"),
            "-obi", os.path.join(args.workdir, "tmp.plus.origin.bed"),  # Should not be different from the -i file
            "-fi", args.fi,
            "--reverse",
        ],
        "atac_feature_construct": [
            "-p", f"{args.p}",
            "--g4Input", origin_catmp_bed,
            "--atacInput", args.atac,
            "--csvOutput", os.path.join(args.workdir, "CATmp.g4seqFirst.F0.1.ex1000.atac.csv"),
        ],
        "get_activeg4s": [
            "--seqCSV", os.path.join(args.workdir, "CATmp.g4seqFirst.F0.1.ex1000.seq.csv"),
            "--atacCSV", os.path.join(args.workdir, "CATmp.g4seqFirst.F0.1.ex1000.atac.csv"),
            "--originBED", origin_catmp_bed,
            "--model", args.model,
            "-o", args.o,
        ],
    }

    seq_feature_cache = args.catmpOrigin is None and os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            "data/",
            "GSM3003539_CATmp.g4seqFirst.F0.1.ex1000.seq.csv")
    )

    print("----- sequece feature construction START -----")
    if not seq_feature_cache:
        seqFeatureConstruct_main(configs["minus_seq_feature_construct"])
        seqFeatureConstruct_main(configs["plus_seq_feature_construct"])
        runShellCmd(
            (f"cat {os.path.join(args.workdir, 'tmp.minus.origin.bed')} "
             f"{os.path.join(args.workdir, 'tmp.plus.origin.bed')} > "
             f"{os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.ex1000.seq.csv')}")
        )
    else:
        # Build tmp soft-link
        runShellCmd(
            (f"ln -s {os.path.join(os.path.dirname(__file__), 'data/', 'GSM3003539_CATmp.g4seqFirst.F0.1.ex1000.seq.csv')} "
             f"{os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.ex1000.seq.csv')}")
        )
        print("Use cache...")
    print("----- sequece feature construction FINISH -----")

    print("----- atac-seq feature construction START -----")
    atacFeatureConstruct_main(configs["atac_feature_construct"])
    print("----- atac-seq feature construction FINISH -----")
    print("----- predict START -----")
    getActiveG4s_main(configs["get_activeg4s"])
    print("----- predict FINISH -----")

    if not seq_feature_cache and args.store_cache and args.catmpOrigin is None:
        if isWritable(os.path.join(os.path.dirname(__file__), 'data/')):
            runShellCmd(
                (f"mv {os.path.join(args.workdir, 'CATmp.g4seqFirst.F0.1.ex1000.seq.csv')} "
                 f"{os.path.join(os.path.dirname(__file__), 'data/', 'GSM3003539_CATmp.g4seqFirst.F0.1.ex1000.seq.csv')}")
            )
        else:
            print("store cache failed: the data/ dir is not writable.")

    runShellCmd(f"rm -rf {args.workdir}")
