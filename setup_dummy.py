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
import py2exe

def main():
    setup(
		console=['stack.py'],
		options={"py2exe": {
			"excludes": ["six.moves.urllib.parse","mf3"]}}
		)

if __name__ == '__main__':
    main()
