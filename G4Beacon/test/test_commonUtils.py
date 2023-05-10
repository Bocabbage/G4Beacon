#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/05/10
from io import StringIO
from unittest import TestCase
from unittest import main as u_main
from unittest.mock import patch
from ..commonUtils import runShellCmd


class TestRunShellCmd(TestCase):
    def test_correct(self):
        cmd = r"echo 'Hello'"
        expected_out = "Hello\n"
        out, err = runShellCmd(cmd)
        self.assertEqual(out, expected_out)
        self.assertIsNone(err)

    def test_error(self):
        cmd = r"echohhhhhhhh 'Hello'"
        expected_err = "bash: line 1: echohhhhhhhh: command not found\n"
        expected_stdout = '''Error occurs in cmd: echohhhhhhhh 'Hello'
STDERR OUTPUT:
bash: line 1: echohhhhhhhh: command not found\n
'''

        with patch('sys.stdout', new=StringIO()) as fake_out:
            _, err = runShellCmd(cmd)
            self.assertEqual(fake_out.getvalue(), expected_stdout)
            self.assertEqual(err, expected_err)


# class TestIsWritable(TestCase):
#     pass


if __name__ == '__main__':
    u_main()
