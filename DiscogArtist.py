#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 21:19:13 2017

@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fileio import get, save
from fileinfo import getBasename, getSize, getBaseFilename
from fsio import removeFile, mkSubDir, moveFile, setDir, setFile, setSubFile, isDir, isFile
from glob import glob
from os.path import join, getsize
from hashlib import sha1
from math import ceil

import artistdata
from strops import getSaveName, nice, nicerate, makeStrFromUnicode, makeUnicode
from search import findNearest, findMatchingWord, findPatternExt, findSubExt, findExt, findAll
from htmlParser import getHTML
from download import getData

from timing import start,inter,end
from collections import Counter
from DiscogDownload import checkFileSize
from DiscogBase import saveBaseDB, getArtistDB, getKnownArtistIDs, getDiscIDHashMod, getBaseDB, saveNewDBs
from artistdata import getArtistDiscID, parse
from DiscogPath import getBaseDBDir, getDiscogDir, getMusicDir, getArtistsDir, getArtistsDBDir, getArtistsExtraDir

################################################################################
#
# Step 1: processArtistDBFiles(), findArtists()
# Step 2: downloadArtists()
# Step 3: 
#
################################################################################



################################################################################
#
# Download Artist Files
#
################################################################################
def downloadArtists(minCounts = 1, debug = False, forceWrite = False):
    basedir      = getBaseDBDir()    
    countsname   = setFile(basedir, "artistFrequency.yaml")
    artistCounts = Counter(get(countsname))
    
    discdbname   = setFile(basedir, "downloadedArtists.yaml")
    discdb       = get(discdbname)
    

    print "Finding artists to download..."
    artistsToGet = []
    for item in artistCounts.most_common():
        href = makeUnicode(item[0])
        cnt  = item[1]
        if cnt < minCounts: continue
        discID = getArtistDiscID(href)
        if discdb.get(discID): continue
        artistsToGet.append(href)

    print "Finding artists to download...",len(artistsToGet)
        
    if debug: print "Loading",dbname
    dbdata = get(dbname)
    if debug: print "Found",len(dbdata),"unique artists from",dbname

    dbname  = setFile(basedir, "artistDB.json")
    if debug: print "Loading",dbname
    db      = get(dbname)
    if debug: print "Found",len(db),"known artists from",dbname
    
    errDB = getBadIDs(getDiscogDir())

    downloads = {}
    downloads = getMissing(dbdata, db, errDB)    
    if debug: print "Downloading",len(downloads),"new artists for missing artists."


    if len(downloads) == 0:
        print "Looping over",len(dbdata),"artist counts data..."
        for k,v in dbdata.iteritems():
            if v["CNT"] < minCounts:
                continue
            discID = getArtistDiscID(v["URL"])
            if db.get(discID):
                continue
            if errDB.get(discID):
                continue
            downloads[k] = v
            
        if debug:
            print "Downloading",len(downloads),"new artists with >=",minCounts,"counts."


    
    baseurl = u"https://www.discogs.com"
    useSafari = True
    dtime = 4
    problems = {}
    
    curDir  = setDir(base, artistDir)
    curDirs = [x for x in findAll(curDir) if isDir(x)]
    subDir  = setDir(base, artistDir)
    savedir = mkSubDir(subDir, str(len(curDirs)))
    print "\n\n===========> Saving files to",savedir," <===========\n\n"
    
    for i,artist in enumerate(downloads.keys()):
        v = downloads[artist]
        if i % 10 == 0:
            print '\n',i,'/',len(downloads),'\t',artist,'\t',v,'\n'
        suburl = v["URL"]
        artistSaveName = getSaveName(artist)
        savename = join(savedir, artistSaveName+"-1.p")
        if isFile(savename):
            continue
        retval = getData(baseurl, suburl, extra=None, savename=savename, 
                         useSafari=useSafari, dtime=dtime, debug=debug)
        if not retval:
            problems[artist] = suburl


    print "Found",len(problems),"download problems."
    if len(problems) > 0:
        savename = setFile(getDiscogDir(), "problems.json")
        print "Saving them to",savename
        save(savename, problems)
    



