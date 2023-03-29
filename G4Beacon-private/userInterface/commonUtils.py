#! usr/bin python
# -*- coding: utf-8 -*-
# Description: provide shell-env support and other util-functions
# Author: Zhuofan Zhang
# Update date: 2021/12/20
import os
import subprocess


def join_path(firstpath, secondpath):
    try:
        path = os.path.join(firstpath, secondpath)
    except TypeError:
        path = None
    return path


def run_shell_cmd(cmd):
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
        # exit(-1)

    return stdout, stderr


if __name__ == '__main__':

    # run_shell_cmd TEST
    stdOut, _ = run_shell_cmd(
        r'echo "Hello" > test.txt; echo "Also for you!"'
    )
    print(stdOut)
    stdOut, stdErr = run_shell_cmd('awk \'{print "file echo: ", $0}\' test.txt')
    print(stdOut)
    run_shell_cmd(r'rm test.txt')
