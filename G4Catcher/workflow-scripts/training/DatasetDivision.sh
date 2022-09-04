CONFIGFILE=$1
SCRIPT_PATH=../../dataPreprocess


python ${SCRIPT_PATH}/fullDataset_sampling.py --json ${CONFIGFILE}
