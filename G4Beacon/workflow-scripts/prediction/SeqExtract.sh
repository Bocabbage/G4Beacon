G4SEQ_PATH=$1
REF_PATH=$2
OUTPUT_PATH=.
SCRIPT_PATH=../../dataPreprocess

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_plus.hits.max.K.w50.25.bed \
    -oseq plus.g4seqFirst.F0.1.ex1000.seq.full.csv \
    -obi plus.g4seqFirst.F0.1.ex1000.origin.full.bed \
    -fi ${REF_PATH} \
    --extend 1000 --reverse &&

python ${SCRIPT_PATH}/g4seqPreprocess.py \
    -i ${G4SEQ_PATH}/GSM3003539_Homo_all_w15_th-1_minus.hits.max.K.w50.25.bed \
    -oseq minus.g4seqFirst.F0.1.ex1000.seq.full.csv \
    -obi minus.g4seqFirst.F0.1.ex1000.origin.full.bed \
    -fi ${REF_PATH} \
    --extend 1000