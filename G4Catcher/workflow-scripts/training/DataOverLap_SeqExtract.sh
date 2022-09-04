G4SEQ_PATH=$1
G4CHIP_PATH=$2
REF_PATH=$3
OUTPUT_PATH=.
SCRIPT_PATH=../../dataPreprocess

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -wa -F 0.1 | sort -k1,1 -k2,2n | sort -k1,1 -k2,2n -u > plus.g4seqFirst.F0.1.bed &&

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -v -F 0.1 | sort -k1,1 -k2,2n | sort -k1,1 -k2,2n -u > plus_v.g4seqFirst.F0.1.bed &&


bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_minus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -wa -F 0.1 | sort -k1,1 -k2,2n | sort -k1,1 -k2,2n -u > minus.g4seqFirst.F0.1.bed &&

bedtools intersect -a ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_minus.hits.max.K.w50.25.bed \
                    -b ${G4CHIP_PATH} \
                    -v -F 0.1 | sort -k1,1 -k2,2n | sort -k1,1 -k2,2n -u > minus_v.g4seqFirst.F0.1.bed &&

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i plus.g4seqFirst.F0.1.bed \
    -oseq plus.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi plus.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --extend 1000 --reverse &&

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i plus_v.g4seqFirst.F0.1.bed \
    -oseq plus_v.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi plus_v.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --extend 1000 --reverse &&

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i minus.g4seqFirst.F0.1.bed \
    -oseq minus.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi minus.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --extend 1000 &&

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i minus_v.g4seqFirst.F0.1.bed \
    -oseq minus_v.g4seqFirst.F0.1.ex1000.seq.csv \
    -obi minus_v.g4seqFirst.F0.1.ex1000.origin.bed \
    -fi ${REF_PATH} \
    --extend 1000