#!/usr/bin/env python 2.7.3
# -*- coding: latin-1 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     06/03/2013
# Copyright:   (c) Olivier.Appere 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from distutils.core import setup
from glob import glob
import sys
#import _elementpath as DONTUSE
import py2exe
import os
import subprocess
import shutil

## si le fichier bundlepmw.py contient l'importation regsub (qui n'existe plus depuis la version 2.5 de Python)
## Vous pouvez sinon le faire à la main en remplaçant "regsub" par "re" et "gsub" par "sub"
fp = open(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py")
a = fp.read().replace("regsub", "re").replace("gsub", "sub")
fp.close()
ft = open(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py", "w")
ft.write(a)
ft.close()

## Création du fichier Pmw.py dans le répertoire courant
subprocess.call([sys.executable, sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py",
                 sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib"])
## On copie les 2 fichiers PmwBlt.py et PmwColor.py dans le répertoire courant
shutil.copyfile(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib/PmwBlt.py", "PmwBlt.py")
shutil.copyfile(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib/PmwColor.py", "PmwColor.py")

newpath = r'result'
if not os.path.exists(newpath): os.makedirs(newpath)

def main():
    data_files = [("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT\*.*')),
                    ("img", glob(r'img\*.*')),
                    ("doc", glob(r'doc\*.*')),
					("css", glob(r'css\*.*')),
                    ("js", glob(r'js\*.*')),
					("template", glob(r'template\*.*')),
                    "ico_sys_internet.ico",
                    "setup_easyig.py",
                    "ig.db3"]
    #setup(name="test",scripts=["test.py"],)
    setup(
        name="easyIG",
        version="0.3.0",
        description="Application to get IG.",
        author="Olivier Appere",
        license="License GPL v3.0",
        data_files=data_files,
        options = {"py2exe": {
            "includes": [
                'django.template.loaders.filesystem',
                'django.template.loaders.app_directories',
                'django.template.defaulttags',
                'django.template.defaultfilters',
                'django.template.loader_tags',
                'django.template.loader'
            ],
            "packages": ["lxml"]} },
       # options = {"py2exe": {"compressed": 1, "optimize": 0, "bundle_files": 1, } },
        zipfile = None,
        windows=[{
            "script": "get_ig_jquery.py",
                "icon_resources":[{0, "ico_sys_internet.ico"}]
        }]
    )
if __name__ == '__main__':
    main()
