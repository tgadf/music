#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 15:47:03 2017

@author: tgadfort
"""

from os.path import join, splitext
from glob import glob, glob1
from os import listdir, walk
from difflib import get_close_matches, SequenceMatcher

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fsio import setSubDir, removeFiles, isdir

###############################################################################
#
# Find Files
#
###############################################################################
def findExt(basedir, ext, debug = False):
    if basedir == None: return []
    if isinstance(ext, list):
        if debug: print "  findExt("+basedir+", ext="+",".join(ext)+")"
        files = []
        for exten in ext:
            #files += [x for x in listdir(basedir) if splitext(x)[1] == exten]
            files += [join(basedir,x) for x in glob1(basedir, "*"+exten)]
        if debug: print "  findExt("+basedir+", ext="+",".join(ext)+"): "+str(len(files))
    else:
        if debug: print "  findExt("+basedir+", ext="+ext+")"
        files = [join(basedir,x) for x in glob1(basedir, "*"+ext)]
        #files = glob1(basedir, "*"+exten)
        #files = [x for x in listdir(basedir) if splitext(x)[1] == ext]
        #files = [x for x in listdir(basedir) if splitext(x)[1] == ext]
        if debug: print "  findExt("+basedir+", ext="+ext+"): "+str(len(files))
    return files
    
def findPattern(basedir, pattern, debug = False):
    if basedir == None: return []
    if debug: print "  findPattern("+basedir+", pattern="+pattern+")"
    files = [x for x in listdir(basedir) if x.find(pattern) != -1]
    files = glob(join(basedir, "*"+pattern+"*"))
    if debug: print "  findPattern("+basedir+", pattern="+pattern+"): "+str(len(files))
    return files
    
def findPatternExt(basedir, pattern, ext, debug = False):
    if basedir == None: return []
    if debug: print "  findPatternExt("+basedir+", pattern="+pattern+", ext="+ext+")"
    files = findExt(basedir, ext)
    files = [x for x in files if x.find(pattern) != -1]
    if debug: print "  findPatternExt("+basedir+", pattern="+pattern+", ext="+ext+"): "+str(len(files))
    return files
    
def find(basedir, pattern, debug = False):
    if basedir == None: return []
    if debug: print "  find("+basedir+", pattern="+pattern+")"
    files = glob(join(basedir, "*"+pattern+"*"))
    if debug: print "  find("+basedir+", pattern="+pattern+"): "+str(len(files))
    return files
    
def findAll(basedir, debug = False):
    if basedir == None: return []
    if debug: print "  findAll("+basedir+")"
    files = glob(join(basedir, "*"))
    if debug: print "  findAll("+basedir+"): "+str(len(files))
    return files

def findSubPattern(basedir, subdirs, pattern, debug = False):
    forceExist = False
    sdfile = setSubDir(basedir, subdirs, forceExist, debug)
    return findPattern(sdfile, pattern, debug)

def findSubExt(basedir, subdirs, ext, debug = False):
    forceExist = False
    sdfile = setSubDir(basedir, subdirs, forceExist, debug)
    return findExt(sdfile, ext, debug)

def findWalkExt(basedir, ext, debug = False):
    retvals = []
    if debug: print "  findWalkExt("+basedir+", ext="+",".join(ext)+")"
    for rootdir,dirvals,files in walk(basedir):
        if len(files) == 0: continue
        if debug:
            print "    -->",rootdir
        if isinstance(ext, list):
            for exten in ext:
                retvals += [join(rootdir,x) for x in files if splitext(x)[1] == exten]
        else:
            retvals += [join(rootdir,x) for x in files if splitext(x)[1] == ext]

    if debug: print "  findWalkExt("+basedir+", ext="+",".join(ext)+"): "+str(len(retvals))
    return retvals

def findWalkPattern(basedir, pattern, debug = False):
    retvals = []
    if debug: print "  findWalkPattern("+basedir+", pattern="+",".join(pattern)+")"
    for rootdir,dirvals,files in walk(basedir):
        if len(files) == 0: continue
        if debug:
            print "    -->",rootdir
        if isinstance(pattern, list):
            for pat in pattern:
                retvals += [join(rootdir,x) for x in files if x.find(pat) != -1]
        else:
            retvals += [join(rootdir,x) for x in files if x.find(pattern) != -1]

    if debug: print "  findWalkPattern("+basedir+", pattern="+",".join(pattern)+"): "+str(len(retvals))
    return retvals

def findWalkPatternExt(basedir, pattern, ext, debug = False):
    retvals = []
    if debug: print "  findWalkPattern("+basedir+", pattern="+",".join(pattern)+")"
    for rootdir,dirvals,files in walk(basedir):
        if len(files) == 0: continue
        if debug:
            print "    -->",rootdir
        if isinstance(ext, list):
            for exten in ext:
                retvals += [join(rootdir,x) for x in files if x.find(pattern) != -1 and splitext(x)[1] == exten]
        else:
            retvals += [join(rootdir,x) for x in files if x.find(pattern) != -1 and splitext(x)[1] == ext]
            
    if debug: print "  findWalkPattern("+basedir+", pattern="+",".join(pattern)+"): "+str(len(retvals))
    return retvals

def findSubPatternExt(basedir, subdirs, pattern, ext, debug = False):
    forceExist = False
    sdfile = setSubDir(basedir, subdirs, forceExist, debug)
    return findPatternExt(sdfile, pattern, ext, debug)

    
def findDirs(basedir, debug = False):
    if basedir == None: return []
    if debug: print "  findDirs("+basedir+")"
    dirs = [x for x in glob(join(basedir, "*")) if isdir(x)]
    if debug: print "  findDirs("+basedir+"): "+str(len(dirs))
    return dirs
    
def findDirsPattern(basedir, pattern, debug = False):
    if basedir == None: return []
    if debug: print "  findDirsPattern("+basedir+", pattern="+pattern+")"
    dirs = [x for x in glob(join(basedir, "*"+pattern+"*")) if isdir(x)]
    if debug: print "  findDirsPattern("+basedir+", pattern="+pattern+"): "+str(len(dirs))
    return dirs
    
def findSubDirs(basedir, subdirs, debug = False):
    forceExist = False
    subdir = setSubDir(basedir, subdirs, forceExist, debug)
    return findDirs(subdir, debug)
    
def findSubDirsPattern(basedir, subdirs, pattern, debug = False):
    forceExist = False
    subdir = setSubDir(basedir, subdirs, forceExist, debug)
    return findDirsPattern(subdir, pattern, debug)



###############################################################################
#
# Find Matches
#
###############################################################################
def findNearest(item, ilist, num, cutoff, debug = False):
    nearest = get_close_matches(item, ilist, n=num, cutoff=cutoff)
    return nearest

def findMatchingWord(item, ilist, num=None, cutoff=None, debug = False):
    nearest = [x for x in ilist if x.find(item) != -1]
    return nearest

def findSimilarity(base, item, debug = False):
    s = SequenceMatcher(None, base, item)
    return s.ratio()


###############################################################################
#
# Remove Pattern Matches
#
###############################################################################
def removePattern(basedir, pattern, debug = False):
    files = find(basedir, pattern)
    removeFiles(files, debug)

def removeSubExt(basedir, subdirs, ext, debug = False):
    files = findSubExt(basedir, subdirs, ext)
    removeFiles(files, debug)

def removeSubPattern(basedir, subdirs, pattern, debug = False):
    files = findSubExt(basedir, subdirs, pattern)
    removeFiles(files, debug)
