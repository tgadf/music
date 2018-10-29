#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 20:26:48 2017

@author: tgadfort
"""


from os.path import basename, splitext, dirname, getsize
import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    


###############################################################################
#
# General (get/save)
#
###############################################################################
def getBasename(ifile):
    bname = basename(ifile)
    return bname

def getDirname(ifile):
    dname = dirname(ifile)
    return dname

def getBaseFilename(ifile):
    bfname = splitext(getBasename(ifile))[0]
    return bfname

def getExt(ifile):
    ext = splitext(getBasename(ifile))[1]
    return ext

def getFileBasics(ifile):
    return getDirname(ifile),getBaseFilename(ifile),getExt(ifile)    





###############################################################################
#
# File Data
#
###############################################################################
def getSize(ifile, unit = "kB", debug = False):
    if unit == "B":
        size = getsize(ifile)
    elif unit == "kB":
        size = getsize(ifile)/1e3
    elif unit == "MB":
        size = getsize(ifile)/1e6
    elif unit == "GB":
        size = getsize(ifile)/1e9
    else:
        raise ValueError("Didn't understand unit:",unit)

    size = round(size, 3)
    if debug:
        print "File:",ifile,"is",size,unit+"."

    return size