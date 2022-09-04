CONFIGFILE=$1
SCRIPT_PATH=../../prediction

# pos-sample oversampling


python ${SCRIPT_PATH}/train.py --json ${CONFIGFILE}