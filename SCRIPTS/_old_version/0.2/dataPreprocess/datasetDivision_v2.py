#! usr/bin python
# -*- coding: utf-8 -*-
# Description: divide feature files to train/test set
# Author: Zhuofan Zhang
# Update date: 2021/08/15
import os
import random
import subprocess
import argparse
import pandas as pd
from imblearn.over_sampling import SMOTE

parser = argparse.ArgumentParser()
parser.add_argument('-pSeq', type=str, default=None, help="positive sample sequence file.")
parser.add_argument('-pATAC', type=str, help="positive sample environment file.")
parser.add_argument('-pBS', type=str, help="positive sample sequence file.")
parser.add_argument('-nSeq', type=str, default=None, help="negative sample sequence file.")
parser.add_argument('-nATAC', type=str, help="negative sample environment file.")
parser.add_argument('-nBS', type=str, help="negative sample environment file.")
parser.add_argument('--seed', type=int, default=42, help="random sampling seed.")
parser.add_argument('--outdir', type=str, default='./', help="output file dir.")
parser.add_argument('--undersampling', action="store_true", default=False, dest="undersampling")
parser.add_argument('--oversampling', action="store_true", default=False, dest="oversampling")
parser.add_argument('--smote', action="store_true", default=False, dest="smote", help="only for pSeq==nSeq==None.")
parser.add_argument('--mixsmote', action="store_true", default=False, dest="mixsmote", help="only for pSeq==nSeq==None.")
args = parser.parse_args()

random.seed(args.seed)

if os.path.isdir(args.outdir) is not True:
    os.makedirs(args.outdir)

# Get sample nums
posNums = int(subprocess.check_output(["wc", "-l", args.pATAC]).decode('utf-8').split(" ")[0])
negNums = int(subprocess.check_output(["wc", "-l", args.nATAC]).decode('utf-8').split(" ")[0])

