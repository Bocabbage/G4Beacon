#! usr/bin python
# -*- coding: utf-8 -*-
# Description: provide shell-env support and other util-functions
# Author: Zhuofan Zhang
# Update date: 2021/12/20
import os
import stat
import subprocess


def isWritable(dirname):
    uid = os.geteuid()
    gid = os.getegid()
    s = os.stat(dirname)
    mode = s[stat.ST_MODE]
    return (
        ((s[stat.ST_UID] == uid) and (mode & stat.S_IWUSR)) or ((s[stat.ST_GID] == gid) and (mode & stat.S_IWGRP)) or (mode & stat.S_IWOTH)
    )


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
        print(f"Error occurs in cmd: {cmd}")
        print("STDERR OUTPUT:")
        print(stderr)
        return None, stderr

    return stdout, None
