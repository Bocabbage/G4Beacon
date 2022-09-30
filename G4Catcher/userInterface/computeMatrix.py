#! usr/bin python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2022/09/25
import random
import json
import argparse
from commonUtils import run_shell_cmd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--extend', type=int, default=1000, help="extended size.")
    parser.add_argument('--binsize', type=int, default=10, help="bin-window size.")

    parser.add_argument('-p', type=int, default=1, help="thread-nums.")
    parser.add_argument('--g4Input', type=str, help="g4seq file (origin-BED) input.")
    parser.add_argument('--envInput', type=str, help="env file (bigwig) input.")
    parser.add_argument('--csvOutput', type=str, help="Ouput env-feature csv path.")

    args = parser.parse_args()


#### Tmp json-file generation
    currConfig = {
        "name": None,
        "g4bed": args.g4Input,
        "envbw": args.envInput,
        "outcsv": args.csvOutput,
        "outplot": None,
        "thread": args.p,
        "extend": args.extend,
        "binsize": args.binsize
    }
    configList = [currConfig]

    jsonConfig = {
        "annotation": None,
        "outplot_dir": None,
        "data_dir": "",
        "outcsv_dir": "",
        "outplot_dir": None,
        "config_list": [currConfig]
    }

    randId = random.randint(0, 4000)
    tmpJsonFile = f"./{randId}tmp.compute-Matrix-config.json"

    jsonObj = json.dumps(jsonConfig, indent=4)
    with open(tmpJsonFile, 'w+') as jsonFile:
        jsonFile.write(jsonObj)

#### Do the real procession
    run_shell_cmd(f"python ../dataPreprocess/computeMatrix.py --json {tmpJsonFile}")

#### Remove the tmp config file
    run_shell_cmd(f"rm {tmpJsonFile}")
