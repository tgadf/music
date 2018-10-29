#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 10:58:39 2017

@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
from fsio import setDir, isDir
    
###############################################################################
#
# Discog Basic Directories
#
###############################################################################
def getDiscogDir():
    if isDir("/Volumes/Music/Discog"):
        return "/Volumes/Music/Discog"
    else:
        return "/Users/tgadfort/Documents/music/Discog"
        
def getBaseDBDir():
    return setDir(getDiscogDir(), "base-db")

def getCollectionsDir():
    return setDir(getDiscogDir(), "collections")

def getCollectionsDBDir():
    return setDir(getDiscogDir(), "collections-db")

def getArtistsDir():
    return setDir(getDiscogDir(), "artists")

def getArtistsExtraDir():
    return setDir(getDiscogDir(), "artists-extra")

def getArtistsDBDir():
    return setDir(getDiscogDir(), "artists-db")

def getAlbumsDir():
    return setDir(getDiscogDir(), "albums")

def getAlbumsDBDir():
    return setDir(getDiscogDir(), "albums-db")

def getSearchDir():
    return setDir(getDiscogDir(), "search")

def getSearchArtistsDir():
    return setDir(getDiscogDir(), "search-artists")

def getSearchArtistsDBDir():
    return setDir(getDiscogDir(), "search-artists-db")

def getSpecialDir():
    return setDir(getDiscogDir(), "special")

def getArtistsSpecialDir():
    return setDir(getDiscogDir(), "artist-special")

def getMusicDir():
    return "/Users/tgadfort/Documents/music"
    
