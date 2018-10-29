#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 18:23:14 2017

@author: tgadfort
"""

import unicodedata
import sys
from hashlib import md5
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from search import findSubPattern
from fileio import getBaseFilename, get
from htmlParser import getHTML
from artistdata import parse
from strops import makeUnicode, makeStrFromUnicode

def getHashVal(name):
    m = md5()
    m.update(name)
    retval = m.hexdigest()
    return retval

basedir = "/Volumes/Music/Discog/artist"
files = findSubPattern(basedir, "98", pattern="Dionne")
try:
    ifile = files[0]
except:
    raise ValueError("No ifile!")

debug = False
name = getBaseFilename(ifile)
name = name.split('-')[0]
print name
print getHashVal(name)
sname = makeStrFromUnicode(name)
print sname
print getHashVal(sname)


#print getHashVal(name)
#print getHashVal(unicodedata.normalize('NFC', makeUnicode(name)).encode('utf-8'))
#print getHashVal(unicodedata.normalize('NFD', makeUnicode(name)).encode('utf-8'))

bsdata         = getHTML(get(ifile))
artistData     = parse(bsdata, debug)

artist = artistData["Artist"]
sArtist = makeStrFromUnicode(artist)
print sArtist
print getHashVal(sArtist)
#artist = artist.encode('utf-8')
#print getHashVal(artist)
#print getHashVal(unicodedata.normalize('NFC', makeUnicode(artist)).encode('utf-8'))
#print getHashVal(unicodedata.normalize('NFD', makeUnicode(artist)).encode('utf-8'))