################################################################################
#
# Process the ArtistDB Files
#
################################################################################
def processArtistDBFiles(debug = False):
    basedir = getBaseDBDir()
    
    artistCntr   = Counter()    
    artistCntrDB = {}

    if debug:
        print "Looking for files in",basedir
    files = findPatternExt(basedir, pattern="artistDB-", ext=".p")
    #files = glob(join(basedir, "artistDB-*.p"))
    if debug:
        print "Found",len(files),"files in",basedir
                         
    nerr = 0
    print "  ",nice("   Progress", 20),nice("#Artists", 10),nice("#Errors", 10),"Filename"
    for i,ifile in enumerate(files):
        if i % 1000 == 0 or i == 10 or i == 100:
            print "  ",nicerate(i,len(files), 20),
            print nice(len(artistCntr), 10),
            print nice(nerr, 10),
            print ifile
        data = get(ifile)
        
        for artist,suburl in data.iteritems():
            discID = getArtistDiscID(suburl)
            if discID == None:
                if debug:
                    nerr += 1
                    #print "    No discID for",artist,suburl
                continue
            artistCntr[artist] += 1
            if artistCntrDB.get(artist) == None:
                artistCntrDB[artist] = suburl

    if debug:
        print "Found ",len(artistCntrDB),"unique artists from files in",basedir

    savename = setFile(basedir, "artistCountsAll.p")
    print "Saving",len(artistCntrDB),"artists to",savename
    save(savename, artistCntrDB)
    print savename,'size ->',getSize(savename, unit='MB'),"MB."

    savename = setFile(basedir, "artistCountsRaw.p")
    print "Saving",len(artistCntr),"artists to",savename
    save(savename, artistCntr)
    print savename,'size ->',getSize(savename, unit='MB'),"MB."


    
def findArtists(minCounts = 1, debug = True):
    basedir = getDiscogBaseDBDir()

    savename = setFile(basedir, "artistCountsAll.p")
    if debug: print "Loading",savename
    artistCntrDB = get(savename)
    if debug: print "Found",len(artistCntrDB),"artists in",savename
    
    savename = setFile(basedir, "artistCountsRaw.p")
    if debug: print "Loading",savename
    artistCntr = get(savename)
    if debug: print "Found",len(artistCntr),"artists in",savename
    

    artistCounter = {}                 
    for artist in artistCntrDB.keys():
        val = artistCntr[artist]
        if val < minCounts:
            continue
        url = artistCntrDB[artist]
        artistCounter[artist] = {"URL": url, "CNT": val}
        
        
    savename = setFile(basedir, "artistCounts.p")
    print "Saving",len(artistCounter),"/",len(artistCntrDB),
    print "unique artists with >=",minCounts,"counts to",savename
    save(savename, artistCounter)
    print savename,'size ->',getSize(savename, unit='kB'),"kB."
    
                                    



################################################################################
#
# Artist Helpers
#
################################################################################
def saveArtistData(artistData, debug = False, ifile = None, forceWrite = False):
    artistDBDir = getArtistsDBDir()

    artist   = artistData["Artist"]
    discID   = artistData["ID"]
    if artist == None or discID == None:
        removeFile(ifile)
        print " --> Removing due to artist/discID error:",ifile
        return

    modValue = getDiscIDHashMod(discID, modval=500)
    subDir   = mkSubDir(artistDBDir, str(modValue))
    outdir   = subDir
    savename  = setFile(outdir, discID+".p")
    if isFile(savename) and not forceWrite:
        return
    save(savename, artistData)
    print " --> Saved",savename




################################################################################
#
# Special Artists
#
################################################################################
def parseSpecialArtists(base = "/Volumes/Music/Discog", debug = False):  
    basedbdir   = getDiscogBaseDBDir()        
    dbname  = setFile(basedbdir, "artistDB.json")
    dbdata  = get(dbname)
    
    specialdir  = getDiscogSpecialDir()
    files = findExt(specialdir, ext=".html")
    for i,ifile in enumerate(files):
        if i % 250 == 0 or i == 50 or i == 10:
            print "\n====>",i,"/",len(files),'\t',ifile
        if getsize(ifile) < 1000:
            print " --> Removing due to low size:",ifile
            removeFile(ifile)
            continue
        
        bsdata         = getHTML(get(ifile))
        artistData     = parse(bsdata, debug)
        saveArtistData(artistData, dbdata, debug, ifile, forceWrite = False)

        artist         = artistData["Artist"]
        artistSaveName = getSaveName(artist)
        savename = setSubFile(base, "artists-special", artistSaveName+"-1.p")
        save(savename, open(ifile).read())

        if isFile(ifile):
            if debug:
                print " --> Removing special artist:",ifile
            removeFile(ifile)




################################################################################
#
# Special Artists
#
################################################################################
def downloadMultipageArtist(debug = False, forceWrite = False):
    
