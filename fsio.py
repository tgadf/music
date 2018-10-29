#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 20:24:29 2017

@author: tgadfort
"""


from os.path import exists, join, isdir, isfile, normpath
from os import remove, mkdir, access, W_OK, rmdir
from shutil import move, copy

###############################################################################
#
# Directory and Files
#
###############################################################################
def setSubDir(basedir, subdirs, forceExist = True, debug = False):
    if not isdir(basedir):
        if forceExist:
            raise ValueError("Basedir",basedir,"does not exist.")
        else:
            return None
    dirval = basedir
    if isinstance(subdirs, list):
        for sdir in subdirs:
            dirval = setDir(dirval, sdir, forceExist, debug)
    else:
        dirval = setDir(dirval, subdirs, forceExist, debug)
    return dirval

    
def setDir(basedir, subdir, forceExist = True, debug = False):
    if not isdir(basedir):
        if forceExist:
            raise ValueError("Basedir",basedir,"does not exist.")
        else:
            return None
    sdfile = join(basedir, subdir)
    return sdfile


def setSubDirFile(basedir, subdirs, filename, forceExist = False, debug = False):
    sdfile = setSubDir(basedir, subdirs, forceExist, debug)
    sdfile = setFile(sdfile, filename, forceExist, debug)
    return sdfile


def setSubFile(basedir, subdirs, filename, forceExist = False, debug = False):
    return setSubDirFile(basedir, subdirs, filename, forceExist, debug)

    
def setFile(basedir, filename, forceExist = False, debug = False):
    if not isdir(basedir):
        if forceExist:
            raise ValueError("Basedir",basedir,"does not exist.")
        else:
            return None
    sdfile = join(basedir, filename)
    if forceExist and not exists(sdfile):
        raise ValueError("File",sdfile,"does not exist.")        
    return sdfile

 
       
###############################################################################
#
# Create Directory
#
###############################################################################
def mkSubDir(basedir, subdirs, debug = False):
    forceExist = True
    dirval = basedir
    if isinstance(subdirs, list):
        for subdir in subdirs:
            dirval = mkDir(setDir(dirval, subdir, forceExist, debug))
    else:
        dirval = mkDir(setDir(dirval, subdirs, forceExist, debug))
        
    return dirval

    
def mkDir(dirval, debug = False):
    if isdir(dirval):
        if debug:
            print "Can not create directory",dirval,". Already exists."
        return dirval
    if debug:
        print "Creating",dirval
    mkdir(dirval)
    return dirval

 

###############################################################################
#
# Get OS-independent path name
#
###############################################################################    
def getPath(dirval):
    return normpath(dirval)


       
###############################################################################
#
# File/Directory Data
#
###############################################################################
def isFile(filename, debug = False):
    if isfile(filename):
        return True
    return False


def isDir(dirval, debug = False):
    if isdir(dirval):
        return True
    return False

 
       
###############################################################################
#
# Directory Properties
#
###############################################################################
def isWriteable(dirval):
    return access(dirval, W_OK)    



###############################################################################
#
# Remove
#
###############################################################################
def removeFiles(files, debug = False):
    if debug: print "Removing these files:",files
    for ifile in files:
        removeFile(ifile, debug)



###############################################################################
#
# Move
#
###############################################################################
def moveFile(src, dst, forceMove = False, debug = False):
    if debug: print "Moving",src,"to",dst
    if isfile(dst) and forceMove == False:
        if debug: print "  Not moving because",dst,"exists."
        return
    if not isfile(src):
        if debug: print "Trying to move",src,"but it doesn't exist."
        return
    move(src, dst)
    

def copyFile(src, dst, forceCopy = False, debug = False):
    if debug: print "Copying",src,"to",dst
    if isfile(dst) and forceCopy == False:
        if debug: print "  Not copying because",dst,"exists."
        return
    if not isfile(src):
        if debug: print "Trying to copy",src,"but it doesn't exist."
        return
    copy(src, dst)
    

def removeFile(filename, debug = False):
    if debug: print "Removing",filename
    if not isfile(filename):
        if debug: print "Trying to remove",filename,"but it doesn't exist."
        return
    remove(filename)



###############################################################################
#
# Move
#
###############################################################################
def moveDir(src, dst, forceMove = False, debug = False):
    if debug: print "Moving",src,"to",dst
    if isdir(dst) and forceMove == False:
        if debug: print "  Not moving because",dst,"exists."
        return
    if not isdir(src):
        if debug: print "Trying to move",src,"but it doesn't exist."
        return
    move(src, dst)
    
def removeDir(dirval, debug = False):
    if debug: print "Removing",dirval
    if not isdir(dirval):
        if debug: print "Trying to remove",dirval,"but it doesn't exist."
        return
    try:
        rmdir(dirval)
    except:
        if debug: print "Trying to remove",dirval,"but it is not empty."
