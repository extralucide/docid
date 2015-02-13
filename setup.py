#!/usr/bin/env python 2.7.3
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
sys.path.append("python-docx")
sys.path.append("tkintertable")
import docid
import docx
#import _elementpath as DONTUSE
import py2exe
import os
import subprocess
import shutil
from conf import VERSION
import django
print "Version Django used:",django.__version__
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
                    ("js", glob(r'js\*.*')),
					("css", glob(r'css\*.*')),
                    ("template", glob(r'template\*.*')),
                    ("result", glob(r'result\*.*')),
                    ("actions", glob(r'actions\*.*')),
					("conf", glob(r'conf\*.*')),
                    ("doc", glob(r'doc\*.*')),
                    "ico_sys_desktop.ico",
                    "README.txt",
                    "CHANGE_LOG.txt",
					"explain.txt",
                    "default_checklists_db.db3",
                    "eqpt_checklist.db3",
                    "board_checklist.db3",
					"pld_checklist.db3",
					"sw_checklist.db3",
                    "docid.db3",
                    "ig.db3"]
    # Save matplotlib-data to mpl-data ( It is located in the matplotlib\mpl-data
    # folder and the compiled programs will look for it in \mpl-data
    # note: using matplotlib.get_mpldata_info
    import matplotlib
    data_files.extend(matplotlib.get_py2exe_datafiles())
    #print "get_py2exe_datafiles",matplotlib.get_py2exe_datafiles()
#    data_files.extend([
#        (r'mpl-data', glob(sys.prefix + os.sep + "Lib\site-packages\matplotlib\mpl-data\*.*")),
    # Because matplotlibrc does not have an extension, glob does not find it (at least I think that's why)
    # So add it manually here:
#    (r'mpl-data', glob(sys.prefix + os.sep + "Lib\site-packages\matplotlib\mpl-data\matplotlibrc")),
#    (r'mpl-data\images',glob(sys.prefix + os.sep + "Lib\site-packages\matplotlib\mpl-data\images\*.*")),
#    (r'mpl-data\fonts',glob(sys.prefix + os.sep + "Lib\site-packages\matplotlib\mpl-data\fonts\*.*"))])
    #setup(name="test",scripts=["test.py"],)
    setup(
        name="docid",
        version=VERSION,
        description="Application to generate CID and CCB minutes report.",
        author="Olivier Appere",
        license="License GPL v3.0",
        data_files=data_files,
        options = {"py2exe": {
            "includes": [
                'docx',
                'django.template.loaders.filesystem',
                'django.template.loaders.app_directories',
                'django.template.defaulttags',
                'django.template.defaultfilters',
                'django.template.loader_tags',
                'django.template.loader',
                'django.apps',
                'matplotlib.backends',
                'matplotlib.figure',
                'matplotlib.pyplot',
                'matplotlib.backends.backend_cairo'
#                "numpy"
#                 "matplotlib.backends.backend_cairo",
#                 "matplotlib.backends.backend_tkagg",
            ],
            #'excludes': ['_tkagg'],
                #,'_gtkagg',

#                         '_agg2',
#                         '_cairo',
#                         '_cocoaagg',
#                         '_fltkagg',
#                         '_gtk',
#                         '_gtkcairo' ],
            'dll_excludes': ['libgdk-win32-2.0-0.dll',
                             'libgobject-2.0-0.dll'],
            "packages": ["lxml"]} },
       # options = {"py2exe": {"compressed": 1, "optimize": 0, "bundle_files": 1, } },
        zipfile = None,
        windows=[{
            "script": "docid.py",
                "icon_resources":[{0, "ico_sys_desktop.ico"}]
        }]
    )
if __name__ == '__main__':
    main()
