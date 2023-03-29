# -*- coding: utf-8 -*-
# Update date: 2023/03/29
# Author: Zhuofan Zhang
import os
import shutil
import re
from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts


class InstallScripts(install_scripts):

    def run(self):
        install_scripts.run(self)

        for script in self.get_outputs():
            if os.path.basename(script)[:-3] == '.py':
                dst = script[:-3]
            else:
                continue
            print("moving %s to %s" % (script, dst))
            shutil.move(script, dst)


def getVersion():
    try:
        version_file = open("G4Beacon/_version.py")
    except EnvironmentError:
        return None
    for line in version_file.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None


setup(
    name='G4Beacon',
    version=getVersion(),
    author="Zhuofan Zhang, Rongxin Zhang, Ke Xiao, Xiao Sun",
    author_email="zhangzhuofan97@gmail.com",
    packages=find_packages(),
    scripts=['bin/g4beacon.py'],
    description="In-vivo G4 prediction tool taking seq+atac features as input.",
    url="https://github.com/Bocabbage/G4Beacon",
    install_requires=[
        "numpy >= 1.21.2",
        "pandas >= 1.3.5",
        "imbalanced-learn >= 0.8.1",
        "scikit-learn >= 1.0.1",
        "lightgbm >= 3.2.1"
    ],
    python_requires=">=3.9",
    cmdclass={"install_scripts": InstallScripts}
)
