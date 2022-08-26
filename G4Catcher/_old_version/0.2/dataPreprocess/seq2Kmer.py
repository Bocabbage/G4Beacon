#! usr/bin python
# -*- coding: utf-8 -*-
# Description: take sequence file(one-hot, CSV format) as input
#              and convert it into K-mer file.
# Author: Zhuofan Zhang
# Update date: 2021/08/24
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help="Input sequence CSV file.")
parser.add_argument('-o', type=str, help="Ouput K-mer CSV file.")
parser.add_argument('-k', type=int, default=3, help="the k of k-mer. default=3.")
args = parser.parse_args()


with open(args.i, 'r') as ifile:
    with open(args.o, 'w+') as ofile:
        for rline in ifile.readlines():
            baseList = rline.strip().split(',')
            result = []
            rangeEnd = len(baseList) - len(baseList) % args.k
            for idx in range(0, rangeEnd, args.k):
                result.append(str(int(''.join(baseList[idx:idx + args.k]), 4)))
            result = ','.join(result)
            result += '\n'
            ofile.write(result)
