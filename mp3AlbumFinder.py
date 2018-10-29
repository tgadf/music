#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 07:08:36 2017

@author: tgadfort
"""


import os
import sys
import argparse
from collections import Counter
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from DiscogPath import getArtistsDBDir
from DiscogBase import getDiscIDHashMod, getArtistNameIDs
from mp3Base import getInfo
from search import findExt, findWalkExt, findNearest, findSimilarity
from fileio import get
from strops import makeStrFromUnicode
from fsio import setFile


def findAlbumAndArtist(mp3s):
    artist = Counter()
    album  = Counter()
    
    for mp3 in mp3s:
        info = getInfo(mp3, allowMissing=True)
        artist[info["AlbumArtist"]] += 1
        album[info["Album"]] += 1

    if len(artist) > 0 and len(album) > 0:
        artist = artist.most_common()[0][0]
        album  = album.most_common()[0][0]
    else:
        artist = None
        album  = None
    
    return artist,album


def main(args, cwd, debug = True):
    if args.dirval == None:
        if debug:
            print "Using current directory as input directory."
        dirval = cwd
    else:
        if debug:
            print "Using -dir argument as input directory."
        dirval = args.dirval[0]
        
        
    mp3s = findExt(dirval, ext=[".mp3", ".Mp3", ".MP3"], debug=False)
    if args.r:
        if debug:
            print "  Using recursive directory search."
        mp3s = findWalkExt(dirval, ext=[".mp3", ".Mp3", ".MP3"], debug=False)

    if debug:
        print "Finding mp3s in",dirval,"... Found",len(mp3s),"mp3s."

    if args.d:
        matchdegree = args.d[0]
        print "Using user match degree of",matchdegree
    else:
        matchdegree = 0.75
        print "Using match degree of 0.75"

    artist,album = findAlbumAndArtist(mp3s)
    
    discogArtistNames   = getArtistNameIDs(debug = True)
    discID = discogArtistNames.get(artist)
    if discID == None:
        print "Could not find discID for artist:",artist
        return

    modValue = getDiscIDHashMod(discID)
    modDBfile = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
    modDB     = get(modDBfile, debug = True)
    
    discogArtistData = modDB.get(discID)
    if discogArtistData == None:
        print "Could not find any data for discID/artist:",discID,artist
        return
            
    discogArtistMediaData = discogArtistData["Media"]
    discogArtistAlbumData = discogArtistMediaData.get("Albums")
    if discogArtistAlbumData == None:
        print "Could not find any albums for discID/artist:",discID,artist
        return

    discogArtistAlbums   = [makeStrFromUnicode(v["Album"]) for k,v in discogArtistAlbumData.iteritems()]
    discogArtistAlbumIDs = discogArtistAlbumData.keys()
    discogArtistAlbums   = dict(zip(discogArtistAlbums, discogArtistAlbumIDs))
                    
    matchVal = findNearest(album, discogArtistAlbums.keys(), 5, matchdegree, debug = False)
    print ""
    print "Found",len(matchVal),"matches:"
    for match in matchVal:
        print findSimilarity(album, match),'\t',match
    print ""



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', dest='dirval', nargs=1, help='Directory with mp3s.', required=False)
    parser.add_argument('-r', action="store_false", default=True, help='Recursive search.', required=False)
    parser.add_argument('-d', dest='d', nargs=1, default=False, help='Match Degree', required=False)
    args = parser.parse_args()
    main(args, cwd=os.getcwd())