def parseMultipageArtists(debug = False, forceWrite = False):
    files = findPatternExt(getArtistsExtraDir(), pattern='-1', ext='.p')
    artists = [x.replace("-1.p", "") for x in files]
    discIDs = [getBasename(x) for x in artists if x.endswith('.p') == False]
    
    for i,discID in enumerate(discIDs):
        print i,'/',len(discIDs)
        files = findPatternExt(getArtistsExtraDir(), pattern=discID+"-", ext='.p')
        fullArtistData = None
        print "  Found",len(files),"for discID:",discID
        for j,ifile in enumerate(files):
            print "    -->",j,"/",len(files)
            bsdata         = getHTML(ifile)
            artistData     = artistdata.parse(bsdata, debug)
        
            if j == 0:
                fullArtistData = artistData
                continue
            else:
                #fullArtistData["Pages"] = max(int(fullArtistData["Pages"]), int(artistData["Pages"]))
                for media,mediaData in artistData["Media"].iteritems():
                    if fullArtistData["Media"].get(media) == None:
                        fullArtistData["Media"][media] = mediaData
                    else:
                        for item in mediaData:
                            fullArtistData["Media"][media].append(item)

        
        modValue = getDiscIDHashMod(discID, modval=500)
        dbname = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
        dbdata = get(dbname, debug)
        dbdata[discID] = fullArtistData
        save(dbname, dbdata, debug = True)
        
    


################################################################################
#
# Artist Data
#
################################################################################
def parseArtistFile(ifile, debug = False, forceWrite = False):
    retval = checkFileSize(ifile, 1000)
    if not retval: return None
    
    bsdata     = getHTML(get(ifile))
    artistData = artistdata.parse(bsdata) 
    return artistData
    
    
def parseArtists(dirnum, artistdir = "artists",
                 debug = False, forceWrite = False):
    base = getDiscogDir()
    basedbdir = getBaseDBDir()
    artistdir = setDir(base, artistdir)
    
    
    basedir = setDir(artistdir, str(dirnum))
    if not isDir(basedir):
        if debug: print basedir,"does not exist."
        return

    dbname  = setFile(basedbdir, "artistDB.json")
    dbdata  = get(dbname)

    files = findExt(basedir, ext=".p")
    print "Found",len(files),"in",basedir
    for i,ifile in enumerate(files):
        if i % 25 == 0 or i == 50 or i == 10:
            print "\n====>",i,"/",len(files),'\t',ifile
        artistData = parseArtistFile(ifile, debug, forceWrite)
        if artistData:
            saveArtistData(artistData, dbdata, debug, ifile, forceWrite)




################################################################################
#
# Show ArtistData
#
################################################################################
def showArtistData(artistData):
    print nice("Artist:",10),artistData.get("Artist")
    for key in artistData.keys():
        print key




################################################################################
#
# Update Artist DBs
#
################################################################################
def updateArtistDBs():
    artistDBDir = getArtistsDBDir()
    files = findExt(artistDBDir, ext=".p")
    for ifile in files:
        data = get(ifile)
        for discID,artistData in data.iteritems():
            media = artistData['Media']
            for mediatype in media.keys():
                tmp = {}
                for item in media[mediatype]:
                    code = item['Code']
                    del item['Code']
                    tmp[code] = item
                media[mediatype] = tmp
                     
        save(ifile, data)



################################################################################
#
# Error handlers
#
################################################################################
def getBadIDs(base, debug = True):
    errDBname = setSubFile(base, "artists-db-err", "errDB.json")
    errDB = get(errDBname)
    
    if debug: print "  Found ",len(errDB),"bad IDs."
    
    files = findSubExt(base, "artists-db-err", ext=".p")
    #for ifile in glob(join(base, "artists-db-err", "*.p")):
    for ifile in files:
        data = get(ifile)
        try:
            discID = data["ID"]
            errDB[discID] = 1
        except:
            continue
        
        removeFile(ifile)

    if debug: print "  Saving",len(errDB),"bad IDs."
    save(errDBname, errDB)
    return errDB
    

    
def removeKnownArtists(allDB, known, debug = False):
    print "Removing Known Artists:",len(allDB)
    print "         Known Artists:",len(known)
    for artist in known.keys():
        if allDB.get(artist):
            del allDB[artist]
    print "     New Known Artists:",len(allDB)
    raise ValueError("Done.")
    return allDB




def getMissing(dbdata, db, errDB, debug = False):
    missingDir  = mkSubDir(getMusicDir(), "missing")
    missingFile = setFile(missingDir, "missing.json")
    missing     = get(missingFile)
    
    downloads = {}
    #allDB = removeKnownArtists(dbdata, db)
    artists = dbdata.keys()
    #artists = allDB.keys()
    
    for i,artist in enumerate(reversed(missing.keys())):
        if len(artist) < 2: continue
        name = artist.replace("The ", "")        
        matches1 = findMatchingWord(name, artists)
        #matches2 = []
        matches2 = findNearest(name, artists, 100, 0.75)
        matches  = list(set(matches1 + matches2))
        #matches  = matches[:min(len(matches), 10)]
        if len(matches) > 0:
            print i,'/',len(missing),'\t',len(downloads),'\t',artist,' \t---> ',len(matches)
        for x in matches:
            v = dbdata[x]
            discID = getArtistDiscID(v["URL"])
            if db.get(discID):
                continue
            if errDB.get(discID):
                continue
            downloads[x] = v
        
        if len(downloads) > 100000:
            break
        
    return downloads



