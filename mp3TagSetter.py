#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  1 12:35:48 2017

@author: tgadfort
"""

import os
import sys
import argparse
from collections import Counter
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from mp3iTunes import getArtistDiscID, getMusicArtistDB
from DiscogBase import getDiscIDHashMod
from DiscogPath import getArtistsDBDir

from mp3Base import getInfo, setArtist, setAlbum, setAlbumArtist, setTrackNumber, setDiscNumber, getAlbumArtist, getArtist, setCountry
from search import findExt, findWalkExt, findNearest
from fsio import setFile
from fileio import get
from fileinfo import getBaseFilename
from strops import nice, makeStrFromUnicode


def info(mp3s):
    for k,mp3 in enumerate(mp3s):
        print mp3
        print getInfo(mp3, allowMissing=True)
        print ""

def show(mp3s):
    print nice("#",4),nice("Filename",40),nice("AlbumArtist",40),nice("Album",30),nice("Country",10),nice("Disc #",10),nice("Track #",10)
              #nice("Artist",40),
    for k,mp3 in enumerate(mp3s):
        info = getInfo(mp3, allowMissing=True)
        print nice(k+1,4),nice(getBaseFilename(mp3),40),
        if info.get("AlbumArtist") != None:
            print nice(info["AlbumArtist"], 40),
        else:
            print nice(" ",40),
        if False:
            if info.get("Artist") != None:
                print nice(info["Artist"], 40),
            else:
                print nice(" ",40),
        if info.get("Album") != None:
            print nice(info["Album"], 30),
        else:
            print nice(" ",30),
        if info.get("Country") != None:
            print nice(info["Country"], 10),
        else:
            print nice(" ",10),
        if info.get("DiscNo") != None:
            print nice(info["DiscNo"], 10),
        else:
            print nice(" ",10),
        if info.get("TrackNo") != None:
            print nice(info["TrackNo"], 10),
        else:
            print nice(" ",10),
        print ""
        
        
def getArtistAndAlbum(mp3s):
    artistCntr = Counter()
    albumCntr  = Counter()    
    for k,mp3 in enumerate(mp3s):
        info = getInfo(mp3, allowMissing=True)
        artistCntr[info["AlbumArtist"]] += 1
        artistCntr[info["Artist"]] += 1
        albumCntr[info["Album"]] += 1
    
    artist = artistCntr.most_common()[0][0]
    album  = albumCntr.most_common()[0][0]
    print "Artist/Album ->",artist,"/",album
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

    if args.get or args.show:
        show(mp3s)

    if args.info:
        info(mp3s)
        
        
    if args.artist:
        artistName = makeStrFromUnicode(args.artist[0])
        for k,mp3 in enumerate(mp3s):
            setArtist(mp3, artistName, debug = True)
        show(mp3s)
        
        
    if args.albumartist or args.aa:
        if args.albumartist:
            albumArtistName = makeStrFromUnicode(args.albumartist[0])
        if args.aa:
            albumArtistName = makeStrFromUnicode(args.aa[0])
        for k,mp3 in enumerate(mp3s):
            setAlbumArtist(mp3, albumArtistName, debug = True)
        show(mp3s)
        
        
    if args.artists:
        artistName = makeStrFromUnicode(args.artists[0])
        for k,mp3 in enumerate(mp3s):
            setArtist(mp3, artistName, debug = True)
            setAlbumArtist(mp3, artistName, debug = True)
        show(mp3s)
        
        
    if args.albumartist2artist or args.aa2a:
        for k,mp3 in enumerate(mp3s):
            artistName = getAlbumArtist(mp3)
            setArtist(mp3, artistName, debug = True)
        show(mp3s)
            
        
    if args.artist2albumartist or args.a2aa:
        for k,mp3 in enumerate(mp3s):
            artistName = getArtist(mp3)
            setAlbumArtist(mp3, artistName, debug = True)
        show(mp3s)


    if args.album:
        albumName = makeStrFromUnicode(args.album[0])
        for k,mp3 in enumerate(mp3s):
            setAlbum(mp3, albumName, debug = True)
        show(mp3s)


    if args.disc:
        discNo = str(args.disc[0])
        for k,mp3 in enumerate(mp3s):
            setDiscNumber(mp3, discNo, debug = True)
        show(mp3s)


    if args.track:
        trackNo = str(args.track[0])
        for k,mp3 in enumerate(mp3s):
            setTrackNumber(mp3, trackNo, debug = True)
        show(mp3s)


    if args.country:
        country = str(args.country[0])
        for k,mp3 in enumerate(mp3s):
            setCountry(mp3, country, debug = True)
        show(mp3s)
        
    if args.match:
        if args.degree:
            matchdegree = float(args.degree[0])
        else:
            matchdegree = 0.5
        artist,album = getArtistAndAlbum(mp3s)
        if artist == None:
            print "Need to set artist or get it from mp3s"
            return
        if album == None:
            print "Need to set album"
            return
        
        musicArtistNames  = getMusicArtistDB(useCleanDirectories = True, debug = True)
        discIDs = musicArtistNames[artist]["DiscID"]
        for discID in discIDs:
            modValue  = getDiscIDHashMod(discID)
            modDBfile = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
            modDB     = get(modDBfile, debug = True)
            artistData = modDB.get(discID)
            artistMediaData = artistData["Media"]

            discogAlbums = []    
            mediaTypes=["Albums", "Singles & EPs", "Compilations"]
            for mediaType in mediaTypes:
                discogArtistAlbumData = artistMediaData.get(mediaType)
                if discogArtistAlbumData:
                    discogAlbums += [makeStrFromUnicode(v["Album"]) for k,v in discogArtistAlbumData.iteritems()]
            
            matchVal = findNearest(album, discogAlbums, 10, matchdegree, debug = False)
            if len(matchVal) > 0:
                print "##",album
                for k in range(len(matchVal)):
                    print "tag -album \""+matchVal[k]+"\""
        
        print ""




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', dest='dirval', nargs=1, help='Directory with mp3s.', required=False)
    parser.add_argument('-r', action="store_false", default=True, help='Recursive search.', required=False)
    parser.add_argument('-get', action="store_true", default=False, help='Get mp3 tags', required=False)
    parser.add_argument('-info', action="store_true", default=False, help='Get mp3 info', required=False)
    parser.add_argument('-show', action="store_true", default=False, help='Show mp3 tags', required=False)
    parser.add_argument('-match', action="store_true", default=False, help='Match album finder', required=False)
    parser.add_argument('-albumartist2artist', action="store_true", default=False, help='Write Artist as Album Artist.', required=False)
    parser.add_argument('-aa2a', action="store_true", default=False, help='Write Artist as Album Artist.', required=False)
    parser.add_argument('-artist2albumartist', action="store_true", default=False, help='Write Album Artist as Artist.', required=False)
    parser.add_argument('-a2aa', action="store_true", default=False, help='Write Album Artist as Artist.', required=False)
    parser.add_argument('-country', dest='country', nargs=1, default=False, help='Write country of release', required=False)
    parser.add_argument('-disc', dest='disc', nargs=1, default=False, help='Write disc number', required=False)
    parser.add_argument('-track', dest='track', nargs=1, default=False, help='Write track number', required=False)
    parser.add_argument('-artist',  dest='artist',  nargs=1, help='Write Artist.', required=False)
    parser.add_argument('-artists',  dest='artists',  nargs=1, help='Write Artist and Album Artist.', required=False)
    parser.add_argument('-album', dest="album", nargs=1, help='Write Album.', required=False)
    parser.add_argument('-albumartist', dest="albumartist", nargs=1, help='Write Album Artist.', required=False)
    parser.add_argument('-aa', dest="aa", nargs=1, help='Write Album Artist.', required=False)
    parser.add_argument('-degree',  dest='degree',  nargs=1, help='Match degree', required=False)
    args = parser.parse_args()
    main(args, cwd=os.getcwd())
