#! usr/bin python
# -*- coding: utf-8 -*-
# Description: take K-mer file(one-hot, CSV format) as input
#              and convert it into K-mer FREQUENCY file.
# Author: Zhuofan Zhang
# Update date: 2021/09/06
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help="Input K-mer CSV file.")
parser.add_argument('-o', type=str, help="Ouput K-mer FREQUENCY CSV file.")
parser.add_argument('-k', type=int, default=3, help="the k of k-mer. default=3.")
args = parser.parse_args()


with open(args.i, 'r') as ifile:
    with open(args.o, 'w+') as ofile:
        for rline in ifile.readlines():
            result = [0 for _ in range(4**(args.k))]
            feature = [int(x) for x in rline.strip().split(',')]
            for x in feature:
                result[x] += 1
            # featureLen = len(feature)
            result = [str(x) for x in result]
            result = ",".join(result) + "\n"
            ofile.write(result)
