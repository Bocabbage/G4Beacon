#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2022/02/28
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import use
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, precision_score
use('Agg')

parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, default=None)
args = parser.parse_args()

with open(args.json, 'r') as jfile:
    jsonData = json.load(jfile)

# Load data
trainPosData = pd.read_csv(jsonData["train-pos-data"], dtype='a', header=None)
testPosData = pd.read_csv(jsonData["test-pos-data"], dtype='a', header=None)

try:
    trainNegData = pd.read_csv(jsonData["train-neg-data"], dtype='a', header=None)
except ValueError:
    trainNegData = None

try:
    testNegData = pd.read_csv(jsonData["test-neg-data"], dtype='a', header=None)
except ValueError:
    testNegData = None

if trainNegData is not None:
    trainData = pd.concat([trainPosData, trainNegData], ignore_index=True)
else:
    trainData = trainPosData

if testNegData is not None:
    testData = pd.concat([testPosData, testNegData], ignore_index=True)
else:
    testData = testPosData

features = pd.concat([trainData, testData], ignore_index=True)
labels = np.array([1 for i in range(trainData.shape[0])] + [0 for i in range(testData.shape[0])])

# Classification
clf = LogisticRegression(random_state=42).fit(features, labels)
y_pred = clf.predict_proba(features)
y_pred = np.argmax(y_pred, axis=1)

print(f"train-data-size: {trainData.shape[0]}")
print(f"test-data-size: {testData.shape[0]}")
print(f"accuracy: {accuracy_score(labels, y_pred)}")
print(f"precision: {precision_score(labels, y_pred)}")
print(f"recall: {recall_score(labels, y_pred)}")

pca = PCA(n_components=2)
features_pca = pca.fit_transform(features)
label_names = jsonData['label-names']
colors = ["navy", "turquoise"]
alphas = [0.9, 0.1]

fig, ax = plt.subplots(figsize=(10, 10))
for color, idx, label_name, alpha in zip(colors, [0, 1], label_names, alphas):
    # print(f"{color}, {idx}, {label_name}, {alpha}")
    ax.scatter(
        features_pca[labels == idx, 0],
        features_pca[labels == idx, 1],
        color=color,
        label=label_name,
        alpha=alpha
    )
    # print(f"feature0 size: {features_pca[labels == idx, 0].shape}")
    # print(f"feature1 size: {features_pca[labels == idx, 1].shape}")

ax.set_title("PCA(n=2) of samples")
ax.legend(loc="lower right")
fig.savefig(jsonData['save-fig'])
