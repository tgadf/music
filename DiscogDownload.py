#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 21:10:03 2017

@author: tgadfort
"""

from urllib2 import urlopen
from urllib import pathname2url
import subprocess
import sys

if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fileio import save
from fsio import removeFile, isFile
from fileinfo import getSize


################################################################################
#
# Download Discog Data
#
################################################################################
def getURL(url, savename, debug = False):
    if debug:
        print "Downloading",url
    content = urlopen(url).read()
    save(savename, content)
    retval = checkFileSize(savename, 1000)
    return retval



def asrun(ascript):
    "Run the given AppleScript and return the standard output and error."
    osa = subprocess.Popen(['osascript', '-'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

    return osa.communicate(ascript)[0]



def getSafariURL(url, savename, dtime = 5, debug = False):
    dscript =  '''
    tell application "Safari"
    activate
    set URL of document 1 to "{0}"
    delay {1}
    set myString to source of document 1
    end tell
    '''.format(url, dtime)
    
    if False:
        dscript = '''
        tell application "Safari"
        activate
        set URL of document 1 to "{0}"
        delay {2}
        set myString to source of document 1
        end tell
        set newFile to POSIX file "{1}"
        open for access newFile with write permission
        write myString to newFile
        close access newFile
        '''.format(url, savename, dtime)

    content = asrun(dscript)
    save(savename, content)
    retval = checkFileSize(savename, 1000)
    return retval


    
def getData(base, suburl, extra, savename, dtime = 5, useSafari = True, debug = False):
    url = base
    if suburl:
        url += pathname2url(suburl.encode("utf-8"))
        
    if extra:
        url += extra

    if useSafari:
        retval = getSafariURL(url, savename, dtime, debug)
    else:
        retval = getURL(url, savename, debug)
    
    return retval
    


def checkFileSize(ifile, minSize = 1000):
    if not isFile(ifile):
        return None
    
    if getSize(ifile, 'B') < minSize:
        print " --> Removing due to low size:",ifile
        removeFile(ifile)
        return False
    return True
