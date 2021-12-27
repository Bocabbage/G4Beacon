#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/12/14
# Author: Zhuofan Zhang
import os
import json
import argparse
import random
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, recall_score, precision_score, auc, roc_curve, precision_recall_curve
from lightgbm import LGBMClassifier
from dataset import g4SeqEnv
from commonUtils import join_path


def balance_sampling(pos_idx, neg_idx,
                     flags: str = 'undersampling', random_state: int = 42):
    r'''
        take pos_idx/neg_idx of samples in imbalanced size,
        do under/oversampling and return concate index np.array
    '''
    random.seed(random_state)
    if flags == 'undersampling':
        balanced_pos_idx = pos_idx
        balanced_neg_idx = np.array(random.sample(list(neg_idx), k=len(pos_idx)))
    elif flags == 'oversampling':
        balanced_pos_idx = np.array(random.choices(list(pos_idx), k=len(neg_idx)))
        balanced_neg_idx = neg_idx

    return np.concatenate((balanced_pos_idx, balanced_neg_idx))


parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, help="Input cross-validation config json file.")
args = parser.parse_args()

#### Load config-json file
with open(args.json, 'r') as json_file:
    json_data = json.load(json_file)
norm = json_data['normalization']
dataset_dir = json_data['dataset_dir']
file_dict = json_data['files']
sampling_flag = json_data['sampling_flag']
model = json_data['model']
kfold = json_data['kfold']
output_dir = json_data['output_dir']
random_state = json_data['random_state']

if 'categorical_feature' in json_data.keys():
    start, end = json_data['categorical_feature']
    categorical_feature_idx = [i for i in range(start, end)]
else:
    categorical_feature_idx = 'auto'


#### Load data ####
for key in file_dict.keys():
    file_dict[key] = join_path(dataset_dir, file_dict[key])

g4_dataset = g4SeqEnv(normalization=norm, **file_dict)


#### K-fold split ####
dataset_idx = []
skf = StratifiedKFold(n_splits=kfold, shuffle=True, random_state=random_state)
for train_idx, test_idx in skf.split(g4_dataset.Features, g4_dataset.Labels):
    dataset_idx.append((train_idx, test_idx))

#### Grid-search tunning cv ####
## params setting
params_grid = json_data['params_grid']
# for key, value in params_grid.items():
#     params_grid[key] = [x for x in range(value[0], value[1], value[2])]

criterion = ['acc', 'pre', 'rec', 'auroc', 'auprc']
dt = np.dtype([(x, float) for x in criterion])
result_grid = np.zeros(
    shape=[len(value) for value in params_grid.values()],
    dtype=dt
)
search_it = np.nditer(result_grid, flags=['multi_index'])

## data-balancing: under/oversampling
# list of (train_features, train_labels, test_features, test_labels)
balanced_datasets = []
for train_idx, test_idx in dataset_idx:
    train_pos_idx = train_idx[g4_dataset.Labels[train_idx] == 1]
    train_neg_idx = train_idx[g4_dataset.Labels[train_idx] == 0]
    balanced_train_idx = balance_sampling(train_pos_idx, train_neg_idx, sampling_flag, random_state)

    balanced_datasets.append((
        g4_dataset.Features.iloc[balanced_train_idx],
        g4_dataset.Labels[balanced_train_idx],
        g4_dataset.Features.iloc[test_idx],
        g4_dataset.Labels[test_idx]
    ))
del g4_dataset

## Grid search
if model == 'lightGBM':
    clf = LGBMClassifier()
    trivial_params = {'seed': random_state, 'objective': 'binary'}
    clf.set_params(**trivial_params)

for point in search_it:
    mult_idx = search_it.multi_index
    params = {}
    # From Python 3.6 onwards, the standard dict type maintains insertion order by default.
    for idx, key in enumerate(params_grid.keys()):
        params[key] = params_grid[key][mult_idx[idx]]

    clf.set_params(**params)

    # K-fold validation
    criterion_results = {
        'acc': 0, 'pre': 0, 'rec': 0, 'auroc': 0, 'auprc': 0
    }

    for dataset in balanced_datasets:
        # training
        clf.fit(
            # (train_data, train_label)
            dataset[0].to_numpy(),
            dataset[1],
            categorical_feature=categorical_feature_idx
        )

        # eval
        y_pred = clf.predict_proba(dataset[2].to_numpy())  # test_data
        y_pred = np.argmax(y_pred, axis=1)

        criterion_results['rec'] += recall_score(dataset[3], y_pred)
        criterion_results['pre'] += precision_score(dataset[3], y_pred)
        criterion_results['acc'] += accuracy_score(dataset[3], y_pred)

        # get AUROC
        fpr, tpr, _ = roc_curve(dataset[3], y_pred)
        criterion_results['auroc'] += auc(fpr, tpr)

        # get AUPRC
        prec, rec, _ = precision_recall_curve(dataset[3], y_pred)
        criterion_results['auprc'] += auc(rec, prec)

    # Calculate the average of the criterion
    criterion_results = {x: (criterion_results[x] / kfold) for x in criterion_results.keys()}

    # write to the result_grid
    for key in criterion_results.keys():
        result_grid[search_it.multi_index][key] = criterion_results[key]

#### Result-save ####
if os.path.isdir(output_dir) is not True:
    os.makedirs(output_dir)

save_file_name = join_path(output_dir, "result_grid.npy")
with open(save_file_name, 'wb') as wfile:
    np.save(wfile, result_grid)
