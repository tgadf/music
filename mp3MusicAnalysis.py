#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 14:06:38 2017

@author: tgadfort
"""

import sys
from filecmp import cmp
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from mp3iTunes import getiTunesDir, getMusicArtistDB, saveMusicArtistDB, getMusicDBDir
from mp3ArtistAnalysis import findSongArtists, getArtists, noDiscogEntry
from DiscogBase import getArtistNameIDs, getDiscIDHashMod, getArtistNames
from DiscogCollections import downloadSearchResults
from DiscogPath import getArtistsDBDir

from fileio import save, get
from fsio import setFile, setDir, isFile, mkSubDir, moveFile, removeFile
from fileinfo import getBasename, getBaseFilename, getSize
from search import findNearest, findPatternExt
from strops import makeStrFromUnicode, nice, getSaveName
from timing import start,inter,end






###############################################################################
# Basic Music DB File
###############################################################################
def getDiscogArtistMusicMatchDB(debug = True):
    dbDir    = getMusicDBDir()
    savename = setFile(dbDir, "discogArtistMusicMatchDB.yaml")
        
    if debug:
        print "Loading",savename
    db = get(savename)
    if debug:
        print "Loading",savename,"... Found",len(db),"entries."
    return db


def saveDiscogArtistMusicMatchDB(db, debug = True):
    dbDir    = setDir(getiTunesDir(), "MusicDB")
    savename = setFile(dbDir, "discogArtistMusicMatchDB.yaml")
    save(savename, db)
    
    
    

def findMp3WithoutArtistDiscogMatch(maxMp3s = 100):
    useCleanDirectories = True
    musicArtistNamesDB  = getMusicArtistDB(useCleanDirectories, debug = True)

    musicArtistNames = [makeStrFromUnicode(x) for x in musicArtistNamesDB.keys()]
    musicArtistNames = [x for x in musicArtistNames if x != None]


    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)

    startVal = start()
    noMatches = {}
    for k,mp3 in enumerate(db.keys()):
        if (k+1) % 1000 == 0: inter(startVal, k+1, len(db))
        mp3data = db[mp3]

        artist      = makeStrFromUnicode(mp3data["Artist"])
        albumArtist = makeStrFromUnicode(mp3data["AlbumArtist"])

        if musicArtistNamesDB.get(artist) == None:
            print "Somehow",artist,"is not a key in the music artist DB!"
            print findNearest(artist, musicArtistNames, 10, 0.8, debug = False)
            f()            
        if musicArtistNamesDB[artist].get("DiscID") == None:
            noMatches[mp3] = db[mp3]
            if len(noMatches) >= maxMp3s: break

        if musicArtistNamesDB.get(albumArtist) == None:
            print "Somehow",albumArtist,"is not a key in the music artist DB!"
            print findNearest(albumArtist, musicArtistNames, 10, 0.8, debug = False)
            f()            
        if musicArtistNamesDB[albumArtist].get("DiscID") == None:
            noMatches[mp3] = db[mp3]
            if len(noMatches) >= maxMp3s: break
            

    for k,v in noMatches.iteritems():
        print k
        
        

            


def matchMusicArtistsToDiscogsDB(matchdegree = 1.0, debug = False, matchToKnown = False):
    useCleanDirectories = True
    musicArtistNames  = getMusicArtistDB(useCleanDirectories, debug = True)
        
    if matchToKnown == True:
        print "Using known matched artists as DB."
        discogArtistNames = {}
        for i,artist in enumerate(musicArtistNames.keys()):            
            if musicArtistNames[artist]["DiscID"] != None:
                discogArtistNames[artist] = musicArtistNames[artist]["DiscID"]
    else:
        print "Using all Discog artists as DB."
        discogArtistNames = getArtistNameIDs(debug = True)
    
    discogArtists = [makeStrFromUnicode(x) for x in discogArtistNames.keys()]
    discogArtists = [x for x in discogArtists if x != None]
    print "There are",len(discogArtists),"discog artist names."
    
    match = [0, 0, 0, 0]
    nomatch = {}
    nearMatches = {}
    startVal = start()
    for i,artist in enumerate(musicArtistNames.keys()):
        
        ################################
        # Check for previous match
        ################################
        discIDmatch = musicArtistNames[artist]["DiscID"]
        if discIDmatch != None:
            if isinstance(discIDmatch, list):
                if all(discIDmatch):
                    match[0] += 1
                    continue
            else:
                match[0] += 1
                continue


        ################################
        # Debugging
        ################################
        if matchToKnown == False:
            if (i+1) % 250 == 0:
                inter(startVal, i+1, len(musicArtistNames))
            #if (i+1) % 1000 == 0:
            #    saveMusicArtistDB(musicArtistNames, useCleanDirectories, debug = True)
        
        
        matchVal    = True
        discIDmatch = []
        artistNames = [makeStrFromUnicode(x) for x in getArtists(findSongArtists(artist))]        
        for j,musicArtistName in enumerate(artistNames):
            if musicArtistName == None:
                matchVal = False
                match[3] += 1
                nomatch[artist] = 1
                continue

            if discogArtistNames.get(musicArtistName) != None:
                discIDmatch.append(discogArtistNames[musicArtistName])
                continue
            
            if noDiscogEntry(musicArtistName):
                discIDmatch.append(None)
                continue
    
            if matchdegree >= 1.0:
                if discogArtistNames.get(musicArtistName):
                    discIDmatch.append(discogArtistNames[musicArtistName])
                else:
                    discIDmatch.append(None)
                    #print "    No Match --> ",musicArtistName
                    nomatch[musicArtistName] = 1
            else:
                discIDmatch.append(None)
                matchVal = findNearest(musicArtistName, discogArtists, 2, matchdegree, debug = False)
                if len(matchVal) > 0:
                    nearMatches[musicArtistName] = [makeStrFromUnicode(x) for x in matchVal]
                    match[1] += 1
                    #print "  Near Match --> ",musicArtistName,"  <===>  ",nearMatches[musicArtistName]
                    for k in range(len(matchVal)):
                        print "replaceArtistName(\""+musicArtistName+"\", \""+nearMatches[musicArtistName][k]+"\")"                    
                else:
                    #match[2] += 1
                    nomatch[musicArtistName] = 1
                    #nomatch[artist] = 1
                    #print "--->",musicArtistName
                    #print "    No Match --> ",musicArtistName
                    

        if all(discIDmatch):
            musicArtistNames[artist]["DiscID"] = discIDmatch
            if debug and False:
                print "  Full Match --> ",musicArtistName
            match[0] += 1
        else:
            match[2] += 1
            #print artist

    end(startVal)

    saveMusicArtistDB(musicArtistNames, useCleanDirectories, debug = True)

    print "Found",len(musicArtistNames),"music artist names."
    print "Found",match[0],"matched music artist names with discog artist names."
    print "Found",match[1],"near matched music artist names with discog artist names."
    print "Found",match[2],"unmatched music artist names with discog artist names."
    print "Found",match[3],"errors in music artist names."

    if len(nomatch) > 0:
        savename = setFile(getMusicDBDir(), "artistsWithNoDiscogMatch.yaml")         
        print "Saving",len(nomatch),"artists with no match to",savename
        save(savename, nomatch)
    
    if len(nearMatches) > 0:
        savename = setFile(getMusicDBDir(), "artistsWithNearDiscogMatch.yaml")         
        print "Saving",len(nearMatches),"artists with near match to",savename
        save(savename, nearMatches)
    
    
    
def createDiscogArtistMatchesDB(coeff = None, debug = True):
    useCleanDirectories = True
    musicArtistNames  = getMusicArtistDB(useCleanDirectories, debug = True)
    discogArtistNames = getArtistNames(debug = True)
    
    noMatches = {}
    discIDs = {}
    if debug:
        print "Finding matched artists."
    for i,artist in enumerate(musicArtistNames.keys()):
        musicArtistData = None
        if coeff:
            if artist.find(coeff) != -1:
                musicArtistData = musicArtistNames[artist]
        else:
            musicArtistData = musicArtistNames[artist]
        if musicArtistData == None:
            continue
        discIDmatch = musicArtistData["DiscID"]
        if discIDmatch == None:
            continue
        if isinstance(discIDmatch, list):
            for discID in discIDmatch:
                if discID != None:
                    modValue  = getDiscIDHashMod(discID)
                    if discIDs.get(modValue) == None:
                        discIDs[modValue] = {}
                    discIDs[modValue][discID] = 1
        
    if debug:
        print "Finding matched artists' discog data."
    discogMatches = {}
    for modValue,modData in discIDs.iteritems():
        modDBfile = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
        modDB     = get(modDBfile, debug = True)
        for discID in modData.keys():
            artistData = modDB.get(discID)
            if artistData == None:
                print "Could not find discID:",discID
                noMatches[discogArtistNames.get(discID)] = 1
            else:
                discogMatches[discID] = modDB.get(discID)
        if debug:
            print "  -->",modValue,"\t",len(modData),"\t",len(discogMatches)
                
    saveDiscogArtistMusicMatchDB(discogMatches, debug)



def matchMusicAlbumsToDiscogsDB(matchdegree = 1.0, debug = False, matchToKnown = False):
    useCleanDirectories = True
    musicArtistDB       = getMusicArtistDB(useCleanDirectories, debug = True)
    discogArtistDB      = getDiscogArtistMusicMatchDB(debug = True)
    discogArtistNames   = getArtistNames(debug = True)
    
    nearMatches = {}
    nMatches    = 0
    noMatches   = {}
    for i,artist in enumerate(musicArtistDB.keys()):
                        
        ################################
        # Check for previous match
        ################################
        musicArtistData = musicArtistDB[artist]
        discIDmatch = musicArtistData["DiscID"]
        if discIDmatch == None:
            continue
        if isinstance(discIDmatch, list):
            for discID in discIDmatch:
                #print "   :",discID,'\t',discogArtistNames.get(discID)
                discogArtistData = discogArtistDB.get(discID)
                if discogArtistData == None:
                    noMatches[discogArtistNames.get(discID)] = 1
                    #noMatches[artist] = 1
                    #print "No data for artist:",artist
                    continue
            
                discogArtistMediaData = discogArtistData["Media"]
                musicArtistAlbumsData = musicArtistData["Albums"]
                
                #Albums
                #Singles & EPs
                #Compilations
                #Instruments & Performance
                #Miscellaneous
                #Writing & Arrangement
                #Production
                #Vocals
                #Technical
                #Visual
                #DJ Mixes
                #Videos
                #Remix
                #Featuring & Presenting
                #Management
                #Mixes
                #Acting, Literary & Spoken
                #Conducting & Leading

                nAlbumMatches = 0
                for musicAlbumName,musicAlbumData in musicArtistAlbumsData.iteritems():
                    albumKey       = musicAlbumName
                    musicAlbumName = makeStrFromUnicode(musicAlbumName)
                        
                    if musicAlbumData["ID"] != None: 
                        if debug:
                            print "\t----> Full Match:",artist,'\t  ',musicAlbumName                                
                        nAlbumMatches += 1
                        continue
                
                    mediaTypes=["Albums", "Singles & EPs", "Compilations"]
                    for mediaType in mediaTypes:
                        discogArtistAlbumData = discogArtistMediaData.get(mediaType)
                        if discogArtistAlbumData == None:
                            continue
    
                        discogArtistAlbums   = [makeStrFromUnicode(v["Album"]) for k,v in discogArtistAlbumData.iteritems()]
                        discogArtistAlbumIDs = discogArtistAlbumData.keys()
                        discogArtistAlbums   = dict(zip(discogArtistAlbums, discogArtistAlbumIDs))
                    
                        if matchdegree >= 1.0:
                            if discogArtistAlbums.get(musicAlbumName):
                                musicArtistDB[artist]["Albums"][albumKey]["ID"] = discogArtistAlbums[musicAlbumName]
                                nAlbumMatches += 1
                                if debug:
                                    print "\t----> Full Match:",artist,'\t  ',musicAlbumName
                        else:
                            num = 1
                            if matchdegree < 0.8:
                                num = 3
                            elif matchdegree < 0.7:
                                num = 5
                            matchVal = findNearest(musicAlbumName, discogArtistAlbums.keys(), num, matchdegree, debug = False)
                            if len(matchVal) > 0:
                                if nearMatches.get(artist) == None:
                                    nearMatches[artist] = {}
                                nearMatches[artist][musicAlbumName] = [makeStrFromUnicode(x) for x in matchVal]
                                for k in range(len(matchVal)):
                                    print "replaceAlbumName(\""+artist+"\", \""+mediaType+"\", \""+musicAlbumName+"\", \""+nearMatches[artist][musicAlbumName][k]+"\", callMissing = True)"
                                if debug:
                                    print "\t----> Near Match:",artist,'\t  ',nearMatches[artist][musicAlbumName]
    


                nMatches += nAlbumMatches
                if nAlbumMatches > 0 and matchdegree >= 1.0:
                    print nice(artist,30),' ',nice(discogArtistNames.get(discID),20),' ',
                    print nice(discID,10),' ',
                    #print musicArtistData["DiscID"],
                    print nice(nAlbumMatches,4),"/",nice(len(musicArtistAlbumsData),4),"/",
                    print nice(len(discogArtistAlbums),4)


    if nMatches > 0:
        print "Found",nMatches,"album matches."
        saveMusicArtistDB(musicArtistDB, useCleanDirectories, debug = True)
        
    if len(nearMatches) > 0:
        savename = setFile(getMusicDBDir(), "albumsWithNearDiscogMatch.yaml")         
        print "Saving",len(nearMatches),"albums with near match to",savename
        save(savename, nearMatches)
        
    if len(noMatches) > 0:
        savename = setFile(getMusicDBDir(), "albumsWithNoDiscogMatch.yaml")         
        print "Saving",len(noMatches),"artists with no match to",savename
        save(savename, noMatches)

    
    

###############################################################################
#
# Re-organize Music Files
#
###############################################################################
def ReoganizeMusicFiles(debug = True):
    useCleanDirectories = True
    musicArtistDB       = getMusicArtistDB(useCleanDirectories, debug = True)

    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    db = get(dbname, debug = True)
    
    musicDir = "/Volumes/Music/iTunes Matched/iTunes Media/Music"
    
    moveList = {}
    
    for k,mp3 in enumerate(db.keys()):
        if not isFile(mp3):
            del db[mp3]
            continue
        
        artist  = db[mp3]["AlbumArtist"]
        album   = db[mp3]["Album"]
        track   = db[mp3]["TrackNo"] 
        disc    = db[mp3]["DiscNo"]
        title   = db[mp3]["Title"]
        country = db[mp3]["Country"]
        
        #if artist.startswith("A") == False:
        #    continue
        
        try:
            artistName = makeStrFromUnicode(artist)
        except:
            artistName = artist
        
        try:
            albumName = makeStrFromUnicode(album)
        except:
            albumName = artist

        if musicArtistDB.get(artistName) == None:
            print "Could not find",artist,"in music artist DB"
            continue
        
        if musicArtistDB.get(artistName):
            artistData = musicArtistDB.get(artistName)
            #discID = musicArtistDB[artist].get("ID")
            if artistData["Albums"].get(albumName):
                albumData = artistData["Albums"][albumName]
                code = albumData.get("ID")
                if code:
                    try:
                        trkNo = int(track)
                        if trkNo > 0:
                            if trkNo < 10:
                                trkNo = "0"+str(trkNo)
                            else: 
                                trkNo = str(trkNo)
                        else:
                            trkNo = None
                    except:
                        trkNo = None

                    if isinstance(title, bool) or title == None:
                        title = None
                    else:
                        title = makeStrFromUnicode(title)

                    fName = None
                    if title != None and trkNo != None:
                        fName = " - ".join([trkNo,title])
                        
                    try:
                        if int(disc) > 0:
                            discNo = getSaveName(str(int(disc)))
                            discNo = "Disc "+discNo
                        else:
                            discNo = None
                    except:
                        discNo = None


                    artistDir = getSaveName(makeStrFromUnicode(artist))
                    if country:
                        if country == "US":
                            albumDir  = getSaveName(makeStrFromUnicode(album))
                        else:
                            albumDir = makeStrFromUnicode(album)+" ("+makeStrFromUnicode(country)+")"
                            albumDir  = getSaveName(albumDir)
                    else:
                        albumDir  = getSaveName(makeStrFromUnicode(album))
                        
                        
                    outdir    = mkSubDir(musicDir, artistDir)
                    outdir    = mkSubDir(outdir, albumDir)
                    if discNo:
                        outdir    = mkSubDir(outdir, discNo)
                    
                    #print outdir
                    #print getBasename(mp3)
                    #print type(outdir)
                    #print type(getBasename(mp3))
                    dst = setFile(outdir, makeStrFromUnicode(getBasename(mp3)))
                    if isFile(dst):
                        if cmp(mp3, dst):
                            removeFile(mp3, debug = True)
                            del db[mp3]
                            continue                            
                        dstSize = getSize(dst)
                        mp3Size = getSize(mp3)
                        if mp3Size > dstSize:
                            moveFile(mp3, dst, debug = True, forceMove = True)
                            del db[mp3]
                        else:
                            removeFile(mp3, debug = True)
                            del db[mp3]
                    else:
                        moveFile(mp3, dst, debug = True)                    
                        del db[mp3]
                    continue
                    
                    if moveList.get(artistDir) == None:
                        moveList[artistDir] = {}
                    albumDir  = getSaveName(makeStrFromUnicode(album))
                    if moveList[artistDir].get(albumDir) == None:
                        moveList[artistDir][albumDir] = {}
                        print artistDir,'\t\t',albumDir
                    if discNo:
                        if moveList[artistDir][albumDir].get(discNo) == None:
                            moveList[artistDir][albumDir][discNo] = {}

                    if fName:
                        if discNo:
                            moveList[artistDir][albumDir][discNo][mp3] = fName
                        else:
                            moveList[artistDir][albumDir][mp3] = fName
                    else:
                        filename = getBaseFilename(mp3)
                        if discNo:
                            moveList[artistDir][albumDir][discNo][mp3] = filename
                        else:
                            moveList[artistDir][albumDir][mp3] = filename
                                            
    savename = setFile(getMusicDBDir(), "moveList.yaml")         
    print "Saving",len(moveList),"albums with near match to",savename
    save(savename, moveList, debug = True)

    dbname = setFile(getMusicDBDir(), "iTunes Consolidate.json")
    save(dbname, db, debug = True)
    
        
    

###############################################################################
#
# Download DBs
#
###############################################################################
def findDiscogIDsToDownload(debug = True):
    savename = setFile(getMusicDBDir(), "artistIDsWithNoDiscogMatch.yaml")         
    noData   = get(savename)
    discogArtistNames   = getArtistNames(debug = debug)
    for discID in noData.keys():
        artist = discogArtistNames.get(discID)
        print discID,artist
        continue
        if artist:
            downloadSearchResults(artist, debug = True)


def findDiscogArtistsToDownload():
    savename = setFile(getMusicDBDir(), "artistsWithNoDiscogMatch.yaml")         
    #savename = setFile(getMusicDBDir(), "albumsWithNoDiscogMatch.yaml")
    nomatch  = get(savename)
    for i,artist in enumerate(nomatch.keys()):
        print i,"/",len(nomatch),"\t",artist
        #if artist.find("&") != -1: continue
        downloadSearchResults(artist, debug = True)
    
    

def findAlbumsWithoutArtistDiscogMatches(useCleanDirectories = True):
    dbDir = setDir(getiTunesDir(), "MusicDB")
    musicDBs = findPatternExt(dbDir, pattern="iTunes", ext=".json")

    musicArtistNames  = getMusicArtistDB(useCleanDirectories, debug = True)
    
    albumsNoMatch = {}

    startVal = start()
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
            if musicDB.find("Errors") != -1:
                continue
        
        db = get(musicDB)
        
        for k, mp3 in enumerate(db.keys()):
            mp3data = db[mp3]
            if (k+1) % 10000 == 0: inter(startVal, k+1, len(db))

            artist = makeStrFromUnicode(mp3data["Artist"])
            if musicArtistNames.get(artist) == None:
                raise ValueError("Not sure how this happened:",artist)
            if musicArtistNames[artist]["DiscID"] == None:
                album  = makeStrFromUnicode(mp3data["Album"])
                if albumsNoMatch.get(album) == None:                    
                    albumsNoMatch[album] = {}
                if albumsNoMatch[album].get(artist) == None:
                    albumsNoMatch[album][artist] = []
                albumsNoMatch[album][artist].append(mp3)
    

    
    savename = setFile(getMusicDBDir(), "albumsWithNoDiscogArtistMatch.yaml")         
    print "Saving",len(albumsNoMatch),"albums with no match to",savename
    save(savename, albumsNoMatch)