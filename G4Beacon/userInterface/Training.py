#! usr/bin python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2022/09/27
import random
import json
import argparse
from commonUtils import run_shell_cmd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vg4seqCSV', type=str, help="Positive seq feature file path (CSV).")
    parser.add_argument('--ug4seqCSV', type=str, help="Negative seq feature file path (CSV).")
    parser.add_argument('--vg4atacCSV', type=str, help="Positive atac feature file path (CSV).")
    parser.add_argument('--ug4atacCSV', type=str, help="Negative atac feature file path (CSV).")
    parser.add_argument('--oname', type=str, help="result output trained-model (JOBLIB).")
    parser.add_argument('--outdir', type=str, default="./", help="output file dir.")
    parser.add_argument('--norm', action="store_true", default=False, help="Apply normalization on ATAC-features.")

    args = parser.parse_args()


#### Tmp json-file generation
    currConfig = {
        "name": args.oname,
        "vg4seq": args.vg4seqCSV,
        "ug4seq": args.ug4seqCSV,
        "vg4atac": args.vg4atacCSV,
        "ug4atac": args.ug4atacCSV,
        "vg4atac-fd": None,
        "ug4atac-fd": None,
        "vg4bs": None,
        "ug4bs": None,
        "model": "lightGBM",
        "model_config":
        {
            "seed": 42,
            "learning_rate": 0.1,
            "n_estimators": 1000,
            "objective": "binary"
        },
        "normalization": args.norm
    }

    jsonConfig = {
        "dataset_dir": "",
        "out_dir": args.outdir,
        "config_list": [currConfig]
    }

    randId = random.randint(0, 4000)
    tmpJsonFile = f"./{randId}tmp.training-config.json"

    jsonObj = json.dumps(jsonConfig, indent=4)
    with open(tmpJsonFile, 'w+') as jsonFile:
        jsonFile.write(jsonObj)

#### Do the real procession
    run_shell_cmd(f"python ../prediction/train.py --json {tmpJsonFile}")

#### Remove the tmp config file
    run_shell_cmd(f"rm {tmpJsonFile}")
