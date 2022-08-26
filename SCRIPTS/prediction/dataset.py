#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2022/01/21
# Author: Zhuofan Zhang
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize


def onehot_encoder(samples):
    res = np.zeros([samples.shape[0], samples.shape[1], 4], dtype=np.float32)
    for idx, sample in enumerate(samples):
        for jdx, base in enumerate(sample):
            res[idx][jdx][int(base)] = 1
    return res


class g4SeqEnv:
    def __init__(self,
                 vg4Seq: str = None,
                 ug4Seq: str = None,
                 vg4ATAC: str = None,
                 ug4ATAC: str = None,
                 vg4ATACFd: str = None,
                 ug4ATACFd: str = None,
                 vg4BS: str = None,
                 ug4BS: str = None,
                 normalization: bool = False,
                 **kwformat_input):
        r'''
            Take feature-file-name(s) as input, load and preprocess
            to construct feature[pandas]/label[np.array] format objects.

            Note: if use **kwformat_input param, the former input param(s) will be ignored
                  except the normalization setting. Usage example of this param is in param_tuning_cv.py.
        '''
        if kwformat_input:
            # fix me: it's so dirty
            # Maybe use locals(), but it's dangerous
            vg4Seq = kwformat_input['vg4seq']
            ug4Seq = kwformat_input['ug4seq']
            vg4ATAC = kwformat_input['vg4atac']
            ug4ATAC = kwformat_input['ug4atac']
            vg4BS = kwformat_input['vg4bs']
            ug4BS = kwformat_input['ug4bs']
            vg4ATACFd = kwformat_input['vg4atacFd']  # First-diff of vg4atac
            ug4ATACFd = kwformat_input['ug4atacFd']  # First-diff of ug4atac

        if vg4Seq and ug4Seq:
            vg4seqFeatures = pd.read_csv(vg4Seq, dtype='a', header=None)
            ug4seqFeatures = pd.read_csv(ug4Seq, dtype='a', header=None)
            pSampleNums = vg4seqFeatures.shape[0]
            nSampleNums = ug4seqFeatures.shape[0]

            # if extend:
            #     mid = vg4seqFeatures.shape[1] // 2
            #     vg4seqFeatures = vg4seqFeatures.iloc[:, mid - extend:mid + extend]
            #     ug4seqFeatures = ug4seqFeatures.iloc[:, mid - extend:mid + extend]
            seqFeatures = pd.concat([vg4seqFeatures, ug4seqFeatures], ignore_index=True)
        else:
            seqFeatures = None

        if vg4ATAC and ug4ATAC:
            vg4atacFeatures = pd.read_csv(vg4ATAC, dtype='a', header=None)
            ug4atacFeatures = pd.read_csv(ug4ATAC, dtype='a', header=None)
            pSampleNums = vg4atacFeatures.shape[0]
            nSampleNums = ug4atacFeatures.shape[0]
            atacFeatures = pd.concat([vg4atacFeatures, ug4atacFeatures], ignore_index=True)
            if normalization:
                atacFeatures = pd.DataFrame(normalize(atacFeatures, 'l2'))
        else:
            atacFeatures = None

        if vg4BS and ug4BS:
            vg4bsFeatures = pd.read_csv(vg4BS, dtype='a', header=None)
            ug4bsFeatures = pd.read_csv(ug4BS, dtype='a', header=None)
            pSampleNums = vg4bsFeatures.shape[0]
            nSampleNums = ug4bsFeatures.shape[0]
            bsFeatures = pd.concat([vg4bsFeatures, ug4bsFeatures], ignore_index=True)
            if normalization:
                bsFeatures = pd.DataFrame(normalize(bsFeatures, 'l2'))
        else:
            bsFeatures = None

        if vg4ATACFd and ug4ATACFd:
            vg4atacFdFeatures = pd.read_csv(vg4ATACFd, dtype='a', header=None)
            ug4atacFdFeatures = pd.read_csv(ug4ATACFd, dtype='a', header=None)
            pSampleNums = vg4atacFdFeatures.shape[0]
            nSampleNums = ug4atacFdFeatures.shape[0]
            atacFdFeatures = pd.concat([
                vg4atacFdFeatures, ug4atacFdFeatures],
                ignore_index=True
            )
            if normalization:
                atacFdFeatures = pd.DataFrame(normalize(atacFdFeatures, 'l2'))
        else:
            atacFdFeatures = None

        featureList = [seqFeatures, atacFeatures, bsFeatures, atacFdFeatures]
        self.Features = None
        for feature in featureList:
            if feature is not None:
                if self.Features is not None:
                    self.Features = pd.concat([self.Features, feature], axis=1, ignore_index=True)
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
