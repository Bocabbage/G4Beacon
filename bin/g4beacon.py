#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import sys
from G4Beacon import seqFeatureConstruct_main, atacFeatureConstruct_main, getActiveG4s_main, trainingsetConstruct_main, trainOwnData_main


def main(args):
    description = """
        [g4beacon] is an in vivo G4 prediction tool taking seq+atac feature inputs.
        This software can be used to construct the feature, train on your own data or
        predict in vivo G4s. We provide the following sub-tools:
        - seqFeatureConstruct   [Takes BED-format file as input to construct sequence-feature]
        - atacFeatureConstruct  [Takes BigWig file as input to construct atac-feature]
        - getActiveG4s          [Predicts in vivo G4s]
        - trainingsetConstruct  [Takes your constructed-feature data and create a balanced training-set]
        - trainOwnData          [Trains GBDT model with your own data]
        Usage: g4beacon atacFeatureConstruct -h
        More information: https://github.com/Bocabbage/G4Beacon
    """
    if len(args) == 1 and args[0] == "--help" or args[0] == "-h":
        print(description)
    elif args[0] == 'seqFeatureConstruct':
        seqFeatureConstruct_main(args)
    elif args[0] == 'atacFeatureConstruct':
        atacFeatureConstruct_main(args)
    elif args[0] == 'getActiveG4s':
        getActiveG4s_main(args)
    elif args[0] == 'trainingsetConstruct':
        trainingsetConstruct_main(args)
    elif args[0] == 'trainOwnData':
        trainOwnData_main(args)
    else:
        print(f"Error: No such sub-tool called: {args[0]}")


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        args = args.append("--help")
    args = sys.argv[1:]
    main(args)
