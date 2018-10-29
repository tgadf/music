# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 15:24:53 2017

@author: tgadfort
"""


import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
from fileio import removeFile, mkSubDir, setDir, get, save, setFile, setSubFile, getBasename, moveFile, isDir, isFile, mkDir, setSubDir
from glob import glob
from os import stat
from os.path import join, getsize, exists
import datetime as dt
from hashlib import sha1
from math import ceil

from search import findNearest, findMatchingWord, findPatternExt, findSubExt, findExt, findAll
from DiscogDownload import getDiscogDir, getDiscogBaseDBDir



################################################################################
#
# Create Master Lists
#
################################################################################
def createMasterLists(base = "/Volumes/Music/Discog", debug = False, lastHours=None, forceWrite=False):
    base    = getDiscogDir()
    basedir = getDiscogBaseDBDir()
    
    dbname  = setFile(basedir, "artistDB.json")
    if forceWrite:
        print "Starting from scratch"
        data = {}
    else:
        print dbname,'size ->',round(getsize(dbname)/1e6),"MB"
        data = get(dbname)
        print "Found",len(data),"known artists from",dbname
    
    
    musicdbname  = setFile(basedir, "artistMusicDB.json")
    if forceWrite:
        print "Starting from scratch"
        musicdata = {}
    else:
        print musicdbname,'size ->',round(getsize(musicdbname)/1e6),"MB"
        musicdata  = get(musicdbname)
        print "Found",len(musicdata),"known artists w/ albums from",musicdbname
    
    
    albumdbname  = setFile(basedir, "albumDB.json")
    if forceWrite:
        print "Starting from scratch"
        albumdata = {}
    else:
        print albumdbname,'size ->',round(getsize(albumdbname)/1e6),"MB"
        albumdata  = get(albumdbname)
        print "Found",len(albumdata),"known artists w/ albums from",albumdbname
    
    
    
    now = dt.datetime.now()

    files = []
    fdirs = ["artists-db", "artists-db-extra"]    
    for fdir in fdirs:
        if not lastHours:
            files += findSubExt(base, fdir, exp=".p")
            #files += glob(join(base, fdir, "*.p"))
        else:
            ago = now-dt.timedelta(hours=lastHours)
            for ifile in findSubExt(base, fdir, exp=".p"):
                st    = stat(ifile)
                mtime = dt.datetime.fromtimestamp(st.st_mtime)
                #print ifile,'\t',mtime > ago
                if mtime > ago:
                    files.append(ifile)
                    if debug: print ifile,'\t',mtime,ago

    if not lastHours:
        print "Found",len(files),"unique artist db files."

    print "Keeping",len(files),"unique artist db files."
    for i,ifile in enumerate(files):
        if i % 1000 == 0 or i == 100 or i == 500:
            print i,'/',len(files),"\t->",ifile
        artistData = get(ifile)
        discID     = artistData["ID"]
        URL        = artistData["URL"]
        artist     = artistData["Artist"]
        media = artistData.get("Media")
        if media:
            albums = artistData["Media"].get("Albums")
            if albums:
                albums = [x["Album"] for x in albums]
            else:
                albums = []
        else:
            albums = []

        if data.get(discID) == None:
            if debug: print "--> Adding",discID,'\t',artist
            data[discID] = {"URL": URL, "Artist": artist, "Files": {ifile: 1}}
        else:
            if data[discID]["Files"].get(ifile) == None:
                if debug: print "\t--> Adding",ifile,"to files"
                data[discID]["Files"][ifile] = 1

        if musicdata.get(artist) == None:
            musicdata[artist] = {"Also": None, "Albums": []}
            musicdata[artist]["Albums"] = albums

        for album in albums:
            if albumdata.get(album) == None:
                albumdata[album] = {}
            albumdata[album][artist] = 1


    print "Saving",len(data),"known artists to",dbname
    save(dbname, data)
    print dbname,'size ->',round(getsize(dbname)/1e6),"MB"

    print "Saving",len(musicdata),"known artists w/ albums to",musicdbname
    save(musicdbname, musicdata)
    print musicdbname,'size ->',round(getsize(musicdbname)/1e6),"MB"

    print "Saving",len(albumdata),"known artists w/ albums to",albumdbname
    save(albumdbname, albumdata)
    print albumdbname,'size ->',round(getsize(albumdbname)/1e6),"MB"