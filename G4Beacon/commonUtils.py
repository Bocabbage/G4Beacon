#! usr/bin python
# -*- coding: utf-8 -*-
# Description: provide shell-env support and other util-functions
# Author: Zhuofan Zhang
# Update date: 2021/12/20
import os
import time
import logging
import functools
import subprocess


def joinPath(firstpath, secondpath):
    try:
        path = os.path.join(firstpath, secondpath)
    except TypeError:
        path = None
    return path


def runShellCmd(cmd):
    r'''
        Run cmd in bash-env.
    '''
    p = subprocess.Popen(
        ['bash', '-o', 'pipefail'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True,
    )
    # p.wait()
    stdout, stderr = [x.decode('utf-8') for x in p.communicate(bytes(cmd, 'utf-8'))]
    if stderr:
        print("Error occurs in cmd: {}".format(cmd))
        print("STDERR OUTPUT:")
        print(stderr)
        exit(-1)

    return stdout, stderr
