#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 21:11:30 2017

@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
from fsio import setDir, isDir, getPath
    
###############################################################################
#
# Music Directories
#
###############################################################################
def getMusicDir():
    if isDir("/Volumes/Music/"):
        return "/Volumes/Music/"
    else:
        return "/Users/tgadfort/Documents/music/"
        
def getiTunesDir():
    dirval = None
    if isDir("/Volumes/Music/"):
        dirval = "/Volumes/Music/"
    elif isDir("/Users/tgadfort/Documents/music/"):
        dirval = "/Users/tgadfort/Documents/music/"
    return(getPath(dirval))

def getMusicDBDir():
    dbdir = setDir(getiTunesDir(), "MusicDB")
    return dbdir

def getConsolidateDir():
    dbdir = setDir(getiTunesDir(), "iTunes Consolidate")
    return dbdir
