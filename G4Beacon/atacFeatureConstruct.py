#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import random
import argparse
from .commonUtils import runShellCmd


def matrixToCsv(imatFile: str, ocsvFile: str) -> None:
    r'''
        Convert deeptools-output matrix file to CSV format.
    '''
    with open(imatFile, 'r') as ifile:
        with open(ocsvFile, 'w+') as ofile:
            for i in range(3):
                # Ignore the header lines
                ifile.readline()

            for line in ifile.readlines():
                line = line.replace("nan", "0.0")
                line = line.replace("\t", ",")
                ofile.write(line)


def computeMatrix(config):

    g4bed = config['g4bed']
    envbw = config['envbw']
    thread = config['thread']
    extend = config['extend']
    binsize = config['binsize']
    outcsv = config['outcsv']

    rand_id = random.randint(0, 9280)
    tmp_file_plot = f"{rand_id}_forplot"
    tmp_file_mat = f"{rand_id}_matrix"

    runShellCmd((
        "computeMatrix reference-point "
        "--referencePoint \"center\" "
        f"-R {g4bed} -S {envbw} -p {thread} "
        f"-a {extend} -b {extend} -bs {binsize} "
        f"--outFileName  {tmp_file_plot} "
        f"--outFileNameMatrix {tmp_file_mat}"
    ))

    matrixToCsv(tmp_file_mat, outcsv)
    runShellCmd(f"rm {tmp_file_plot} {tmp_file_mat}")


def atacFeatureConstruct_main(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', type=int, default=1, help="thread-nums.")
    parser.add_argument('--g4Input', type=str, help="g4seq file (origin-BED) input.")
    parser.add_argument('--atacInput', type=str, help="atac file (bigwig) input.")
    parser.add_argument('--csvOutput', type=str, help="Ouput env-feature csv path.")
    args = parser.parse_args(args)
    # Config dict
    config = {
        "g4bed": args.g4Input,
        "envbw": args.envInput,
        "outcsv": args.csvOutput,
        "thread": args.p,
        "extend": 1000,
        "binsize": 10
    }

    computeMatrix(config)
