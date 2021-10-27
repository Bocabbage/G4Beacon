#! usr/bin python
# -*- coding: utf-8 -*-
# Description: compute Matrix and convert it into CSV format [json-format input]
# Author: Zhuofan Zhang
# Update date: 2021/10/19
import os
import json
import random
import argparse
from commonUtils import run_shell_cmd


def join_path(firstpath, secondpath):
    try:
        path = os.path.join(firstpath, secondpath)
    except TypeError:
        path = None
    return path


def matrix_to_csv(imatFile: str, ocsvFile: str) -> None:
    r'''
        Convert deeptools-output matrix file to CSV format.
    '''
    with open(imatFile, 'r') as ifile:
        with open(ocsvFile, 'w+') as ofile:
            for i in range(3):
                # Ignore the header lines
                ifile.readline()

            for line in ifile.readlines():
                line = line.replace("nan", "0.0")
                line = line.replace("\t", ",")
                ofile.write(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=str)
    args = parser.parse_args()

    with open(args.json, 'r') as json_file:
        json_data = json.load(json_file)

    data_dir = json_data['data_dir']
    outcsv_dir = json_data['outcsv_dir']
    outplot_dir = json_data['outplot_dir']

    if os.path.isdir(outcsv_dir) is not True:
        os.makedirs(outcsv_dir)

    if os.path.isdir(outplot_dir) is not True:
        os.makedirs(outplot_dir)

    for config in json_data['config_list']:
        g4bed = os.path.join(data_dir, config['g4bed'])
        envbw = os.path.join(data_dir, config['envbw'])
        thread = config['thread']
        extend = config['extend']
        binsize = config['binsize']
        outcsv = os.path.join(outcsv_dir, config['outcsv'])
        outplot = os.path.join(outplot_dir, config['outplot'])

        rand_id = random.randint(0, 9280)
        tmp_file_plot = f"{rand_id}_forplot"
        tmp_file_mat = f"{rand_id}_matrix"

        run_shell_cmd((
            "computeMatrix reference-point "
            "--referencePoint \"center\" "
            f"-R {g4bed} -S {envbw} -p {thread} "
            f"-a {extend} -b {extend} -bs {binsize} "
            f"--outFileName  {tmp_file_plot} "
            f"--outFileNameMatrix {tmp_file_mat}"
        ))

        if outplot:
            run_shell_cmd((f"plotProfile -m {tmp_file_plot} "
                           f"-o {outplot} "
                           "--refPointLabel \"G4-center\" "))

        matrix_to_csv(tmp_file_mat, outcsv)
        run_shell_cmd(f"rm {tmp_file_plot} {tmp_file_mat}")
