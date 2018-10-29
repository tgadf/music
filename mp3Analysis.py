#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:52:53 2017

@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
import mp3Base
from search import findExt
from fileinfo import getBasename, getDirname
from fsio import mkSubDir, moveDir, setDir, getPath


###############################################################################
#
# Find all mp3s
#
###############################################################################
def findMp3s(dirname, debug = False):
    mp3s  = findExt(dirname, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)
    return mp3s

    
    
###############################################################################
#
# Track Number Analysis
#
###############################################################################
def analysisTrackNumber(tracknumber, num0s, debug = False):
    result = None
    reason = None
    
    if tracknumber == None:
        reason = "No tracknumber tag."
    else:
        if tracknumber == "0":
            num0s += 1
            result = True
            if num0s > 1:
                result = False
                reason = "Tracknumber is zero."
        elif len(tracknumber) > 0:
            result = True
        else:
            result = False
            reason = "Tracknumber is empty."

    return result,reason,num0s



###############################################################################
#
# Artist Analysis
#
###############################################################################
def analysisArtist(artist, debug = False):
    result = None
    reason = None

    if artist == None:
        reason = "No artist tag."
    else:
        if artist.title().find("Unknown") != -1:
            reason = "Unknown Artist."
            result = True
        if len(artist) > 0:
            result = True
        else:
            result = False
            reason = "Artist is empty."

    return result,reason



###############################################################################
#
# Album Analysis
#
###############################################################################
def analysisAlbum(album, debug = False):
    result = None
    reason = None

    if album == None:
        reason = "No album tag."
    else:
        if album.title().find("Unknown") != -1:
            reason = "Unknown Album."
            result = True
        if len(album) > 0:
            result = True
        else:
            result = False
            reason = "Album is empty."

    return result,reason




###############################################################################
#
# Inspect Directory for good ID3 tags
#
###############################################################################
def inspectDirectoryForGoodID3Tags(dirname, debug = False):
    mp3s = findMp3s(dirname)
    if len(mp3s) == 0: return
    
    if debug:
        print ""
        print "======================",dirname,"======================"
        print " -> Found",len(mp3s),"mp3s."
        print ""


    ###########################################################################
    ## Loop over mp3s
    ###########################################################################
    id3Result    = True
    id3Reason    = None
    trackResult  = True
    trackReason  = None
    artistResult = True
    artistReason = None
    albumResult  = True
    albumReason  = None
    num0s = 0
    for k, mp3 in enumerate(mp3s):
        audio = mp3Base.getID3(mp3, debug)
        if audio == None:
            id3Reason = "Broken ID3."
            id3Result = None
            break

        if trackResult:
            tracknumber = mp3Base.getTrackNo(audio)
            trackResult,trackReason,num0s = analysisTrackNumber(tracknumber, num0s, debug)

        if artistResult:
            artist = mp3Base.getArtist(audio)
            artistResult,artistReason = analysisArtist(artist, debug)

        if albumResult:
            album = mp3Base.getArtist(audio)
            albumResult,albumReason = analysisAlbum(album, debug)


    isGood = all([id3Result,trackResult,artistResult,albumResult])
    isErr  = not id3Result == True
    isFix  = not isGood and not isErr
    if debug:
        print "\nInspect [",dirname,"]"
        if not id3Result == True:
            print " -> ID3 error:",id3Reason
        if not trackResult == True: 
            print " -> Track numbers error:",trackReason
        if not artistResult == True:
            print " -> Artist error:",artistReason
        if not albumResult == True:
            print " -> Album error:",albumReason
        if isGood:
           print " -> Folder looks good."
        else:
           print " -> Bad folder."
        print "==============================================================="
        print ""

    return isGood, isErr, isFix



###############################################################################
#
# Inspect Directory for good ID3 tags
#
###############################################################################
def inspectForGoodID3Tags(rootdir, outputdir, debug = True):
    rootdir = getPath(rootdir)
    basedir = getDirname(rootdir)
    
    from os import walk
    for root, dirs, files in walk(rootdir, topdown=False):
        if len(files) == 0: continue
        if debug:
            print "Walking to",root
        isGood,isErr,isFix = inspectDirectoryForGoodID3Tags(root, debug)

        if isGood: dstDir = mkSubDir(outputdir, 'good-tags', debug)
        if isErr:  dstDir = mkSubDir(outputdir, 'error-tags', debug)
        if isFix:  dstDir = mkSubDir(outputdir, 'fix-tags', debug)

        path = getPath(root.replace(basedir, ""))
        if path.startswith('/'): path = path[1:]
        if path.count('/') > 0:
            dirpath = getDirname(path)
            dstDir = mkSubDir(dstDir, dirpath.split('/'), debug)

        sublevel = getBasename(getPath(root))
        dstDir = setDir(dstDir, sublevel, debug)    
        moveDir(root, dstDir, debug = True)