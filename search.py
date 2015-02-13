#!/usr/bin/env python 2.7.3
# -*- coding: latin-1 -*-
__author__ = 'olivier'
import re
import sys
import argparse

if __name__ == '__main__':
    # command line option ?
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="file to get version")
    args = parser.parse_args()
    #import os, sys
    #print 'Mon Rep de Travail: ', os.getcwd()
    #print 'Chemin deRecherche', sys.path

    if args.filename:
        filename = args.filename
        file = open(filename, 'r')
        txt = file.read(100)
        print txt
        m = re.match(r'^__version__ = "rev ([0-9])\.([0-9])\.([0-9])"',txt)
        if m:
            version = m.group(1)
            revision = m.group(2)
            minor = m.group(3)
            print version,revision,minor
        file.close()