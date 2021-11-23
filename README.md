# in-vivo G4-DNA prediction

### I. Old-version Log

- ** version 0.1: ** Use narrowPeak from ATAC-seq as chromatin accessibility features

- ** version 0.2: ** Try K-mer features; Add SMOTE-oversampling experiment

- ** version 0.3: **  Use JSON as the experiment config input and log; Use signal/fold-change files as chromatin accessibility features. [Last updated: 2021/11/15]

  <u>The above versions split dataset into 2 parts: train/test and use Precision/Recall/AUC/AUPRC as criterions.</u>



### II. Now-version

​	[ Start at 2021/11/15, unfinished ]

**Two parts of the workflow:**

- **In one Cell-line:** Split the dataset into 3 parts: train/validation/test set
- **Cross-test:** Use full-size dataset from one cell-line and test on dataset from another

