#! usr/bin python
# -*- coding: utf-8 -*-
# Description: provide shell-env support
# Author: Zhuofan Zhang
# Update date: 2021/07/25
import os
import time
import logging
import functools
import subprocess


def running_log(logName="default.log"):
    r'''
        Log running info and save log-file at the dir
        where function was executed.
    '''
    logPath = os.path.join(os.getcwd(), logName)

    def log_dec(func):
        logging.basicConfig(
            filename=logPath,
            level=logging.INFO,
            format='%(levelname)s:%(asctime)s:\n%(message)s\n')

        @functools.wraps(func)
        def wrapper(*args, **kargs):
            try:
                startTime = time.time()
                result = func(*args, **kargs)
                endTime = time.time()
                runTime = endTime - startTime
                message = "{} finish in {:.2f}s.".format(func.__name__,
                                                         runTime)
                logging.info(message)

                return result
            except Exception as e:
                message = "{} Error happened.\n**{}**".format(func.__name__, e)
                logging.error(message)
                # exit(-1)
        return wrapper
    return log_dec


# Here for test running_log decorator:
# @running_log()
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
