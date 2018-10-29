# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 20:48:27 2017

@author: tgadfort
"""


from glob import glob
from os.path import join, isdir, isfile, exists, basename, dirname, splitext
from os import mkdir


def splitFilename(ifile):
    if ifile:
        bname     = basename(ifile)
        bname,ext = splitext(bname)
        dname     = dirname(ifile)
        return dname,bname,ext
    return None,None,None


def mkDir(fdir, debug = False):
    if exists(fdir):
        if debug:
            print "Exists",fdir
        return fdir
    else:
        if debug:
            print "Making",fdir
        mkdir(fdir)
        return fdir
            

def mkBaseDir(base, tmpdir, debug = False):
    if isinstance(tmpdir, str):
        fdir = join(base, tmpdir)
        mkDir(fdir, debug)
        return fdir
    elif isinstance(tmpdir, list):
        fdir = base
        mkDir(base, debug)
        for tmp in tmpdir:
            fdir = join(fdir, tmp)
            mkDir(fdir, debug)
        if debug: print "--->",fdir
        return fdir
    else:
        print "Unknown type for",tmpdir
        raise()
    

def getDirs(dbdir):
    dirs  = [x for x in glob(join(dbdir, "*")) if isdir(x)]
    return dirs
    
def getFiles(dbdir, pattern = None, filetype = None):
    if filetype:
        if pattern:
            print pattern
            files  = [x for x in glob(join(dbdir, "*"+pattern+"*"+"."+filetype)) if isfile(x)]
        else:
            files  = [x for x in glob(join(dbdir, "*"+"."+filetype)) if isfile(x)]
    else:
        if pattern:
            print pattern
            files  = [x for x in glob(join(dbdir, "*"+pattern+"*")) if isfile(x)]
        else:
            files  = [x for x in glob(join(dbdir, "*")) if isfile(x)]
    return files

