 #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 14:54:44 2017

@author: tgadfort
"""

import sys
from urllib import pathname2url
from collections import Counter
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
from fileio import get, save 
from fileinfo import getBaseFilename, getBasename, getDirname, getSize
from fsio import setSubDir, isDir, setFile, moveFile, isFile, removeFile, mkDir, setDir
from search import findSubExt, findExt, findDirs, findWalkExt
from strops import makeStrFromUnicode, makeUnicode
from timing import start,inter,end
    
from htmlParser import getHTML
from download import getData

from DiscogBase import getDiscIDHashMod, getArtistDB
from albumdata import parse, getAlbumCode
from DiscogPath import getArtistsDBDir, getAlbumsDir, getAlbumsDBDir, getSearchDir
from mp3iTunes import getMusicDBDir


################################################################################
#
# getAlbums()
#
################################################################################
def createAlbumDownloadList(useKnown = False, maxDownload = 3, debug = False, forceWrite = False):
    
    toGet = {}

    startVal = start()
    
    if useKnown:
        dbDir    = getMusicDBDir()
        dbname   = setFile(dbDir, "discogArtistMusicMatchDB.yaml")
        end(startVal)
        startVal = start()
        artistDB = get(dbname, debug = True)
        for i,discID in enumerate(artistDB.keys()):
            if (i+1) % 100 == 0: inter(startVal, i+1, len(artistDB))
            artistData = artistDB[discID]
            modValue   = getDiscIDHashMod(discID)
            artistDir  = setSubDir(getAlbumsDir(), [str(modValue), discID])
            if not isDir(artistDir):
                mkDir(artistDir)
            media      = artistData.get("Media")
            if media == None:
                continue
            albums     = media.get("Albums")
            if albums == None:
                continue
            known = 0
            for code,albumData in albums.iteritems():
                albumFile = setFile(artistDir, str(code)+".p")
                if isFile(albumFile):
                    known += 1
                    continue
                if toGet.get(discID) == None:
                    toGet[discID] = {}
                if len(toGet[discID])+known > maxDownload:
                    break
                toGet[discID][code] = albumData["URL"]
                if len(toGet) % 250 == 0:
                    savename = setFile(getAlbumsDir(), "toGet.p")
                    save(savename, toGet, debug = True)
    else:
        dbnames  = findWalkExt(getArtistsDBDir(), ext=".p")
        for dbname in dbnames:
            artistDB = get(dbname, debug = True)
            for discID in artistDB.keys():
                artistData = artistDB[discID]
                modValue   = getDiscIDHashMod(discID)
                artistDir  = setSubDir(getAlbumsDir(), [str(modValue), discID])
                if not isDir(artistDir):
                    mkDir(artistDir)
                media      = artistData.get("Media")                
                if media == None:
                    continue
                
                mediaTypes=["Albums", "Compilations"]
                for mediaType in mediaTypes:
                    albums     = media.get(mediaType)
                    if albums == None:
                        continue
                    known = 0
                    for code,albumData in albums.iteritems():
                        if known > maxDownload:
                            break
                        albumFile = setFile(artistDir, str(code)+".p")
                        if isFile(albumFile):
                            known += 1
                            continue
                        if toGet.get(discID) == None:
                            toGet[discID] = {}
                        if len(toGet[discID])+known > maxDownload:
                            break
                        toGet[discID][code] = albumData["URL"]
                        if len(toGet) % 2500 == 0:
                            savename = setFile(getAlbumsDir(), "toGet.p")
                            save(savename, toGet, debug = True)
    
    savename = setFile(getAlbumsDir(), "toGet.p")
    save(savename, toGet, debug = True)

    end(startVal)


def downloadAlbumsFromList(dtime = 4, debug = False, forceWrite = False):

    outdir   = getAlbumsDir()
    baseURL  = u"https://www.discogs.com"
    useSafari = True
    
    
    savename = setFile(getAlbumsDir(), "toGet.p")
    toGet = get(savename, debug = True)
    print "Downloading",len(toGet),"new disc IDs."

    startVal = start()

    for i,discID in enumerate(toGet.keys()):
        
        if (i+1) % 100 == 0: inter(startVal, i+1, len(toGet))

        modValue   = getDiscIDHashMod(discID)
        artistDir  = setSubDir(outdir, [str(modValue), discID])
                    
        j = 0
        for code,href in toGet[discID].iteritems():
            j += 1
            if j % 5 == 0:
                print "  ----->",j,"/",len(toGet[discID])
            savename = setFile(artistDir, str(code)+".p")            
            if isFile(savename):
                continue
        
            URL = baseURL + href
            URL = baseURL + pathname2url(makeUnicode(href).encode("utf-8"))
            #URL = URL + "?sort=year%2Casc&limit=500&page=1"

            retval   = False
            attempts = 0
            while not retval and attempts < 3:
                retval = getData(base=URL, suburl=None, extra=None, savename=savename, 
                                 useSafari=useSafari, dtime=dtime+2*attempts, debug=debug)
                attempts += 1
           
    end(startVal)
    


################################################################################
#
# Album Data
#
################################################################################
def parseAlbums(modValues = None, debug = False, forceWrite = False):
    if modValues == None:
        modValues = findDirs(getAlbumsDir())
        modValues = [getBasename(x) for x in modValues]
    else:
        if not isinstance(modValues, list):
            modValues = [modValues]

    print "Creating DBs for the following mod values:",modValues
    
    startVal  = start()
    for i,modValue in enumerate(modValues):
        inter(startVal, i+1,len(modValues))
        albumDBfile = setFile(getAlbumsDBDir(), str(modValue)+"-DB.p")
        albumDB     = get(albumDBfile)

        modValueDir = setDir(getAlbumsDir(), str(modValue))
        artistDirs  = findDirs(modValueDir)
        for j,artistDir in enumerate(artistDirs):
            if (j+1) % 10 == 0: inter(startVal, j+1, len(artistDirs))
            discID   = getBasename(artistDir)
            artistDB = albumDB.get(discID)
            if artistDB == None:
                albumDB[discID] = {}
            
            for album in findExt(artistDir, ext='.p'):
                if getSize(album) < 50:
                    tmp = get(album)
                    if isinstance(tmp, dict):
                        if tmp.get("Album") and tmp.get("Artist"):
                            removeFile(album, debug = True)
                    continue
                
                code = getBaseFilename(album)
                if albumDB[discID].get(code) and forceWrite == False:
                    continue

                bsdata    = getHTML(album)
                albumData = parse(bsdata, filename = album)

                albumDB[discID][code] = albumData

        save(albumDBfile, albumDB, debug = True)

    end(startVal)



################################################################################
#
# Find Artists from Albums
#
################################################################################
def findArtistsFromAlbums(debug = False):
    artistDB = getArtistDB()
    
    toGet    = {}
    toGetCntr = Counter()
    startVal = start()
    albumDBfiles = findExt(getAlbumsDBDir(), ext='.p')
    for i,albumDBfile in enumerate(albumDBfiles):
        #modValue = getBaseFilename(albumDBfile)
        if (i+1) % 5 == 0: inter(startVal, i+1, len(albumDBfiles))
        albumDB = get(albumDBfile)
        for discID,artistData in albumDB.iteritems():
            for code,albumData in artistData.iteritems():
                if albumData == None:
                    #print "No albumData for discID/code:",discID,code
                    continue
                albumArtists = albumData["Artist"]
                if albumArtists == None:
                    #print "No artist for discID/code:",discID,code
                    continue
                for albumArtist in albumArtists:
                    albumArtistID = albumArtist[2]
                    if albumArtistID:
                        if artistDB.get(albumArtistID) == None:
                            toGetCntr[albumArtistID] += 1
                            if toGet.get(albumArtistID) == None:
                                toGet[albumArtistID] = makeStrFromUnicode(albumArtist[1])
                                #print modValue,'\t',albumArtistID,'\t',makeStrFromUnicode(albumArtist[1])
                            
                creditArtists = albumData.get("Credits")
                if creditArtists == None:
                    #print "No credit for discID/code:",discID,code
                    continue
                for creditType,creditData in creditArtists.iteritems():
                    for creditArtist in creditData:
                        creditArtistID = creditArtist[2]
                        if creditArtistID:
                            if artistDB.get(creditArtistID) == None:
                                toGetCntr[creditArtistID] += 1
                                if toGet.get(creditArtistID) == None:
                                    toGet[creditArtistID] = makeStrFromUnicode(creditArtist[1])
                                    #print modValue,'\t',creditArtistID,'\t',makeStrFromUnicode(creditArtist[1])

    for item in toGetCntr.most_common():
        val = item[0]
        cnt = item[1]
        if cnt < 5:
            del toGet[val]

    savename = setFile(getSearchDir(), "toGet.yaml")    
    print "Downloading",len(toGet),"new disc IDs."
    save(savename, toGet, debug = True)
                    
    end(startVal)


################################################################################
#
# Renames
#
################################################################################
def createAlbumDBs(debug = False):
    albumsDir = getAlbumsDBDir()
    for modDir in findDirs(albumsDir):
        modValue = getBasename(modDir)
        data = {}
        for discIDDir in findDirs(modDir):
            discID = getBasename(discIDDir)
            data[discID] = {}
            albums = findWalkExt(discIDDir, ext='.p')
            for album in albums:
                albumData = get(album)
                code      = getAlbumCode(albumData['URL'])
                data[discID][code] = albumData

        dbname = setFile(albumsDir, modValue+"-DB.p")
        save(dbname, data, debug = True)
        
    
def renameAlbumsDB():
    albumsDir = getAlbumsDBDir()
    for modDir in findDirs(albumsDir):
        print modDir
        for discIDDir in findDirs(modDir):
            albums = findSubExt(discIDDir, '*', ext='.p')
            for album in albums:

                try:
                    code = str(int(getBaseFilename(album)))
                    continue
                except:
                    albumData = get(album)
                    
                try:
                    code      = getAlbumCode(albumData['URL'])
                except:
                    #removeFile(album, debug = True)
                    continue

                if code:
                    albumID = code
                    outfile = setFile(getDirname(album), albumID+".p")
                    if isFile(outfile):
                        #removeFile(album, debug = True)
                        continue
                        
                    moveFile(album, outfile, debug = False)
                    
                    
                    
def renameAlbums():
    albumsDir   = getAlbumsDir()
    for modDir in findDirs(albumsDir):
        for discIDDir in findDirs(modDir):
            albums = findWalkExt(discIDDir, ext='.p')
            for album in albums:
                fname   = getBasename(album)
                outfile = setFile(discIDDir, fname)
                moveFile(album, outfile, debug = True)

    return
    
    for modDir in findDirs(albumsDir):
        for discIDDir in findDirs(modDir):
            albums = findSubExt(discIDDir, '*', ext='.p')
            for album in albums:
                code = getBaseFilename(album)
                try:
                    int(code)
                    continue
                except:
                    bsdata    = getHTML(get(album), allowError = True)
                    if bsdata == None:
                        removeFile(album, debug = True)
                        continue
                    albumData = parse(bsdata)
                    if albumData == None:
                        removeFile(album, debug = True)
                        continue
                    code      = getAlbumCode(albumData['URL'])
                
                if code:
                    albumID = code
                    outfile = setFile(getDirname(album), albumID+".p")
                    if isFile(outfile):
                        removeFile(album, debug = True)
                        continue
                        
                    moveFile(album, outfile, debug = True)