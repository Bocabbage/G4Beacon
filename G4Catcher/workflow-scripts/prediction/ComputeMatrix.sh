CONFIGFILE=$1
OUTPUT_PATH=.
SCRIPT_PATH=../../dataPreprocess

python ${SCRIPT_PATH}/computeMatrix.py --json ${CONFIGFILE} && 

# concat seq
cat minus.g4seqFirst.F0.1.ex1000.seq.full.csv plus.g4seqFirst.F0.1.ex1000.seq.full.csv > CATmp.g4seqFirst.F0.1.ex1000.seq.full.csv &&

# concat atac
cat minus.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.full.csv plus.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.full.csv > CATmp.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.full.csv &&
