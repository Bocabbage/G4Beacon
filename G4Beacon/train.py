#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/05/08
import os
import random
import argparse


def train_main(args):
    parser = argparse.ArgumentParser()
    # Essential params
    parser.add_argument('--atac', type=str, default=None, help=r"cellular-specific ATAC-seq data(hg19-ref).")
    parser.add_argument('--vg4', type=str, default=None, help=r"")
    parser.add_argument('-fi', type=str, default=None, help=r"reference-genome fasta file dir(hg19).")
    parser.add_argument('--out-model', type=str, default=None, help=r"output trained-model dir.")

    # Optional configuration params
    randId = random.randint(0, 40000000)
    parser.add_argument('--workdir', type=str, default=os.path.join(os.path.expanduser('~'), f"{randId}-g4beacon"), help=r"tmp-file dir (default: $HOME).")
    parser.add_argument('-p', type=int, default=1, help=r"process-num for using multi-process to accelerate the progress (default: 1).")

    args = parser.parse_args(args)

    if not os.path.isdir(args.workdir):
        os.makedirs(args.workdir)
