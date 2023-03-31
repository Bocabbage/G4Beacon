# -*- coding: utf-8 -*-
# Update date: 2023/03/30
# Author: Zhuofan Zhang
import os
import shutil
import re
from setuptools import setup, find_packages
# from setuptools.command.install_scripts import install_scripts
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist


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


class install(_install):
    def run(self):
        self.distribution.metadata.version = getVersion()
        _install.run(self)
        return


class sdist(_sdist):

    def run(self):
        self.distribution.metadata.version = getVersion()
        return _sdist.run(self)


setup(
    name='G4beacon',
    version=getVersion(),
    author="Zhuofan Zhang, Rongxin Zhang, Ke Xiao, Xiao Sun",
    author_email="zhangzhuofan97@gmail.com",
    packages=find_packages(),
    package_data={"": ["models/*.joblib"]},
    scripts=['bin/g4beacon'],
    description="In-vivo G4 prediction tool taking seq+atac features as input.",
    url="https://github.com/Bocabbage/G4Beacon",
    install_requires=[
        "numpy >= 1.21.2",
        "pandas >= 1.3.5",
        "imbalanced-learn >= 0.8.1",
        "scikit-learn >= 1.0.1",
        "lightgbm >= 3.2.1",
        "biopython >= 1.79"
    ],
    include_package_data=True,
    python_requires=">=3.9",
    cmdclass={"install": install, "sdist": sdist}
)
