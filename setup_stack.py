#!/usr/bin/env python 3.4.4
# -*- coding: latin-1 -*-
#-------------------------------------------------------------------------------
# Name:        setup
# Purpose:
#
# Author:      Olivier Appere
#
# Created:     06/03/2013
# Copyright:   (c) Olivier.Appere 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from distutils.core import setup
from glob import glob
import sys
sys.path.append("pycparser")

import py2exe
import os
#import subprocess
#import shutil
from conf import VERSION

newpath = r'result'
if not os.path.exists(newpath): os.makedirs(newpath)

def main():
    data_files = [("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT\*.*')),
                    ("img", glob(r'img\*.*')),
                    ("js", glob(r'js\*.*')),
					("css", glob(r'css\*.*')),
					("db", glob(r'db\*.*')),
                    ("template", glob(r'template\*.*')),
                    ("result", glob(r'result\*.*')),
                    ("actions", glob(r'actions\*.*')),
					("conf", glob(r'conf\*.*')),
                    ("bin", glob(r'bin\*.exe')),
                    ("doc", glob(r'doc\*.*')),
                    "ico_sys_desktop.ico",
                    "README.txt",
					"explain.txt",
                    "docid.db3",
                    "ig.db3"]
    setup(
        name="stack",
        version=VERSION,
        description="Application to measure stack depth in function call tree.",
        author="Olivier Appere",
        license="License GPL v3.0",
        data_files=data_files,
        options = {"py2exe": {
            #"skip_archive": True,
            #"bundle_files": 1,
            "includes": [
				'openpyxl',
				'pycparser'
            ],

            'dll_excludes': ['libgdk-win32-2.0-0.dll',
                             'libgobject-2.0-0.dll'],
            "packages": ["lxml"]} },
       # options = {"py2exe": {"compressed": 1, "optimize": 0, "bundle_files": 1, } },
        zipfile = None,
        windows=[{
            "script": "stack.py",
                "icon_resources":[{0, "ico_sys_desktop.ico"}]
        }]
    )
if __name__ == '__main__':
    main()
