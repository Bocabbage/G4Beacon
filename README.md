# G4Catcher: An in vivo G4 prediction method using chromatin and sequence information

## I. Introduction

G-quadruplex (G4) is a kind of the non-canonical secondary structure which usually formed in guanine-rich regions. G4 detection method based on next-generation sequencing technology allows profiling G4s in vitro on a genome-wide scale, which imputed numerous G4 entries on the human genome. However, recent G4 ChIP-seq technology established for in vivo G4 detection revealed that the amount of G4s in living cells is substantially lower. In vivo G4 sites can provide more convincing support for exploring the biological function of G4s, as these sites are direct evidence for the presence of folded G4s. However, there are some limitations to the G4-probing methods, for example, they are high-cost and difficult to operate. We proposed G4Catcher, a new machine-learning approach to predict whether in vitro G4 entries can actually fold into quadruplex structures in a given cell type, by integrating the chromatin accessibility profile and the surrounding sequence of G4 entries.

<img src="./suppl-pics/fig1.png" alt="fig1" style="zoom:80%;" />

## II. Dependencies
- Ubuntu 20.04.4 LTS
- Bedtools 2.29.2
- Deeptools 3.5.1
- Python 3.9.7
  - LightGBM 3.2.1
  - imblearn 0.8.1
  - scikit-learn 1.0.1

## III. Code Structure

-  `/G4Catcher`
    - `workflow-scripts` : the wieldy scripts provided for users.
    - `dataPreprocess` : the python-scripts for data preprocessing.
    - `prediction` : the codes of the whole classifier-implement and scripts of model evaluation.
    - `visualization` : the util-codes for result-visualization.

## IV. Workflow & Usage

<img src="./suppl-pics/fig2.png" alt="fig2" style="zoom:80%;" />

### Training
#### 1. Feature Selection (Construction)
```bash
mkdir {output-dir}
cd {output-dir}

# 1) Build G4-candidate dataset
# 2) Pos/neg data division
bash workflow-scripts/training/DataOverLap_SeqExtract.sh \
     {G4-seq data directory} \        # GSE110582-K+
     {G4 ChIP-seq data path} \
     {Reference-genome data path}

# Construct the chromatin-accessibility feature
bash workflow-scripts/training/ComputeMatrix.sh \
     {json file [compute matrix config]}

# Dataset division
bash workflow-scripts/training/DatasetDivision.sh \
     {json file [dataset division config]}
```

#### 2. Model Training
```bash
# working-dir: {output-dir} in the feature-selection step
bash workflow-scripts/training/Training.sh \
     {json file [training config]}
```

### Prediction

#### 1. Feature Selection (Construction)
```bash
mkdir {output-dir}
cd {output-dir}

# Build G4-candidate dataset
bash workflow-scripts/prediction/SeqExtract.sh \
     {G4-seq data path} \           # GSE110582-K+
     {Reference-genome data path}

# Construct the chromatin-accessibility feature
bash workflow-scripts/prediction/ComputeMatrix.sh \
     {json file [compute matrix config]}
```

#### 2. Prediction
```bash
# working-dir: {output-dir} in the feature-selection step
bash workflow-scripts/prediction/Predict.sh \
     {json file [prediction config]} # output of the 'training' step
```

## Old-version Log

- version 0.1: Use narrowPeak from ATAC-seq as chromatin accessibility features

- version 0.2: Try K-mer features; Add SMOTE-oversampling experiment

- version 0.3:  Use JSON as the experiment config input and log; Use signal/fold-change files as chromatin accessibility features. [Last updated: 2021/11/15]

