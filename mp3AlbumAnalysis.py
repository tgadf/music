#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 10:37:17 2017

@author: tgadfort
"""



import sys
from collections import Counter
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
import mp3Base
import mp3TrackNumberAnalysis
from search import findExt, findSimilarity
from fileinfo import getBasename
from fsio import getPath, getDirname, mkSubDir, setDir, moveDir


###############################################################################
#
# Determine Artist Parameters
#
###############################################################################
def inspectAlbumArtist(mp3s, minSim = 0.75, minVarious = 0.25, suggestedArtistName = None, debug = False):
    artistCnt = Counter()
    compilationFlag = False
    if len(mp3s) == 0:
        return None, False
    
    for k, mp3 in enumerate(mp3s):
        artist = mp3Base.getArtist(mp3)
        artistCnt[artist] += 1

    if float(len(artistCnt))/len(mp3) > minVarious:
        compilationFlag = True
        albumArtist = "Various Artists"
    else:
        albumArtist = artistCnt.most_common()[0][0]
        if suggestedArtistName:
            similarity = findSimilarity(albumArtist, suggestedArtistName)
        else:
            similarity = 1.0
            
        if similarity < minSim:
            albumArtist = None
        
    if debug:
        print "  Determined artist/compilation as:",albumArtist,"/",compilationFlag
        
    return albumArtist, compilationFlag



###############################################################################
#
# Determine Album Parameters
#
###############################################################################
def inspectAlbumName(mp3s, minSim = 0.75, suggestedAlbumName = None, debug = False):
    albumCnt = Counter()
    if len(mp3s) == 0:
        return None, False
    
    for k, mp3 in enumerate(mp3s):
        album = mp3Base.getAlbum(mp3)
        albumCnt[album] += 1

    albumName = albumCnt.most_common()[0][0]
    if suggestedAlbumName:
        similarity = findSimilarity(albumName, suggestedAlbumName)
    else:
        similarity = 1.0
        
    if similarity < minSim:
        albumName = None

    if debug:
        print "  Determined album as:",albumName
                
    return albumName



###############################################################################
#
# Determine Album Parameters
#
###############################################################################
def getTrackNumbers(mp3s, trknomap, force = False):
    ntrks = 0
    for k1,v1 in trknomap.iteritems():
        ntrks += len(v1.keys())
    #print ntrks,'\t',len(mp3s)
    if ntrks == len(mp3s) or force:
        trknums=[]
        for k in range(len(mp3s)): trknums.append(0)
        discs = sorted(trknomap.keys())
        for idisc in range(len(discs)):
            nprev = 0
            for ii in range(idisc, 0, -1):
                nprev += len(trknomap[discs[ii-1]])
            for trkno,mp3no in trknomap[discs[idisc]].iteritems():
                #print mp3no,'\t',trkno,'\t',trkno + nprev
                trknums[mp3no] = trkno + nprev
        return trknums
    return None



def inspectAlbumTrackNumbers(mp3s, debug = False):
    
    foundTrackNumberFromID3   = False
    foundTrackOrderFromNames  = True
    foundTrackNumberFromNames = True
    
    trackNoMap = {}
    trackNos   = []
    ptrknovals = [None,None]
    trackValueMap = {}

    for k, mp3 in enumerate(mp3s):
        mp3Name = getBasename(mp3)
        
        trackNumber = mp3Base.getTrackNumber(mp3)
        if trackNumber != None:
            foundTrackNumberFromID3 = True
            trackValueMap[k] = trackNumber

        trkno = str(k+1)
        if mp3Name.find(trkno) == -1:
            foundTrackOrderFromNames = False


        trknovals = mp3TrackNumberAnalysis.findTrkNo(mp3Name)
        if trknovals[0] != None:
            disc = trknovals[0]
            tkno = trknovals[1]                
            if trackNoMap.get(disc) == None:
                trackNoMap[disc] = {}
            if trknovals[1] != None:
                trackNoMap[disc][tkno] = k


        if trknovals[0] != None:
            if ptrknovals[0] == None:
                ptrknovals[0] = trknovals[0]
                ptrknovals[1] = trknovals[1]
                trackNos.append(trknovals[1])
            else:
                discdiff = trknovals[0] - ptrknovals[0]
                trkdiff  = trknovals[1] - ptrknovals[1]
                if discdiff == 0 and trkdiff == 1:
                    ptrknovals[0] = trknovals[0]
                    ptrknovals[1] = trknovals[1]
                    trackNos.append(trknovals[1])
                elif discdiff == 1 and trkdiff < 0:
                    ptrknovals[0] = trknovals[0]
                    ptrknovals[1] = trknovals[1]
                    trackNos.append(trackNos[-1]+1)
                else:
                    foundTrackNumberFromNames = False
        else:
            foundTrackNumberFromNames = False

        if ptrknovals[0] == None:
            foundTrackNumberFromNames = False
      
        
        
    if debug:
        if foundTrackNumberFromID3:
            print "  --> Found all track numbers from ID3 tags."
        else:
            print "  --> Could not find all track numbers from ID3 tags."
        if foundTrackOrderFromNames:
            print "  --> Found all track ordering from file names."
        else:
            print "  --> Could not find all track ordering from file names."
        if foundTrackNumberFromNames:
            print "  --> Found all track numbers from file names."
        else:
            print "  --> Could not find all track numbers from file names."
        
    
    ###########################################################################
    # Set track numbers now if they aren't already set since we just did the analysis
    ###########################################################################
    if not foundTrackNumberFromID3:
        trknums = getTrackNumbers(mp3s, trackNoMap)
        if trknums:
            if debug:
                print "  ==> Determined track numbers using track numbers map."
            trackNos = trknums
            foundTrackNumberFromNames = True
        
    madeEdits = False
    if foundTrackNumberFromNames and not foundTrackNumberFromID3:
        if debug:
            print "  ==> Setting track numbers based on track number map."
        madeEdits = True
        for k, mp3 in enumerate(mp3s):
            mp3Base.setTrackNo(mp3, str(trackNos[k]), debug)
    elif foundTrackOrderFromNames and not foundTrackNumberFromID3:
        if debug:
            print "  ==> Setting track numbers based on file name."
        retval = True
        madeEdits = True
        for k, mp3 in enumerate(mp3s):
            trkno = k+1
            mp3Base.setTrackNo(mp3, str(trkno), debug)
    else:
        if foundTrackNumberFromID3:
            print "  ==> Not setting track numbers because they are already set."
            retval = True
        else:
            retval = False
    
    if debug:
        if madeEdits:
            print "  ==> Set track numbers while determining their order."
        else:
            print "  ==> No changes were made to the track numbers."

    return retval



def inspectDirectoryForCorrectness(dirname, debug = False):
    mp3s = findExt(dirname, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)
    if len(mp3s) == 0: return

    
    # 1) check artist
    albumArtist,compilationFlag = inspectAlbumArtist(mp3s, debug = debug)
    
    # 2 check album
    albumName = inspectAlbumName(mp3s, debug = debug)
    
    # 3 check track numbers
    trackRetval = inspectAlbumTrackNumbers(mp3s, debug = debug)
    

    print "|------------------------------------------------------------------"
    print "| Folder      ->",dirname
    print "| Artist      ->",albumArtist
    print "| Compilation ->",compilationFlag
    print "| Album       ->",albumName
    print "| Track Nums  ->",trackRetval
    print "|------------------------------------------------------------------"

    isGood = (albumArtist != None and len(albumArtist) > 0) and (albumName != None and len(albumName) > 0) and (trackRetval)
    retval = {"good": isGood, "artist": albumArtist, "album": albumName, "compilation": compilationFlag, "tracks": trackRetval}
    return retval



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
        retval = inspectDirectoryForCorrectness(root, debug)
        isGood = retval["good"]

        if isGood:
            dstDir = mkSubDir(outputdir, 'good-corr', debug)
        else:
            dstDir = mkSubDir(outputdir, 'error-corr', debug)

        path = getPath(root.replace(basedir, ""))
        if path.startswith('/'): path = path[1:]
        if path.count('/') > 0:
            dirpath = getDirname(path)
            dstDir = mkSubDir(dstDir, dirpath.split('/'), debug)

        sublevel = getBasename(getPath(root))
        dstDir = setDir(dstDir, sublevel, debug)    
        moveDir(root, dstDir, debug = True)