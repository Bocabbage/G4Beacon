#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/10/23
# Author: Zhuofan Zhang
import torch.utils.data as data
from torch import from_numpy
import numpy as np
import pandas as pd


class g4SeqEnv(data.Dataset):
    def __init__(self,
                 vg4Seq: str = None,
                 vg4ATAC: str = None,
                 vg4BS: str = None,
                 extend: int = None):

        if vg4Seq:
            vg4seqFeatures = pd.read_csv(vg4Seq, dtype='a', header=None)
            pSampleNums = vg4seqFeatures.shape[0]

            if extend:
                mid = vg4seqFeatures.shape[1] // 2
                vg4seqFeatures = vg4seqFeatures.iloc[:, mid - extend:mid + extend]
            # seqFeatures = pd.concat([vg4seqFeatures, ug4seqFeatures])
            seqFeatures = vg4seqFeatures
        else:
            seqFeatures = None

        if vg4ATAC:
            vg4atacFeatures = pd.read_csv(vg4ATAC, dtype='a', header=None)
            pSampleNums = vg4atacFeatures.shape[0]
            # atacFeatures = pd.concat([vg4atacFeatures, ug4atacFeatures])
            atacFeatures = vg4atacFeatures
        else:
            atacFeatures = None

        if vg4BS:
            vg4bsFeatures = pd.read_csv(vg4BS, dtype='a', header=None)
            pSampleNums = vg4bsFeatures.shape[0]
            # bsFeatures = pd.concat([vg4bsFeatures, ug4bsFeatures])
            bsFeatures = vg4bsFeatures
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

        self.Features = from_numpy(np.nan_to_num(self.Features.to_numpy().astype(np.float32)))
        self.Labels = np.array([1 for i in range(pSampleNums)])

    def __len__(self):
        return len(self.Labels)

    def __getitem__(self, idx):
        # return (self.seqFeatures.iloc[idx], self.envFeatures.iloc[idx]), self.Labels[idx]
        return self.Features[idx], self.Labels[idx]