def splitArtistFilesByHashval(artistdir = "artists", N = 2000):
    base   = getDiscogDir()
    files  = glob(join(base, "artistFiles", "artists[0-9]", "*.p"))
    files += glob(join(base, "artistFiles", "artists[1-9][0-9]", "*.p"))
    print "Found",len(files)

    modN  = int(ceil(len(files) / N)) + 2
    fvals = {}    
    for ifile in files:
        hexval = int(sha1(ifile).hexdigest(), 16)
        modval = hexval % modN
        if fvals.get(modval) == None:
            fvals[modval] = []
        fvals[modval].append(ifile)
        
    for k,v in fvals.iteritems():
        outdir = mkSubDir(base, [artistdir, str(k)])
        print "Moving",len(v),"to",outdir
        for ifile in v:
            src = ifile
            dst = setFile(outdir, getBasename(src))
            moveFile(src, dst)
            
            
            


def addNewArtistsDBToDB():
    startVal       = start()
    artistDB       = getArtistDB()
    tmpdir = setDir(getDiscogDir(), "artists-db")
    files = findSubExt(getDiscogDir(), "artist-db", ext=".p")
    newToDB  = {}
    for i,ifile in enumerate(files):
        if (i+1) % 25 == 0: inter(startVal, i+1,len(files))
        artistData = get(ifile)
        #artistData = parseArtistFile(ifile)
        #print artistData
        discID = artistData.get("ID")
        if discID == None:
            removeFile(ifile, debug = True)
            continue
        if newToDB.get(discID):
            removeFile(ifile, debug = True)
            continue
        if artistDB.get(discID) == None:
            ref    = artistData.get("URL")
            name   = makeStrFromUnicode(makeUnicode(artistData.get("Artist")))
            newToDB[discID] = {"URL": ref, "Name": name}

        outfile = setFile(tmpdir, discID+".p")
        if isFile(outfile):
            removeFile(ifile, debug = True)
            continue
        moveFile(ifile, outfile, debug = True)
        
            
    saveNewDBs(newToDB)
    end(startVal)



def addNewArtistsToDB():
        
    startVal       = start()
    artistDB       = getArtistDB()
    knownArtistIDs = getKnownArtistIDs()
    
    tmpdir = setDir(getDiscogDir(), "artists-tmp")
    files = findSubExt(getDiscogDir(), "artists-special", ext=".p")
    newToDB  = {}
    for i,ifile in enumerate(files):
        if (i+1) % 25 == 0: inter(startVal, i+1,len(files))
        artistData = parseArtistFile(ifile)
        #print artistData
        discID = artistData.get("ID")
        if discID == None:
            removeFile(ifile, debug = True)
            continue
            
        if knownArtistIDs.get(discID) or newToDB.get(discID):
            removeFile(ifile, debug = True)
            continue
        
        outfile = setFile(tmpdir, discID+".p")
        moveFile(ifile, outfile, debug = True)

        if artistDB.get(discID) == None or True:
            ref    = artistData.get("URL")
            name   = makeStrFromUnicode(makeUnicode(artistData.get("Artist")))
            newToDB[discID] = {"URL": ref, "Name": name}
        #print ifile,'\t\t',discID,'\t',ref,'\t\t',name

    saveNewDBs(newToDB)
    end(startVal)



###############################################################################
#
# Re-arrange Artists by ModVal
#
###############################################################################
def moveArtistsByHash():
    artistsDir = getArtistsDBDir()
    #artistNameDB = getArtistNameDB(slim = False, debug = True)
    #files = findSubExt(setDir(getDiscogDir(), "artistNew"), "*", ext=".p")
    files = findSubExt(getDiscogDir(), "artists-db", ext=".p")
    #cnts = [0, 0]
    for ifile in files:
        discID = getBaseFilename(ifile)
        modValue = getDiscIDHashMod(discID, modval=500)
        subDir   = mkSubDir(artistsDir, str(modValue))
        outdir   = subDir
        outname  = setFile(outdir, discID+".p")
        if isFile(outname):
            removeFile(ifile, debug = True)
            continue
        moveFile(ifile, outname, debug = True)
        