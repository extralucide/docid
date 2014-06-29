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
sys.path.append("python-docx")
sys.path.append("tkintertable")
import docx
#import _elementpath as DONTUSE
import py2exe
import os
import subprocess
import shutil

## si le fichier bundlepmw.py contient l'importation regsub (qui n'existe plus depuis la version 2.5 de Python)
## Vous pouvez sinon le faire � la main en rempla�ant "regsub" par "re" et "gsub" par "sub"
fp = open(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py")
a = fp.read().replace("regsub", "re").replace("gsub", "sub")
fp.close()
ft = open(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py", "w")
ft.write(a)
ft.close()

## Cr�ation du fichier Pmw.py dans le r�pertoire courant
subprocess.call([sys.executable, sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/bin/bundlepmw.py",
                 sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib"])
## On copie les 2 fichiers PmwBlt.py et PmwColor.py dans le r�pertoire courant
shutil.copyfile(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib/PmwBlt.py", "PmwBlt.py")
shutil.copyfile(sys.prefix + os.sep + "Lib/site-packages/Pmw/Pmw_1_3_3/lib/PmwColor.py", "PmwColor.py")

newpath = r'result'
if not os.path.exists(newpath): os.makedirs(newpath)

def main():
    data_files = [("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT\*.*')),
                    ("img", glob(r'img\*.*')),
                    ("template", glob(r'template\*.*')),
                    ("result", glob(r'result\*.*')),
                    "qams.ico",
                    "docid.ini",
					"standards.csv",
                    "descr_docs.csv",
                    "func_chg.txt",
                    "oper_chg.txt",
                    "setup.py",
                    "README.txt",
                    "docid.db3"]
    #setup(name="test",scripts=["test.py"],)
    setup(
        name="docid",
        version="2.5.3",
        description="Application to generate CID and CCB minutes report.",
        author="Olivier Appere",
        license="License GPL v3.0",
        data_files=data_files,
        options = {"py2exe": {"includes": "docx","packages": "lxml", } },
       # options = {"py2exe": {"compressed": 1, "optimize": 0, "bundle_files": 1, } },
        zipfile = None,
        windows=[{
            "script": "docid.py",
                "icon_resources":[{0, "qams.ico"}]
        }]
    )
if __name__ == '__main__':
    main()
