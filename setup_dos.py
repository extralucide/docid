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
import docx
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
                    ("template", glob(r'template\*.*')),
                    ("result", glob(r'result\*.*')),
                    "qams.ico",
                    "docid.ini",
					"standards.csv",
                    "descr_docs.csv",
					"glossary.csv",					
                    "func_chg.txt",
                    "oper_chg.txt",
                    "setup.py",
                    "README.txt",
					"explain.txt",
					"explain_sci.txt",
					"explain_hcmr_pld.txt",
					"pld_checklist.db3",
					"sw_checklist.db3",					
                    "docid.db3"]
    #setup(name="test",scripts=["test.py"],)
    setup(
        name="docid_cli",
        version="1.0",
        description="Application to generate HCMR.",
        author="Olivier Appere",
        license="License GPL v3.0",
        data_files=data_files,
        options = {"py2exe": {"includes": "docx","packages": "lxml", } },
       # options = {"py2exe": {"compressed": 1, "optimize": 0, "bundle_files": 1, } },
        zipfile = None,
        console=[{
            "script": "docid.py",
                "icon_resources":[{0, "qams.ico"}]
        }]
    )
if __name__ == '__main__':
    main()
