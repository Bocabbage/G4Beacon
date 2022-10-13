#! usr/bin python
# -*- coding: utf-8 -*-
# Description: compute Matrix and convert it into CSV format
# Author: Zhuofan Zhang
# Update date: 2021/07/26
import random
import argparse
from commonUtils import run_shell_cmd, running_log


def compute_Matrix() -> None:
    r'''
        Self-definition matrix-compute method.
        (unfinished)
    '''
    pass


def matrix_to_csv(imatFile: str, ocsvFile: str) -> None:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--g4BED', type=str, help="g4 bed-file path.")
    parser.add_argument('--atacBW', type=str, help="atac bw-file path.")
    parser.add_argument('--extend', type=int)
    parser.add_argument('--binSize', type=int)
    parser.add_argument('--outCSV', type=str, help="Output result csv file.")
    parser.add_argument('-p', type=int, default=10, help="Thread nums.")
    args = parser.parse_args()

    randId = random.randint(0, 9280)
    tmpFilePlot = "{}_forplot".format(randId)
    tmpFileMat = "{}_matrix".format(randId)
    run_shell_cmd(("computeMatrix reference-point "
                   "--referencePoint \"center\" "
                   "-R {g4BED} -S {atacBW} -p {p} "
                   "-a {extend} -b {extend} -bs {binSize} "
                   "--outFileName  {plotFile} "
                   "--outFileNameMatrix {matFile}").format(
                       g4BED=args.g4BED,
                       atacBW=args.atacBW,
                       extend=args.extend,
                       binSize=args.binSize,
                       p=args.p,
                       plotFile=tmpFilePlot,
                       matFile=tmpFileMat))

    matrix_to_csv(tmpFileMat, args.outCSV)
    run_shell_cmd("rm {} {}".format(tmpFilePlot, tmpFileMat))