if args.undersampling:
    if args.pSeq:
        spData = pd.read_csv(args.pSeq, dtype='a', header=None)
    else:
        spData = None
    epData = pd.read_csv(args.pATAC, dtype='a', header=None)
    mpData = pd.read_csv(args.pBS, dtype='a', header=None)

    shuffleList = random.sample([x for x in range(posNums)], k=posNums)
    trainIdx = shuffleList[:(posNums // 2)]
    testIdx = shuffleList[(posNums // 2):]
    suffix = "under"

    trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
    trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
    testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
    testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

    if spData is not None:
        trainSamplingPosSeq = spData.iloc[trainIdx]
        trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
    trainSamplingPosATAC = epData.iloc[trainIdx]
    trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
    trainSamplingPosBS = mpData.iloc[trainIdx]
    trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

    if spData is not None:
        testSamplingPosSeq = spData.iloc[testIdx]
        testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
    testSamplingPosATAC = epData.iloc[testIdx]
    testSamplingPosATAC.to_csv(testPosPrefix + ".atac.csv", header=False, index=False)
    testSamplingPosBS = mpData.iloc[testIdx]
    testSamplingPosBS.to_csv(testPosPrefix + ".bs.csv", header=False, index=False)

    del spData, epData, mpData

    # Negative Samples
    if args.nSeq:
        snData = pd.read_csv(args.nSeq, dtype='a', header=None)
    else:
        snData = None
    enData = pd.read_csv(args.nATAC, dtype='a', header=None)
    mnData = pd.read_csv(args.nBS, dtype='a', header=None)
    shuffleList = random.sample([x for x in range(negNums)], k=negNums)
    trainIdx = shuffleList[:(negNums // 2)]
    testIdx = shuffleList[(negNums // 2):]

    trainIdx = random.sample(trainIdx, k=(posNums // 2))

    if snData is not None:
        trainSamplingNegSeq = snData.iloc[trainIdx]
        trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
    trainSamplingNegATAC = enData.iloc[trainIdx]
    trainSamplingNegATAC.to_csv(trainNegPrefix + ".atac.csv", header=False, index=False)
    trainSamplingNegBS = mnData.iloc[trainIdx]
    trainSamplingNegBS.to_csv(trainNegPrefix + ".bs.csv", header=False, index=False)

    if snData is not None:
        testSamplingNegSeq = snData.iloc[testIdx]
        testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
    testSamplingNegATAC = enData.iloc[testIdx]
    testSamplingNegATAC.to_csv(testNegPrefix + ".atac.csv", header=False, index=False)
    testSamplingNegBS = mnData.iloc[testIdx]
    testSamplingNegBS.to_csv(testNegPrefix + ".bs.csv", header=False, index=False)

elif args.oversampling:
    if args.pSeq:
        spData = pd.read_csv(args.pSeq, dtype='a', header=None)
    else:
        spData = None
    epData = pd.read_csv(args.pATAC, dtype='a', header=None)
    mpData = pd.read_csv(args.pBS, dtype='a', header=None)

    shuffleList = random.sample([x for x in range(posNums)], k=posNums)
    trainIdx = shuffleList[:(posNums // 2)]
    trainIdx = random.choices(trainIdx, k=(negNums // 2))
    testIdx = shuffleList[(posNums // 2):]
    suffix = "over"

    trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
    trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
    testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
    testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

    if spData is not None:
        trainSamplingPosSeq = spData.iloc[trainIdx]
        trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
    trainSamplingPosATAC = epData.iloc[trainIdx]
    trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
    trainSamplingPosBS = mpData.iloc[trainIdx]
    trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

    if spData is not None:
        testSamplingPosSeq = spData.iloc[testIdx]
        testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
    testSamplingPosATAC = epData.iloc[testIdx]
    testSamplingPosATAC.to_csv(testPosPrefix + ".atac.csv", header=False, index=False)
    testSamplingPosBS = mpData.iloc[testIdx]
    testSamplingPosBS.to_csv(testPosPrefix + ".bs.csv", header=False, index=False)

    del spData, epData, mpData

    # Negative Samples
    if args.nSeq:
        snData = pd.read_csv(args.nSeq, dtype='a', header=None)
    else:
        snData = None
    enData = pd.read_csv(args.nATAC, dtype='a', header=None)
    mnData = pd.read_csv(args.nBS, dtype='a', header=None)
    shuffleList = random.sample([x for x in range(negNums)], k=negNums)
    trainIdx = shuffleList[:(negNums // 2)]
    testIdx = shuffleList[(negNums // 2):]

    if snData is not None:
        trainSamplingNegSeq = snData.iloc[trainIdx]
        trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
    trainSamplingNegATAC = enData.iloc[trainIdx]
    trainSamplingNegATAC.to_csv(trainNegPrefix + ".atac.csv", header=False, index=False)
    trainSamplingNegBS = mnData.iloc[trainIdx]
    trainSamplingNegBS.to_csv(trainNegPrefix + ".bs.csv", header=False, index=False)

    if snData is not None:
        testSamplingNegSeq = snData.iloc[testIdx]
        testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
    testSamplingNegATAC = enData.iloc[testIdx]
    testSamplingNegATAC.to_csv(testNegPrefix + ".atac.csv", header=False, index=False)
    testSamplingNegBS = mnData.iloc[testIdx]
    testSamplingNegBS.to_csv(testNegPrefix + ".bs.csv", header=False, index=False)

elif args.smote:
    sm = SMOTE(random_state=args.seed)

    # Read data
    if args.pSeq:
        spData = pd.read_csv(args.pSeq, dtype='a', header=None)
    else:
        spData = None
    epData = pd.read_csv(args.pATAC, dtype='a', header=None)
    mpData = pd.read_csv(args.pBS, dtype='a', header=None)

    if args.nSeq:
        snData = pd.read_csv(args.nSeq, dtype='a', header=None)
    else:
        snData = None
    enData = pd.read_csv(args.nATAC, dtype='a', header=None)
    mnData = pd.read_csv(args.nBS, dtype='a', header=None)

    shuffleList = random.sample([x for x in range(posNums)], k=posNums)
    trainIdx = shuffleList[:(posNums // 2)]
    testIdx = shuffleList[(posNums // 2):]
    suffix = "smote"

    # Set the prefix of file
    trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
    trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
    testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
    testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

    if spData is not None:
        trainSamplingPosSeq = spData.iloc[trainIdx]
        # trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
    trainSamplingPosATAC = epData.iloc[trainIdx]
    # trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
    trainSamplingPosBS = mpData.iloc[trainIdx]
    # trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

    if spData is not None:
        testSamplingPosSeq = spData.iloc[testIdx]
        testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
    testSamplingPosATAC = epData.iloc[testIdx]
    testSamplingPosATAC.to_csv(testPosPrefix + ".atac.csv", header=False, index=False)
    testSamplingPosBS = mpData.iloc[testIdx]
    testSamplingPosBS.to_csv(testPosPrefix + ".bs.csv", header=False, index=False)

    del spData, epData, mpData

    # Negative Samples
    shuffleList = random.sample([x for x in range(negNums)], k=negNums)
    trainIdx = shuffleList[:(negNums // 2)]
    testIdx = shuffleList[(negNums // 2):]

    if snData is not None:
        trainSamplingNegSeq = snData.iloc[trainIdx]
        trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
    trainSamplingNegATAC = enData.iloc[trainIdx]
    trainSamplingNegATAC.to_csv(trainNegPrefix + ".atac.csv", header=False, index=False)
    trainSamplingNegBS = mnData.iloc[trainIdx]
    trainSamplingNegBS.to_csv(trainNegPrefix + ".bs.csv", header=False, index=False)

    if snData is not None:
        testSamplingNegSeq = snData.iloc[testIdx]
        testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
    testSamplingNegATAC = enData.iloc[testIdx]
    testSamplingNegATAC.to_csv(testNegPrefix + ".atac.csv", header=False, index=False)
    testSamplingNegBS = mnData.iloc[testIdx]
    testSamplingNegBS.to_csv(testNegPrefix + ".bs.csv", header=False, index=False)

    # Smote oversampling the training set
    trainSamplingATAC = pd.concat([trainSamplingPosATAC, trainSamplingNegATAC])
    trainSamplingLabels = [1 for i in range(trainSamplingPosATAC.shape[0])] + [0 for i in range(trainSamplingNegATAC.shape[0])]
    trainSamplingATAC, trainSamplingLabels = sm.fit_resample(trainSamplingATAC, trainSamplingLabels)
    posIdx = []
    for idx in range(len(trainSamplingLabels)):
        if trainSamplingLabels[idx] == 1:
            posIdx.append(idx)
    trainSamplingPosATAC = trainSamplingATAC.iloc[posIdx]
    trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)

    trainSamplingBS = pd.concat([trainSamplingPosBS, trainSamplingNegBS])
    trainSamplingLabels = [1 for i in range(trainSamplingPosBS.shape[0])] + [0 for i in range(trainSamplingNegBS.shape[0])]
    trainSamplingBS, trainSamplingLabels = sm.fit_resample(trainSamplingBS, trainSamplingLabels)
    posIdx = []
    for idx in range(len(trainSamplingLabels)):
        if trainSamplingLabels[idx] == 1:
            posIdx.append(idx)
    trainSamplingPosBS = trainSamplingBS.iloc[posIdx]
    trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

elif args.mixsmote:
    sm = SMOTE(random_state=args.seed)

    # Read data
    if args.pSeq:
        spData = pd.read_csv(args.pSeq, dtype='a', header=None)
    else:
        spData = None
    epData = pd.read_csv(args.pATAC, dtype='a', header=None)
    mpData = pd.read_csv(args.pBS, dtype='a', header=None)

    if args.nSeq:
        snData = pd.read_csv(args.nSeq, dtype='a', header=None)
    else:
        snData = None
    enData = pd.read_csv(args.nATAC, dtype='a', header=None)
    mnData = pd.read_csv(args.nBS, dtype='a', header=None)

    shuffleList = random.sample([x for x in range(posNums)], k=posNums)
    trainIdx = shuffleList[:(posNums // 2)]
    testIdx = shuffleList[(posNums // 2):]
    suffix = "smote"

    # Set the prefix of file
    trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
    trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
    testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
    testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

    if spData is not None:
        trainSamplingPosSeq = spData.iloc[trainIdx]
        # trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
    trainSamplingPosATAC = epData.iloc[trainIdx]
    # trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
    trainSamplingPosBS = mpData.iloc[trainIdx]
    # trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

    if spData is not None:
        testSamplingPosSeq = spData.iloc[testIdx]
        testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
    testSamplingPosATAC = epData.iloc[testIdx]
    testSamplingPosATAC.to_csv(testPosPrefix + ".atac.csv", header=False, index=False)
    testSamplingPosBS = mpData.iloc[testIdx]
    testSamplingPosBS.to_csv(testPosPrefix + ".bs.csv", header=False, index=False)

    del spData, epData, mpData

    # Negative Samples
    shuffleList = random.sample([x for x in range(negNums)], k=negNums)
    trainIdx = shuffleList[:(negNums // 2)]
    testIdx = shuffleList[(negNums // 2):]

    if snData is not None:
        trainSamplingNegSeq = snData.iloc[trainIdx]
        trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
    trainSamplingNegATAC = enData.iloc[trainIdx]
    trainSamplingNegATAC.to_csv(trainNegPrefix + ".atac.csv", header=False, index=False)
    trainSamplingNegBS = mnData.iloc[trainIdx]
    trainSamplingNegBS.to_csv(trainNegPrefix + ".bs.csv", header=False, index=False)

    if snData is not None:
        testSamplingNegSeq = snData.iloc[testIdx]
        testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
    testSamplingNegATAC = enData.iloc[testIdx]
    testSamplingNegATAC.to_csv(testNegPrefix + ".atac.csv", header=False, index=False)
    testSamplingNegBS = mnData.iloc[testIdx]
    testSamplingNegBS.to_csv(testNegPrefix + ".bs.csv", header=False, index=False)

    # Smote oversampling the training set
    trainSamplingATAC = pd.concat([trainSamplingPosATAC, trainSamplingNegATAC])
    trainSamplingBS = pd.concat([trainSamplingPosBS, trainSamplingNegBS])
    trainSample = pd.concat([trainSamplingATAC, trainSamplingBS], axis=1)
    trainSampleLabels = [1 for i in range(trainSamplingPosATAC.shape[0])] + [0 for i in range(trainSamplingNegATAC.shape[0])]
    trainSample, trainSamplingLabels = sm.fit_resample(trainSample.to_numpy(), trainSampleLabels)
    trainSample = pd.DataFrame(trainSample)
    posIdx = []
    for idx in range(len(trainSamplingLabels)):
        if trainSamplingLabels[idx] == 1:
            posIdx.append(idx)
    trainSamplingPosATAC = trainSample.iloc[posIdx, :trainSamplingATAC.shape[1]]
    trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
    trainSamplingPosBS = trainSample.iloc[posIdx, trainSamplingATAC.shape[1]:]
    trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

# Positive Samples
# if args.pSeq:
#     spData = pd.read_csv(args.pSeq, dtype='a', header=None)
# else:
#     spData = None
# epData = pd.read_csv(args.pATAC, dtype='a', header=None)
# mpData = pd.read_csv(args.pBS, dtype='a', header=None)

# shuffleList = random.sample([x for x in range(posNums)], k=posNums)
# trainIdx = shuffleList[:(posNums // 2)]
# testIdx = shuffleList[(posNums // 2):]

# suffix = "under"
# if args.oversampling:
#     # Oversampling
#     trainIdx = random.choices(trainIdx, k=(negNums // 2))
#     suffix = "over"

# # Set the result name
# trainPosPrefix = os.path.join(args.outdir, "trainPos.random{}.{}".format(args.seed, suffix))
# trainNegPrefix = os.path.join(args.outdir, "trainNeg.random{}.{}".format(args.seed, suffix))
# testPosPrefix = os.path.join(args.outdir, "testPos.random{}.{}".format(args.seed, suffix))
# testNegPrefix = os.path.join(args.outdir, "testNeg.random{}.{}".format(args.seed, suffix))

# if spData is not None:
#     trainSamplingPosSeq = spData.iloc[trainIdx]
#     trainSamplingPosSeq.to_csv(trainPosPrefix + ".seq.csv", header=False, index=False)
# trainSamplingPosATAC = epData.iloc[trainIdx]
# trainSamplingPosATAC.to_csv(trainPosPrefix + ".atac.csv", header=False, index=False)
# trainSamplingPosBS = mpData.iloc[trainIdx]
# trainSamplingPosBS.to_csv(trainPosPrefix + ".bs.csv", header=False, index=False)

# if spData is not None:
#     testSamplingPosSeq = spData.iloc[testIdx]
#     testSamplingPosSeq.to_csv(testPosPrefix + ".seq.csv", header=False, index=False)
# testSamplingPosATAC = epData.iloc[testIdx]
# testSamplingPosATAC.to_csv(testPosPrefix + ".atac.csv", header=False, index=False)
# testSamplingPosBS = mpData.iloc[testIdx]
# testSamplingPosBS.to_csv(testPosPrefix + ".bs.csv", header=False, index=False)

# del spData, epData, mpData

# # Negative Samples
# if args.nSeq:
#     snData = pd.read_csv(args.nSeq, dtype='a', header=None)
# else:
#     snData = None
# enData = pd.read_csv(args.nATAC, dtype='a', header=None)
# mnData = pd.read_csv(args.nBS, dtype='a', header=None)
# shuffleList = random.sample([x for x in range(negNums)], k=negNums)
# trainIdx = shuffleList[:(negNums // 2)]
# testIdx = shuffleList[(negNums // 2):]

# if args.undersampling:
#     # Undersampling
#     trainIdx = random.sample(trainIdx, k=(posNums // 2))

# if snData is not None:
#     trainSamplingNegSeq = snData.iloc[trainIdx]
#     trainSamplingNegSeq.to_csv(trainNegPrefix + ".seq.csv", header=False, index=False)
# trainSamplingNegATAC = enData.iloc[trainIdx]
# trainSamplingNegATAC.to_csv(trainNegPrefix + ".atac.csv", header=False, index=False)
# trainSamplingNegBS = mnData.iloc[trainIdx]
# trainSamplingNegBS.to_csv(trainNegPrefix + ".bs.csv", header=False, index=False)

# if snData is not None:
#     testSamplingNegSeq = snData.iloc[testIdx]
#     testSamplingNegSeq.to_csv(testNegPrefix + ".seq.csv", header=False, index=False)
# testSamplingNegATAC = enData.iloc[testIdx]
# testSamplingNegATAC.to_csv(testNegPrefix + ".atac.csv", header=False, index=False)
# testSamplingNegBS = mnData.iloc[testIdx]
# testSamplingNegBS.to_csv(testNegPrefix + ".bs.csv", header=False, index=False)
