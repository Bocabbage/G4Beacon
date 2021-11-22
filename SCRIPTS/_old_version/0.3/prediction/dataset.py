#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/08/10
# Author: Zhuofan Zhang
import numpy as np
import pandas as pd
from sklearn.preprocessing import Normalizer


class g4SeqEnv:
    def __init__(self,
                 vg4Seq: str = None,
                 ug4Seq: str = None,
                 vg4ATAC: str = None,
                 ug4ATAC: str = None,
                 vg4BS: str = None,
                 ug4BS: str = None,
                 extend: int = None):

        if vg4Seq:
            vg4seqFeatures = pd.read_csv(vg4Seq, dtype='a', header=None)
            ug4seqFeatures = pd.read_csv(ug4Seq, dtype='a', header=None)
            pSampleNums = vg4seqFeatures.shape[0]
            nSampleNums = ug4seqFeatures.shape[0]

            if extend:
                mid = vg4seqFeatures.shape[1] // 2
                vg4seqFeatures = vg4seqFeatures.iloc[:, mid - extend:mid + extend]
                ug4seqFeatures = ug4seqFeatures.iloc[:, mid - extend:mid + extend]
            seqFeatures = pd.concat([vg4seqFeatures, ug4seqFeatures])
        else:
            seqFeatures = None

        if vg4ATAC:
            vg4atacFeatures = pd.read_csv(vg4ATAC, dtype='a', header=None)
            ug4atacFeatures = pd.read_csv(ug4ATAC, dtype='a', header=None)
            pSampleNums = vg4atacFeatures.shape[0]
            nSampleNums = ug4atacFeatures.shape[0]
            atacFeatures = pd.concat([vg4atacFeatures, ug4atacFeatures])
        else:
            atacFeatures = None

        if vg4BS:
            vg4bsFeatures = pd.read_csv(vg4BS, dtype='a', header=None)
            ug4bsFeatures = pd.read_csv(ug4BS, dtype='a', header=None)
            pSampleNums = vg4bsFeatures.shape[0]
            nSampleNums = ug4bsFeatures.shape[0]
            bsFeatures = pd.concat([vg4bsFeatures, ug4bsFeatures])
        else:
            bsFeatures = None

        featureList = [seqFeatures, atacFeatures, bsFeatures]
        self.Features = None
        for feature in featureList:
            if feature is not None:
                if self.Features is not None:
                    self.Features = pd.concat([self.Features, feature], axis=1)
                else:
                    self.Features = feature

            # self.seqFeatures = pd.concat([vg4seqFeatures, ug4seqFeatures])
            # self.envFeatures = pd.concat([vg4envFeatures, ug4envFeatures])

            # Normalization
            # if normalization:
            #     self.envFeatures = Normalizer.fit_transform(self.envFeatures)

            # self.Labels = [1 for i in range(vg4seqFeatures.shape[0])] + [0 for i in range(ug4seqFeatures.shape[0])]
            self.Labels = np.array([1 for i in range(pSampleNums)] + [0 for i in range(nSampleNums)])

    def __len__(self):
        return len(self.Labels)

    def __getitem__(self, idx):
        # return (self.seqFeatures.iloc[idx], self.envFeatures.iloc[idx]), self.Labels[idx]
        return self.Features.iloc[idx], self.Labels[idx]
