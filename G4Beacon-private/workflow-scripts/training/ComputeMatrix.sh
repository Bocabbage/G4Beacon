CONFIGFILE=$1
OUTPUT_PATH=.
SCRIPT_PATH=../../dataPreprocess

python ${SCRIPT_PATH}/computeMatrix.py --json ${CONFIGFILE} && 

# concat seq
cat minus.g4seqFirst.F0.1.ex1000.seq.csv plus.g4seqFirst.F0.1.ex1000.seq.csv > CATmp.g4seqFirst.F0.1.ex1000.seq.csv &&
cat minus_v.g4seqFirst.F0.1.ex1000.seq.csv plus_v.g4seqFirst.F0.1.ex1000.seq.csv > CATmp_v.g4seqFirst.F0.1.ex1000.seq.csv &&

# concat atac
cat minus.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv plus.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv > CATmp.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv &&
cat minus_v.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv plus_v.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv > CATmp_v.g4seqFirst.F0.1.ex1000.bin10.atacFeatures_signal.csv &&
