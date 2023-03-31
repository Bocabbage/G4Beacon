# G4Beacon: An *in vivo* G4 prediction method using chromatin and sequence information

## <img src="./suppl-pics/beacon.ico"/> Introduction

G-quadruplex (G4) structures are critical epigenetic regulatory elements, which usually form in guanine-rich regions in DNA. However, predicting the formation of G4 structures within living cells remains a challenge. Here, we present an ultra-robust machine learning method, G4Beacon, which utilizes the Gradient-Boosting Decision Tree (GBDT) algorithm, coupled with the ATAC-seq data and the surrounding sequences of in vitro G4s, to accurately predict the for-mation ability of these in vitro G4s in different cell types. As a result, our model achieved excel-lent performance even when the test set was extremely skewed. Besides this, G4Beacon can also identify the in vivo G4s of other cell lines precisely with the model built on a special cell line, regardless of the experimental techniques or platforms. Altogether, G4Beacon is an accurate, re-liable, and easy-to-use method for the prediction of in vivo G4s of various cell lines.

<img src="./suppl-pics/fig1.png" alt="fig1" style="zoom:80%;" />

## <img src="./suppl-pics/beacon.ico"/> Prerequisites

### Dependencies

- Ubuntu 20.04.4 LTS
- Bedtools 2.29.2
- Deeptools 3.5.1
- Python 3.9.7

### Installation

The Linux command tools: *bedtools* and *deeptools* should be installed and added to `PATH` before you used *G4Beacon*.
You can install G4Beacon using the following Linux-shell commands:
```
$ git clone https://github.com/Bocabbage/G4Beacon.git
$ cd G4Beacon/
$ python setup.py install
```
It's more recommanded to use *G4Beacon* by creating a new env with *anaconda*.

## <img src="./suppl-pics/beacon.ico"/> Sub-commands

```
$ g4beacon --help
        [g4beacon] is an in vivo G4 prediction tool taking seq+atac feature inputs.
        This software can be used to construct the feature, train on your own data or
        predict in vivo G4s. We provide the following sub-tools:
        - seqFeatureConstruct   [Takes BED-format file as input to construct sequence-feature]
        - atacFeatureConstruct  [Takes BigWig file as input to construct atac-feature]
        - getActiveG4s          [Predicts in vivo G4s]
        - trainingsetConstruct  [Takes your constructed-feature data and create a balanced training-set]
        - trainOwnData          [Trains GBDT model with your own data]
        Usage: g4beacon atacFeatureConstruct -h
        More information: https://github.com/Bocabbage/G4Beacon
```
## <img src="./suppl-pics/beacon.ico"/> Workflow & Example

<img src="./suppl-pics/fig2.png" alt="fig2" style="zoom:80%;" />

### Training

#### 1. Training-set Preparing

```bash
# Pos/neg data division
# For combination of {posChain-G4ChIPpos, negChain-G4ChIPpos, posChain-G4ChIPneg, negChain-G4ChIPneg}
bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -wa -F 0.1 | sort -k1,1 -k2,2n -u > plus.g4seqFirst.F0.1.bed &&

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -v -F 0.1 | sort -k1,1 -k2,2n -u > plus_v.g4seqFirst.F0.1.bed &&

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_minus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -wa -F 0.1 | sort -k1,1 -k2,2n -u > minus.g4seqFirst.F0.1.bed &&

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_minus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -v -F 0.1 | sort -k1,1 -k2,2n -u > minus_v.g4seqFirst.F0.1.bed &&

g4beacon seqFeatureConstruct \
    -i plus.g4seqFirst.F0.1.bed \
    -oseq plus.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi plus.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --reverse &&     
    # When origin-data is from the neg-chain, turn on the '--reverse' option

g4beacon seqFeatureConstruct \
    -i plus_v.g4seqFirst.F0.1.bed \
    -oseq plus_v.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi plus_v.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --reverse &&

g4beacon seqFeatureConstruct \
    -i minus.g4seqFirst.F0.1.bed \
    -oseq minus.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi minus.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    &&

g4beacon seqFeatureConstruct \
    -i minus_v.g4seqFirst.F0.1.bed \
    -oseq minus_v.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi minus_v.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH}

# Construct the chromatin-accessibility feature
# For feature in {vg4-pos, vg4-neg, ug4-pos, ug4-neg}:
g4beacon atacFeatureConstruct \
       -p          [threadNums] \
       --g4Input   [g4seq-origin-bed file imported from the former step] \
       --envInput  [ATAC-seq signal-track file (BIGWIG)] \
       --csvOutput [Output path of the result atac feature file (CSV)]

# Cat pos/neg chain data
cat [vg4-pos seq CSV] [vg4-neg seq CSV] > [vg4 seq CSV]
cat [ug4-pos seq CSV] [ug4-neg seq CSV] > [ug4 seq CSV]
cat [vg4-pos atac CSV] [vg4-neg atac CSV] > [vg4 atac CSV]
cat [ug4-pos atac CSV] [ug4-neg atac CSV] > [ug4 atac CSV]


# Construct training set (over-sampling)
g4beacon trainingsetConstruct \
       --vg4seqCSV  [Positive seq-feature file path (CSV)] \
       --ug4seqCSV  [Negative seq feature file path (CSV)] \
       --vg4atacCSV [Positive atac feature file path (CSV)] \
       --ug4atacCSV [Negative atac feature file path (CSV)] \
       --outdir     [result output dir]
```

#### 2. Model Training

```bash
g4beacon trainOwnData \
       --vg4seqCSV  [Positive seq-feature file path (CSV)] \
       --ug4seqCSV  [Negative seq feature file path (CSV)] \
       --vg4atacCSV [Positive atac feature file path (CSV)] \
       --ug4atacCSV [Negative atac feature file path (CSV)] \
       --oname      [prefix-name of the output trained-model-param file (JOBLIB)] \
       --outdir     [output file dir]
```

### Prediction

#### 1. Feature Construction

```bash
# Build G4-candidate dataset and construct the sequence feature
# For g4seq file of {pos, neg} chains:
g4beacon seqFeatureConstruct \
     -i    [G4-seq data path (BED)] \  # sorted GSE110582-K+ (like: GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed)
     -fi   [Reference-genome data path (FASTA)] \ # the pre-trained model we provided is under hg19
     -oseq [Output path of the result seq feature file (CSV)] \
     -obi  [Output path of the result cleaned g4-seq entries (the "origin-bed file") (BED)] \
     {--reverse} # It's essential for neg-chain data

# Construct the chromatin-accessibility feature
# For feature in {pos, neg}:
g4beacon atacFeatureConstruct \
       -p          [threadNums] \
       --g4Input   [g4seq-origin-bed file imported from the former step] \
       --envInput  [ATAC-seq signal-track file (BIGWIG)] \
       --csvOutput [Output path of the result atac feature file (CSV)]
```

#### 2. Prediction

```bash
# For feature in {pos, neg}:
g4beacon getActiveG4s \
       --seqCSV     [seq-feature file (CSV) generated in 'seqFeatureConstruct' step] \
       --atacCSV    [atac-feature file (CSV) generated in 'atacFeatureConstruct' step] \
       --originBED  [origin-g4-seq-entry file (BED) generated in 'seqFeatureConstruct' step] \
       -o           [in vivo G4 entries (BED)] \
```
