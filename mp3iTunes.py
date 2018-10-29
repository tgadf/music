#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 08:36:11 2017

@author: tgadfort
"""

import sys
import re
from collections import Counter
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

import mp3Base
from fileio import save, get
from fileinfo import getBasename, getFileBasics, getSize, getBaseFilename
from fsio import setSubDir, removeDir, moveDir, setFile, setDir, isFile, moveFile, mkSubDir, removeFile
from search import findDirs, findExt, findDirsPattern, findPatternExt, findNearest, findWalkExt
from strops import makeStrFromUnicode, makeUnicode, getSaveName
from timing import start,inter,end
from mp3Path import getMusicDBDir, getiTunesDir, getConsolidateDir




###############################################################################
# Basic Music DB File
###############################################################################
def getMusicArtistDB(useCleanDirectories = True, debug = True):
    dbDir    = getMusicDBDir()
    if useCleanDirectories:
        savename = setFile(dbDir, "artistMusicDB-clean.yaml")
    else:
        savename = setFile(dbDir, "artistMusicDB-full.yaml")
        
    if debug:
        print "Loading",savename
    db = get(savename)
    if debug:
        print "Loading",savename,"... Found",len(db),"entries."
    return db


def getArtistDiscID(artist):
    db     = getMusicArtistDB(useCleanDirectories = True, debug = False)
    discID = db.get(artist)
    return discID


def saveMusicArtistDB(db, useCleanDirectories = True, debug = True):
    dbDir    = setDir(getiTunesDir(), "MusicDB")
    if useCleanDirectories:
        savename = setFile(dbDir, "artistMusicDB-clean.yaml")
    else:
        savename = setFile(dbDir, "artistMusicDB-full.yaml")
    if debug:
        print "Saving",len(db),"artist names (determined from Music) to",savename
    save(savename, db)




###############################################################################
# Clean iTunes music directories
###############################################################################
def cleaniTunesDir(dirname, debug = False):
    try:
        baseMusicDir = setSubDir(dirname, ["iTunes Media", "Music"])
    except:
        print "Could not find iTunes Music Directory in",dirname
        return

    musicDirs = findDirs(baseMusicDir, debug)
    for musicDir in musicDirs:
        print musicDir
        albums = findDirs(musicDir, debug)
        mp3s = findExt(musicDir, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)
        print len(albums),'\t',len(mp3s),'\t',musicDir
        if len(albums) == 0 and len(mp3s) == 0:
            removeDir(musicDir, debug = True)
            continue
        for album in albums:
            if album.count('[') > 0:
                newAlbum = album.replace("[", "")
                newAlbum = newAlbum.replace("]", "")
                moveDir(album, newAlbum, debug = True)
                album = newAlbum
            mp3s = findExt(album, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)
            dirs = findDirs(album, debug)
            print "\t",len(dirs),'\t',len(mp3s),'\t',album
            if len(mp3s) == 0 and len(dirs) == 0:
                removeDir(album, debug = True)
                continue
            
###############################################################################
#
# Clean all iTunes music directories
#
###############################################################################
def cleaniTunesDirs(debug = False):
    basedir = getiTunesDir()
    iTunesDirs = findDirsPattern(basedir, "iTunes", debug)
    for iTunesDir in iTunesDirs:
        cleaniTunesDir(iTunesDir, debug)






###############################################################################
#
# Create Music DB from iTunes Directories
#
###############################################################################
def createBaseMusicDB(dirname, debug = True):
    try:
        baseMusicDir = setSubDir(dirname, ["iTunes Media", "Music"])
    except:
        print "Could not find iTunes Music Directory in",dirname
        return

    data = {}
    errs = {}
    for k,mp3 in enumerate(findWalkExt(baseMusicDir, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)):
        try:
            mp3data = mp3Base.getInfo(mp3, allowMissing = True)
        except:
            print "Problem with mp3 data for",mp3
            errs[mp3] = mp3data
            continue
        data[mp3] = mp3data

    savename = setFile(getMusicDBDir(), getBasename(dirname)+".json")
    print "Saving",len(data),"mp3s to",savename
    save(savename, data, debug = True)

    print "Error with the following mp3s:"
    for err in errs.keys():
        print err

    savename = setFile(getMusicDBDir(), getBasename(dirname)+"-Errors.json")
    print "Saving",len(errs),"error mp3s to",savename
    save(savename, errs, debug = True)


                        
def createBaseMusicDBs(debug = False):
    basedir = getiTunesDir()
    iTunesDirs = findDirsPattern(basedir, "iTunes", debug)
    for iTunesDir in iTunesDirs:
        createBaseMusicDB(iTunesDir, debug)



###############################################################################
#
# Clean Music DB
#
###############################################################################
def cleanBaseMusicDB(dirname, debug = True):
    savename = setFile(getMusicDBDir(), getBasename(dirname)+".json")
    data = get(savename, debug = True)
    print "Found",len(data),"mp3s."
    
    startVal = start()
    for k,mp3 in enumerate(data.keys()):
        if (k+1) % 10000 == 0: inter(startVal, k+1, len(data))
        if not isFile(mp3):
            del data[mp3]

    savename = setFile(getMusicDBDir(), getBasename(dirname)+".json")
    print "Saving",len(data),"mp3s to",savename
    save(savename, data, debug = True)



###############################################################################
#
# Create Master Music DB
#
###############################################################################
def createMasterMusicDB(useCleanDirectories = True):
    dbDir = setDir(getiTunesDir(), "MusicDB")    
    musicDBs = findPatternExt(dbDir, pattern="iTunes", ext=".json")
    
    artistMusicDB = {}
    missingTags   = {"Compilation": [], "Artist": [], "Album": [], "Title": [], "AlbumArtist": [], "Track": [], "Disc": []}
    
    for musicDB in musicDBs:
        if useCleanDirectories:
            if musicDB.find("Multiple Artists and DJs") != -1 or musicDB.find("Fix Artists") != -1:
                continue
            if musicDB.find("Investigate") != -1 or musicDB.find("Missing") != -1:
                continue
            if musicDB.find("Fix Artists") != -1 or musicDB.find("Fix1") != -1:
                continue
            if musicDB.find("Live") != -1:
                continue
            if musicDB.find("Classical") != -1:
                continue
            if musicDB.find("Compilation") != -1:
                continue
            if musicDB.find("Errors") != -1:
                continue
            if musicDB.find("Matched") != -1:
                continue
            if musicDB.find("Jazz") != -1:
                continue
        
        db = get(musicDB)
        
        startVal = start()
        for k, mp3 in enumerate(db.keys()):
            mp3data = db[mp3]
            if (k+1) % 20000 == 0: inter(startVal, k+1, len(db))

            artist      = makeStrFromUnicode(mp3data["Artist"])
            albumartist = makeStrFromUnicode(mp3data["AlbumArtist"])
            album       = makeStrFromUnicode(mp3data["Album"])
            title       = makeStrFromUnicode(mp3data["Title"])
            track       = mp3data["TrackNo"] 
            disc        = mp3data["DiscNo"]
            compilation = mp3data["Compilation"]
            if artistMusicDB.get(albumartist) == None:
                artistMusicDB[albumartist] = {"DiscID": None, "Albums": {}}
            if artistMusicDB[albumartist]["Albums"].get(album) == None:
                artistMusicDB[albumartist]["Albums"][album] = {"ID": None, "Cnt": 0, "Titles": {}}
            artistMusicDB[albumartist]["Albums"][album]["Cnt"] += 1
            artistMusicDB[albumartist]["Albums"][album]["Titles"][title] = track

            try:
                int(compilation)
            except:
                missingTags["Compilation"].append(mp3)

            try:
                int(disc)
            except:
                missingTags["Disc"].append(mp3)
                
            try:
                int(track)
            except:
                missingTags["Track"].append(mp3)
                
            if artist == None or artist == False:
                missingTags["Artist"].append(mp3)

            if albumartist == None or albumartist == False:
                missingTags["AlbumArtist"].append(mp3)

            if album == None or album == False:
                missingTags["Album"].append(mp3)

            if title == None or title == False:
                missingTags["Title"].append(mp3)

            if disc == None or disc == False:
                missingTags["Disc"].append(mp3)
            

    end(startVal)
    saveMusicArtistDB(artistMusicDB, useCleanDirectories)
    
    for k,v in missingTags.iteritems():
        if len(v) > 0:
            savename = setFile(dbDir, "missingTags-"+k+".json")
            print "Saving",len(v),"missing",k,"tags to",savename
            save(savename, v)
            
            

###############################################################################
#
# Consolidate Mp3s by Artist/Album
#
###############################################################################
def consolidateMp3sByArtist(useCleanDirectories = True):
    consolidateDir = getConsolidateDir()
    baseMusicDir   = setSubDir(consolidateDir, ["iTunes Media", "Music"])
    
    dbDir = setDir(getiTunesDir(), "MusicDB")
    musicDBs = findPatternExt(dbDir, pattern="iTunes", ext=".json")
    
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    condb = get(dbname, debug = True)
    
    for musicDB in musicDBs:
        if useCleanDirectories:
            if musicDB.find("Multiple Artists and DJs") != -1 or musicDB.find("Fix Artists") != -1:
                continue
            if musicDB.find("Investigate") != -1 or musicDB.find("Missing") != -1:
                continue
            if musicDB.find("Fix Artists") != -1 or musicDB.find("Fix1") != -1:
                continue
            if musicDB.find("Compilation") != -1:
                continue
            if musicDB.find("Live") != -1:
                continue
            if musicDB.find("Classical") != -1:
                continue
            if musicDB.find("Consolidate") != -1:
                continue
            if musicDB.find("Errors") != -1:
                continue
        
        db = get(musicDB)
        
        for mp3,mp3data in db.iteritems():
            artistName = makeStrFromUnicode(mp3data["AlbumArtist"])
            if artistName == None:
                mp3data = mp3Base.getInfo(mp3, allowMissing = True)
                artistName = makeStrFromUnicode(mp3data["AlbumArtist"])
            if artistName == None:
                print mp3
                print mp3data
                raise ValueError("No artist!")
            artistName = getSaveName(artistName)
            artistDir  = mkSubDir(baseMusicDir, artistName, debug = False)

            albumName = makeStrFromUnicode(mp3data["Album"])
            if albumName == None:
                mp3data = mp3Base.getInfo(mp3, allowMissing = True)
                albumName = makeStrFromUnicode(mp3data["Album"])
            if albumName == None:
                setMp3Tags(mp3, album="Unknown Album")
                mp3data = mp3Base.getInfo(mp3, allowMissing = True)
                albumName = makeStrFromUnicode(mp3data["Album"])
            if albumName == None:
                print mp3
                print mp3data
                raise ValueError("No album!")
            albumName = getSaveName(albumName)
            albumDir  = mkSubDir(artistDir, albumName, debug = False)

            mp3Dirname, mp3Basename, mp3Ext = getFileBasics(mp3)
            mp3Basename = makeStrFromUnicode(mp3Basename)
            outname = setFile(albumDir, mp3Basename+".mp3")
            moveFile(mp3, outname, debug = True)
            if isFile(outname):
                mp3data = mp3Base.getInfo(outname, allowMissing = True)
                condb[outname] = mp3data

    save(dbname, condb, debug = True)



###############################################################################
#
# Consolidate Remaining MP3s
#
###############################################################################
def consolidateRemainingMp3s(debug = False):
    consolidateDir = getConsolidateDir()
    consolidateMusicDir   = setSubDir(consolidateDir, ["iTunes Media", "Music"])

    mp3Dir = setDir(getiTunesDir(), 'iTunes Test')
    baseMusicDir   = setSubDir(mp3Dir, ["iTunes Media", "Music"])

    dirs = findDirs(baseMusicDir)
    for artistDir in dirs:
        albums = findDirs(artistDir)
        for albumDir in albums:
            mp3s = findWalkExt(albumDir, ext=[".mp3", ".Mp3", ".MP3"], debug=debug)
            for mp3 in mp3s:
                outfile = mp3.replace(baseMusicDir, consolidateMusicDir)
                if isFile(outfile):
                    mp3size = getSize(mp3)
                    outsize = getSize(outfile)
                    if mp3size > outsize:
                        moveFile(mp3, outfile, forceMove = True, debug = True)
                    else:
                        removeFile(mp3, debug = True)
                
    
    print consolidateMusicDir
    print baseMusicDir

###############################################################################
#
# Find records
#
###############################################################################
def findDBRecords(db = None, artist = None, album = None, pattern = None,
                  useCleanDirectories = True):
    if db == None:
        dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
        print "Searching in",dbname
        db = get(dbname, debug = True)
    else:
        print "Searching in custum DB."
        
    if isinstance(artist,list):
        artist = [makeStrFromUnicode(x) for x in artist]
    else:
        artist = makeStrFromUnicode(artist)
    if isinstance(album,list):
        album = [makeStrFromUnicode(x) for x in album]
    else:
        album = makeStrFromUnicode(album)


    records = {}
    for mp3,mp3data in db.iteritems():
        if artist:
            if isinstance(artist,list):
                for artistName in artist:
                    if makeUnicode(mp3data["Artist"]).find(artistName) != -1:
                        records[mp3] = mp3data
                    if makeUnicode(mp3data["AlbumArtist"]).find(artistName) != -1:
                        records[mp3] = mp3data
            else:
                if makeStrFromUnicode(mp3data["Artist"]).find(artist) != -1:
                    records[mp3] = mp3data
                if makeStrFromUnicode(mp3data["AlbumArtist"]).find(artist) != -1:
                    records[mp3] = mp3data
                
        if album:
            if isinstance(album,list):
                for albumName in album:
                    if makeUnicode(mp3data["Album"]) == albumName:
                        records[mp3] = mp3data
            else:
                if makeStrFromUnicode(mp3data["Album"]) == artist:
                    records[mp3] = mp3data
                
        if pattern:
            keep = True
            if isinstance(pattern, list):
                for patt in pattern:
                    if mp3.find(patt) == -1:
                        keep = False
            else:
                if mp3.find(pattern) == -1:
                    keep = False
            if keep:
                records[mp3] = mp3data
                       

    print "Found",len(records),"matching records."
    i = 0
    for mp3,mp3data in records.iteritems():
        print mp3
        print mp3data
        print "\n"
        if i == 2:
            print "..."
            print ""
            break
        i += 1
        
    return records




###############################################################################
#
# Check for near matches
#
###############################################################################
def findNearArtistNameMatches(useCleanDirectories = True, debug = True):
    db = getMusicArtistDB(useCleanDirectories)
        
    artists = db.keys()
    for artist in sorted(artists):
        matches = findNearest(artist, artists, 5, 0.85, debug)
        if len(matches) == 1: continue
        print artist,"--->",
        matches.remove(artist)
        print " , ".join(matches)



###############################################################################
#
# Set MP3 Size
#
###############################################################################
def addMp3Size(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    
    startVal = start()
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 5000 == 0: inter(startVal, k+1, len(db))
        if db[mp3].get("Size") == None:
            if isFile(mp3):
                size = getSize(mp3)
                db[mp3]["Size"] = size
            else:
                del db[mp3]

    save(dbname, db, debug = True)
    end(startVal)

    
def addCountry(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    
    startVal = start()
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 5000 == 0: inter(startVal, k+1, len(db))
        if db[mp3].get("Country") == None:
            if isFile(mp3):
                country = "US"
                db[mp3]["Country"] = country
            else:
                del db[mp3]

    save(dbname, db, debug = True)
    end(startVal)
    
    
###############################################################################
#
# Set Album Artist Tag (if missing)
#
###############################################################################
def setAlbumArtistTag(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    fix = {}
    startVal = start()
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 25000 == 0: inter(startVal, k+1, len(db))
        albumArtist = db[mp3]["AlbumArtist"]
        if albumArtist == None or albumArtist == False:            
            fix[mp3] = db[mp3]

    startVal = start()
    for k,mp3 in enumerate(fix.keys()):
        if (k+1) % 250 == 0:
            inter(startVal, k+1, len(fix))
            save(dbname, db, debug = True)

        artist      = fix[mp3]["Artist"]
        if isFile(mp3):
            mp3Base.setAlbumArtist(mp3, artist, debug = False)
            db[mp3]["AlbumArtist"] = artist

    end(startVal)
    save(dbname, db, debug = True)


    
###############################################################################
#
# Set Unknown Artist/Album (if missing)
#
###############################################################################
def setArtistOrAlbumTag(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    startVal = start()
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 5000 == 0:
            inter(startVal, k+1, len(db))
            save(dbname, db, debug = True)
            
        artist = db[mp3]["Artist"]
        if artist == "Unknown Album":
            artist = "Unknown Artist"
            mp3Base.setArtist(mp3, artist, debug = True)
            db[mp3]["Artist"] = artist
              
        continue

        albumArtist = db[mp3]["AlbumArtist"]
        if albumArtist == None or albumArtist == False or albumArtist == "False":
            mp3Base.setAlbumArtist(mp3, artist, debug = True)
            db[mp3]["AlbumArtist"] = artist
              
        continue
        if artist == "Unknown Artist" and albumArtist != "Unknown Artist":
            artist = albumArtist
            mp3Base.setArtist(mp3, artist, debug = True)
            db[mp3]["Artist"] = artist
        continue

        album = db[mp3]["Album"]
        if album == None or album == False or album == "False" or album == "Unknown Artist":
            album = "Unknown Album"
            mp3Base.setAlbum(mp3, album, debug = True)
            db[mp3]["Album"] = artist
              
    save(dbname, db, debug = True)
    end(startVal)        



###############################################################################
#
# Set Album Artist Tag (if missing)
#
###############################################################################
def findMissingTagMP3s(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    startVal = start()
    missingTags = {}
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 1000 == 0: inter(startVal, k+1, len(db))
        mp3data = db[mp3]

        artist      = mp3data["Artist"]
        albumArtist = mp3data["AlbumArtist"]
        title       = mp3data["Title"]
        album       = mp3data["Album"]
        trackNo     = mp3data["TrackNo"]  

        if artist == None or artist == False:
            print "Artist:",mp3
            if missingTags.get("Artist") == None:
                missingTags["Artist"] = []
            missingTags["Artist"].append(mp3)
                
        if albumArtist == None or albumArtist == False:            
            print "AlbumArtist:",mp3
            if missingTags.get("AlbumArtist") == None:
                missingTags["AlbumArtist"] = []
            missingTags["AlbumArtist"].append(mp3)
                
        if title == None or title == False:            
            print "Title:",mp3
            if missingTags.get("Title") == None:
                missingTags["Title"] = []
            missingTags["Title"].append(mp3)
                
        if album == None or album == False:            
            print "Album:",mp3
            if missingTags.get("Album") == None:
                missingTags["Album"] = []
            missingTags["Album"].append(mp3)
                
        if trackNo == None or trackNo == False:            
            print "TrackNo:",mp3
            if missingTags.get("TrackNo") == None:
                missingTags["TrackNo"] = []
            missingTags["TrackNo"].append(mp3)
            
    for k,v in missingTags.iteritems():
        if len(v) > 0:
            savename = setFile(getMusicDBDir(), "missingTags-"+k+".json")
            print "Saving",len(v),"missing",k,"tags to",savename
            save(savename, v)


              
    save(dbname, db, debug = True)
    end(startVal)          



###############################################################################
#
# Look for duplicates
#
###############################################################################
def findDuplicateMp3s(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    
    data = {}
    for k,mp3 in enumerate(db.keys()):
        size = db[mp3]["Size"]
        if data.get(size) == None:
            data[size] = {}
        artist = db[mp3]["AlbumArtist"]
        if data[size].get(artist) == None:
            data[size][artist] = {}
        data[size][artist][mp3] = 1


    rms = []
    for size,artistData in data.iteritems():
        for artist,mp3s in artistData.iteritems():
            if len(mp3s) > 1:
                for mp3 in mp3s:
                    test = mp3.replace(".mp3", " 1.mp3")
                    if test in mp3s:                        
                        rms.append(test)
                    test = mp3.replace(".mp3", " 2.mp3")
                    if test in mp3s:                        
                        rms.append(test)
    
    for mp3 in rms:
        removeFile(mp3, debug = True)
        del db[mp3]

    if len(rms) > 0:
        save(dbname, db, debug = True)


###############################################################################
#
# Analyze Missing Tags
#
###############################################################################
def replaceArtistName(inName, outName, callMissing = False, exact= True, debug = False):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    fixArtist = {}
    for mp3 in db.keys():
        #name = getBaseFilename(mp3)
        artist = makeStrFromUnicode(db[mp3]["AlbumArtist"])
        #artist = makeStrFromUnicode(db[mp3]["Artist"])
        if exact:
            if artist == inName and (artist.find(outName) == -1 or inName.find(outName) != -1):
                artist = artist.replace(inName, outName)
                fixArtist[mp3] = {"Artist": makeStrFromUnicode(artist)}
        else:
            if artist.find(inName) != -1 and (artist.find(outName) == -1 or inName.find(outName) != -1):
                artist = artist.replace(inName, outName)
                fixArtist[mp3] = {"Artist": makeStrFromUnicode(artist)}
            
    tag = "Artist"        
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixArtist),"fixes for",tag,"ID3 tag."
    save(ifile, fixArtist)
    
    if callMissing:
        setMissingTags("Artist")
        
        
def replaceCountry(inName, outName, callMissing = False, exact= True, debug = False):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    fixCountry = {}
    for mp3 in db.keys():
        #name = getBaseFilename(mp3)
        country = makeStrFromUnicode(db[mp3]["Country"])
        #artist = makeStrFromUnicode(db[mp3]["Artist"])
        if exact:
            if country == inName and (country.find(outName) == -1 or inName.find(outName) != -1):
                country = country.replace(inName, outName)
                fixCountry[mp3] = {"Country": makeStrFromUnicode(country)}
        else:
            if country.find(inName) != -1 and (country.find(outName) == -1 or inName.find(outName) != -1):
                country = country.replace(inName, outName)
                fixCountry[mp3] = {"Country": makeStrFromUnicode(country)}
            
    tag = "Country"        
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixCountry),"fixes for",tag,"ID3 tag."
    save(ifile, fixCountry)
    
    if callMissing:
        setMissingTags("Country")
    
    
def replaceAlbumName(artist, mediaType, inName, outName, callMissing = False, debug = False):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    fixAlbum = {}
    for mp3 in db.keys():
        if makeStrFromUnicode(artist) == makeStrFromUnicode(db[mp3]["AlbumArtist"]):
            album = makeStrFromUnicode(db[mp3]["Album"])
            if album.find(inName) != -1 and (album.find(outName) == -1 or inName.find(outName) != -1):
                album = album.replace(inName, outName)
                fixAlbum[mp3] = {"Album": makeStrFromUnicode(album)}
            
    tag = "Album"        
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixAlbum),"fixes for",tag,"ID3 tag."
    save(ifile, fixAlbum)
    
    if callMissing:
        setMissingTags("Album")
            


def analyzeMissingTrackNoTag(debug = True):    
    recs = findDBRecords(pattern="(German")
    setMp3Tags(recs, country="Germany")
    
    recs = findDBRecords(pattern="(Australian")
    setMp3Tags(recs, country="Aus")
    
    recs = findDBRecords(pattern="[Australian")
    setMp3Tags(recs, country="Aus")
    
    recs = findDBRecords(pattern="(AU ")
    setMp3Tags(recs, country="Aus")
    
    recs = findDBRecords(pattern="(Japan")
    setMp3Tags(recs, country="Japan")
    
    recs = findDBRecords(pattern="(EU")
    setMp3Tags(recs, country="EU")
    
    recs = findDBRecords(pattern="(EUR")
    setMp3Tags(recs, country="EU")
    
    recs = findDBRecords(pattern="(UK")
    setMp3Tags(recs, country="UK")
    
    recs = findDBRecords(pattern="[UK")
    setMp3Tags(recs, country="UK")
    
    recs = findDBRecords(pattern="Promo UK")
    setMp3Tags(recs, country="UK")
    
    recs = findDBRecords(pattern=" UK)")
    setMp3Tags(recs, country="UK")
    
    recs = findDBRecords(pattern=") UK")
    setMp3Tags(recs, country="UK")
    f()

    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    
    dbDir = getMusicDBDir()
    tag   = "Track"
    ifile = setFile(dbDir, "missingTags-"+tag+".json")
    mp3s  = get(ifile, debug)
    fixTrackNo = {}
    for mp3 in mp3s:
        name  = getBaseFilename(mp3)
        try:
            title       = db[mp3]["Title"]
            artist      = db[mp3]["Artist"]
            albumartist = db[mp3]["AlbumArtist"]
            #trackNo     = db[mp3]["TrackNo"]
        except:
            continue

        test = name
        if title != None and not isinstance(title, bool):
            test = test.replace(title, "").strip()
        if artist != None and not isinstance(artist, bool):
            test = test.replace(artist, "").strip()
        if albumartist != None and not isinstance(albumartist, bool):
            test = test.replace(albumartist, "").strip()
            
        try:
            int(test)
            fixTrackNo[mp3] = {"TrackNo": str(int(test))}
        except:
            continue
        
        if len(fixTrackNo) > 500: break
            
    tag = "TrackNo"        
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixTrackNo),"fixes for",tag,"ID3 tag."
    save(ifile, fixTrackNo)
    
        

def analyzeMissingTags(debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    finddb = db
    #finddb = findDBRecords(db = db, pattern=["Music/", "Vantoura"])
    fixArtist = {}
    fixTitle  = {}
    saveIt = False
    for mp3 in finddb.keys():
        if not isFile(mp3):
            del db[mp3]
            saveIt = True
            continue
        continue
        name = getBaseFilename(mp3)
        artist = db[mp3]["AlbumArtist"]
        if artist == None or artist == False or artist == "Unknown Artist" or artist == "Unknown Album":
            del db[mp3]
            removeFile(mp3)
            saveIt = True
            continue
        continue
        #artist = db[mp3]["Artist"]
        if artist == False:
            if not isFile(mp3):
                saveIt = True
                del db[mp3]
                continue
            fixArtist[mp3] = {"Artist": ""}
            continue
        #if artist.find(" Feat. ") != -1 or artist.find(" Feat ") != -1 or artist.find(" Ft. ") != -1:
        #if artist.find("Dj ") != -1:
        #if artist.find(",") != -1:
        #if artist.find(" With ") != -1:
        #if artist.find(" Vs ") != -1:
        if artist.find("Carl And The Passions") != -1:
        #if artist != artist.strip():
        #if artist.find(".com") != -1:
            #artist = db[mp3]["Artist"]
        #if artist.find("The The ") != -1:
        #if artist.find(", ") != -1: # or artist.find(" and ") != -1 or artist.find(" And ") != -1:
        #vals = name.split(" - ")
        #if len(vals) == 2 or True:

            if not isFile(mp3):
                del db[mp3]
                saveIt = True
            artist = db[mp3]["AlbumArtist"]
            artist = db[mp3]["Artist"]
            artist = artist.replace(", ", " & ")
            artist = artist.replace(",", " & ")
            artist = artist.replace(" and ", " & ")
            artist = artist.replace(" And ", " & ")
            artist = artist.replace("Dj ", "DJ ")
            artist = artist.replace(" Feat ", " & ")
            artist = artist.replace(" Feat. ", " & ")
            artist = artist.replace(" Ft. ", " & ")
            artist = artist.replace(" ft. ", " & ")
            artist = artist.replace(" With ", " & ")
            artist = artist.replace("The The ", "The ")
            artist = artist.replace("Jay Z", "Jay-Z")
            artist = artist.replace(" + ", " & ")
            artist = artist.replace("/", " & ")
            artist = artist.replace(" Vs. ", " vs. ")
            artist = artist.replace(" Vs ", " vs. ")
            artist = artist.replace(" VS ", " vs. ")
            artist = artist.replace(" vs ", " vs. ")
            artist = artist.replace("", "")
            artist = artist.strip()
            title  = db[mp3]["Title"]
            fixArtist[mp3] = {"Artist": makeStrFromUnicode(artist)}
            #if len(fixArtist) > 100: break
            continue
            #fixTitle[mp3] = {"Title": makeStrFromUnicode(title.title())}
            #artist = vals[0].strip()
            #title  = vals[1].strip()
            
            if db[mp3]["Artist"] == None or db[mp3]["Artist"] == False or db[mp3]["Artist"] == "To Do":
                fixArtist[mp3] = {"Artist": makeStrFromUnicode(artist)}
                if len(title) > 1:
                    if title[-1].isdigit():
                        title = title[:-1].strip()                    
                fixTitle[mp3] = {"Title": makeStrFromUnicode(title.title())}

    if saveIt:
        dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
        save(dbname, db, debug = True)

    tag = "Artist"        
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixArtist),"fixes for",tag,"ID3 tag."
    save(ifile, fixArtist)

    tag = "Title"
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fixTitle),"fixes for",tag,"ID3 tag."
    save(ifile, fixTitle)
        
    return
    
    fix = {}
    for k,mp3 in enumerate(missing):        
        name = getBaseFilename(mp3)
        if mp3.find("--") != -1:
            continue
        if name.count('_') >= 2:
            continue
        if name.find("Track") != -1:
            continue
        if name.find("perderti") != -1:
            continue
        if mp3.find("Manu ") != -1:
            continue
        if mp3.find("ben mio") != -1:
            continue
        if mp3.find("Gloria") != -1:
            continue
        if mp3.find("U2") != -1:
            continue
        vals = name.split()
        vals = [x.strip() for x in vals]
        
        print vals
        
        trkNo  = None
        album  = None
        artist = None
        albumArtist = None
        title  = None
        
        if len(vals) > 0:
            if not isFile(mp3):
                continue
            tags = mp3Base.getInfo(mp3)
            artist = tags.get("Artist")
            for i,val in enumerate(vals):
                try:
                    int(val)
                    trkNo = val
                    vals.remove(val)
                    break
                except:
                    continue

                
            for i,val in enumerate(vals):
                if artist:
                    if val == artist:
                        try:
                            vals.remove(val)
                            break
                        except:
                            continue

            if True:
                title = " ".join(vals)            
                nums = re.findall(r'\d+', title)
                for num in nums:
                    title.replace(num, "")
                title = title.strip()
                if len(title) > 5:
                    fix[mp3] = {"Title": makeStrFromUnicode(title.title())}
                    if len(fix) == 100: break
                continue

            #print vals
            if len(vals) >= 1:
                if len(vals) == 1:
                    title = vals[0]
                else:
                    try:
                        title = vals[-1]
                    except:
                        continue
                if len(title) > 5:
                    nums = re.findall(r'\d+', title)
                    #if len(nums) > 0: continue
                    fix[mp3] = {"Title": makeStrFromUnicode(title.title())}
                    if len(fix) % 25 == 0:
                        print len(fix)
                    if len(fix) == 100: break
                     
    
    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    print "Saving",len(fix),"fixes for",tag,"ID3 tag."
    save(ifile, fix)
    
    
def setMissingTags(tag, debug = True):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    ifile = setFile(getMusicDBDir(), "missingTags-"+tag+".yaml")
    fix = get(ifile, debug = True)
    saveIt = False
    for mp3,v in fix.iteritems():
        if isFile(mp3):
            if tag == 'title':
                title = v['Title']
                saveIt = True
                retval = mp3Base.setTitle(mp3, title, debug)
                db[mp3]["Title"] = title

            if tag == 'Country':
                country = v['Country']
                saveIt = True
                #retval = mp3Base.setArtist(mp3, artist, debug)
                retval = mp3Base.setCountry(mp3, country, debug)
                #db[mp3]["Artist"] = artist
                db[mp3]["Country"] = country

            if tag == 'Artist':
                artist = v['Artist']
                saveIt = True
                #retval = mp3Base.setArtist(mp3, artist, debug)
                retval = mp3Base.setAlbumArtist(mp3, artist, debug)
                #db[mp3]["Artist"] = artist
                db[mp3]["AlbumArtist"] = artist

            if tag == 'Album':
                album = v['Album']
                saveIt = True
                #retval = mp3Base.setArtist(mp3, artist, debug)
                retval = mp3Base.setAlbum(mp3, album, debug)
                #db[mp3]["Artist"] = artist
                db[mp3]["Album"] = album

            if tag == 'TrackNo':
                trackNo = v['TrackNo']
                saveIt = True
                #retval = mp3Base.setArtist(mp3, artist, debug)
                retval = mp3Base.setTrackNo(mp3, trackNo, debug)
                #db[mp3]["Artist"] = artist
                db[mp3]["TrackNo"] = trackNo

    if saveIt:
        dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
        save(dbname, db, debug = True)


###############################################################################
#
# Set Tags for mp3
#
###############################################################################
def setMp3Tag(mp3, artists = None, artist = None, albumArtist = None, 
              album = None, disc = None, country = None, debug = False):
    if not isFile(mp3):
        print mp3,"is not available."
        return
    
    if debug:
        print "Setting ID3 tags for",mp3
    
    if artists:
        mp3Base.setArtist(mp3, makeUnicode(artists), debug = True)
        mp3Base.setAlbumArtist(mp3, makeUnicode(artists), debug = True)
        
    if artist:
        mp3Base.setArtist(mp3, makeUnicode(artist), debug = True)
        
    if albumArtist:
        mp3Base.setAlbumArtist(mp3, makeUnicode(albumArtist), debug = True)
        
    if album:
        mp3Base.setAlbum(mp3, makeUnicode(album), debug = True)
        
    if disc:
        mp3Base.setDiscNo(mp3, makeUnicode(disc), debug = True)
        
    if country:
        mp3Base.setCountry(mp3, makeUnicode(country), debug = True)
                
    if debug:
        print mp3Base.getInfo(mp3)
        

def setMp3Tags(mp3s, artists = None, artist = None, albumArtist = None, 
               album = None, disc = None, country = None, debug = False):
    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    if isinstance(mp3s, dict):
        mp3s = mp3s.keys()

    for i,mp3 in enumerate(mp3s):
        if (i+1) % 100 == 0: print '---> ',i+1,"/",len(mp3s)
        if db.get(mp3) == None:
            print "mp3:",mp3,"not in DB. Adding it!"
            db[mp3] = mp3Base.getInfo(mp3)            
        setMp3Tag(mp3, artists, artist, albumArtist, album, disc, country, debug)
        db[mp3] = mp3Base.getInfo(mp3)
    
    save(dbname, db, debug = True)
