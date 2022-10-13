#! usr/bin python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2022/09/27
import os
import random
import json
import argparse
from commonUtils import run_shell_cmd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seqCSV', type=str, help="Seq feature file path (CSV).")
    parser.add_argument('--atacCSV', type=str, help="Atac feature file path (CSV).")
    parser.add_argument('--originBED', type=str, help="origin-bed file generated from the pre-process step.")
    parser.add_argument('--model', type=str, help="Trained G4Catcher model file (checkpoint, JOBLIB).")
    parser.add_argument('-o', type=str, help="result output path (BED).")
    parser.add_argument('--norm', type=str, default="False")

    args = parser.parse_args()


#### Tmp json-file generation
    norm = bool(args.norm == "True")
    if norm:
        print("[Info] Normalization: True")

    currConfig = {
        "name": None,
        "vg4seq": args.seqCSV,
        "ug4seq": None,
        "vg4atac": args.atacCSV,
        "ug4atac": None,
        "vg4atac-fd": None,
        "ug4atac-fd": None,
        "vg4bs": None,
        "ug4bs": None,
        "origin-bed": args.originBED,
        "result-file": args.o,
        "checkpoint": args.model,
        "model": "lightGBM",
        "normalization": norm
    }
    configList = currConfig

    jsonConfig = {
        "predict-name": None,
        "tfn-tpn": None,
        "dataset_dir": "",
        "out_dir": "",
        "data_list": [configList]
    }

    randId = random.randint(0, 4000)
    basename = os.path.basename(args.seqCSV)
    tmpJsonFile = f"./{randId}tmp.{basename}.getActiveG4s-config.json"

    jsonObj = json.dumps(jsonConfig, indent=4)
    with open(tmpJsonFile, 'w+') as jsonFile:
        jsonFile.write(jsonObj)

#### Do the real procession
    run_shell_cmd(f"python ../prediction/getActiveG4s.py --json {tmpJsonFile}")

#### Remove the tmp config file
    run_shell_cmd(f"rm {tmpJsonFile}")
