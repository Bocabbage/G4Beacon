#! usr/bin python
# -*- coding: utf-8 -*-
# Description: divide feature files to train/test set
# Author: Zhuofan Zhang
# Update date: 2021/08/04
import os
import random
import subprocess
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-pSeq', type=str, help="positive sample sequence file.")
parser.add_argument('-pEnv', type=str, help="positive sample environment file.")
parser.add_argument('-nSeq', type=str, help="negative sample sequence file.")
parser.add_argument('-nEnv', type=str, help="negative sample environment file.")
parser.add_argument('--seed', type=int, default=42, help="random sampling seed.")
parser.add_argument('--outdir', type=str, default='./', help="output file dir.")
parser.add_argument('--undersampling', action="store_true", default=False, dest="undersampling")
parser.add_argument('--oversampling', action="store_true", default=False, dest="oversampling")
args = parser.parse_args()

random.seed(args.seed)

# Get sample nums
posNums = int(subprocess.check_output(["wc", "-l", args.pEnv]).decode('utf-8').split(" ")[0])
negNums = int(subprocess.check_output(["wc", "-l", args.nEnv]).decode('utf-8').split(" ")[0])

# Positive Samples
spData = pd.read_csv(args.pSeq, dtype='a', header=None)
epData = pd.read_csv(args.pEnv, dtype='a', header=None)
shuffleList = random.sample([x for x in range(posNums)], k=posNums)
trainIdx = shuffleList[:(posNums // 2)]
testIdx = shuffleList[(posNums // 2):]

suffix = "under"
if args.oversampling:
    # Oversampling
    trainIdx = random.choices(trainIdx, k=(negNums // 2))
    suffix = "over"

# Set the result name
trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

trainSamplingPosSeq = spData.iloc[trainIdx]
trainSamplingPosEnv = epData.iloc[trainIdx]
trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
trainSamplingPosEnv.to_csv(trainPosPrefix + ".env.csv", header=False, index=False)

testSamplingPosSeq = spData.iloc[testIdx]
testSamplingPosEnv = epData.iloc[testIdx]
testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
testSamplingPosEnv.to_csv(testPosPrefix + ".env.csv", header=False, index=False)
del spData, epData

# Negative Samples
snData = pd.read_csv(args.nSeq, dtype='a', header=None)
enData = pd.read_csv(args.nEnv, dtype='a', header=None)
shuffleList = random.sample([x for x in range(negNums)], k=negNums)
trainIdx = shuffleList[:(negNums // 2)]
testIdx = shuffleList[(negNums // 2):]

if args.undersampling:
    # Undersampling
    trainIdx = random.sample(trainIdx, k=(posNums // 2))

trainSamplingNegSeq = snData.iloc[trainIdx]
trainSamplingNegEnv = enData.iloc[trainIdx]
trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
trainSamplingNegEnv.to_csv(trainNegPrefix + ".env.csv", header=False, index=False)

testSamplingNegSeq = snData.iloc[testIdx]
testSamplingNegEnv = enData.iloc[testIdx]
testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
testSamplingNegEnv.to_csv(testNegPrefix + ".env.csv", header=False, index=False)
