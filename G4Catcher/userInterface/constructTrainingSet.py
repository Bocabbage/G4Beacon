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
    parser.add_argument('--outdir', type=str, default="./", help="output file dir.")

    args = parser.parse_args()


#### Tmp json-file generation
    currConfig = {
        "mode": "over",
        "pos_shuffle_list": None,
        "neg_shuffle_list": None,
        "seed": 42,
        "out_dir": args.outdir
    }
    configList = [currConfig]

    jsonConfig = {
        "origin_data_dir": "",
        "origin_data":
        {
            "pos_seq": args.vg4seqCSV,
            "neg_seq": args.ug4seqCSV,
            "pos_atac": args.vg4atacCSV,
            "neg_atac": args.ug4atacCSV
        },
        "config_lists": configList
    }

    randId = random.randint(0, 4000)
    tmpJsonFile = f"./{randId}tmp.datasetDivision-config.json"

    jsonObj = json.dump(jsonConfig, indent=4)
    with open(tmpJsonFile, 'w+') as jsonFile:
        jsonFile.write(jsonObj)

#### Do the real procession
    run_shell_cmd(f"python ../dataPreProcess/fullDataset_sampling.py --json {tmpJsonFile}")

#### Remove the tmp config file
    run_shell_cmd(f"rm {tmpJsonFile}")
