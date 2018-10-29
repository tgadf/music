#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 18:30:09 2017

@author: tgadfort
"""

import sys
from math import ceil
from collections import Counter
from time import sleep
from urllib import pathname2url

if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from strops import makeUnicode, nicerate, makeStrFromUnicode, getSaveName
from fileio import get, save
from fsio import isFile, setFile, removeFile, setDir, setSubFile, moveFile
from fileinfo import getBasename, getBaseFilename
from artistdata import getArtistDiscID, parse
from htmlParser import getHTML
from search import findExt, findPattern
from timing import start,inter,end

from DiscogDownload import getData
from DiscogBase import saveArtistCounts, saveArtistRefs, saveArtistDB, saveArtistNames, saveArtistNameIDs, getArtistDB, saveNewDBs, getDiscIDHashMod, mergeArtistDBs
from DiscogPath import getCollectionsDir, getBaseDBDir, getCollectionsDBDir, getSearchDir, getDiscogDir, getSearchArtistsDBDir, getSearchArtistsDir, getArtistsDBDir, getArtistsDir


###############################################################################
#
# Parse Global Collections and Download Collections Files  (1)
#
###############################################################################
def createCollections():
    filename = setFile(getCollectionsDir(), "collections.txt")
    data     = get(filename)
    
    #https://www.discogs.com/search/?sort=have%2Cdesc&style_exact=Experimental&layout=sm&page=1&decade=2010    
    
    #https://www.discogs.com/search/?sort=have%2Cdesc&layout=sm&country_exact=UK&style_exact=Experimental&genre_exact=Electronic&page=1&decade=2010

                  
    results = {}
    i = 0
    collection = None
    while i < len(data):
        line = unicode(data[i], 'utf-8')
        if len(line) == 0:
            collection = None
        elif line[0] == "#":
            collection = line[2:]
            print collection
            results[collection] = Counter()
        else:
            val = line
            cnt = val.split()[0]
            value = " ".join(val.split()[1:])
            try:
                cnt = int(cnt.replace(",", ""))
            except:
                raise ValueError("Could not parse",cnt)

            print collection,'\t',cnt,'\t',value
            results[collection][value] = cnt
                   
        i += 1
        #print i,len(data)
        if i > 1000:
            break
        
    savename = setFile(getCollectionsDir(), "collections.yaml")
    print "Saving collections data to",savename
    save(savename, results)
    
    
def getCollections(maxToGet = 100000, dtime = 10, useSafari = True, 
                   force = False, debug = False):
    filename = setFile(getCollectionsDir(), "collections.yaml")
    data     = get(filename)

    collectionDict = {}
    collectionDict["Style"]    = "style_exact"
    collectionDict["Genre"]    = "genre_exact"
    collectionDict["Country"]  = "country_exact"
    collectionDict["Base"]     = "limit=250&sort=have%2Cdesc&layout=sm"
    #https://www.discogs.com/search/?sort=have%2Cdesc&layout=sm&page=1&country_exact=US

    baseURL  = u"https://www.discogs.com/search/"
    problems = {}

    for collection,collectionData in data.iteritems():
        cData = Counter(collectionData)
        for item in cData.most_common():
            num = item[1]
            val = item[0]
            pages = int(ceil((num+1)/500.0))
            
            maxVal = min(maxToGet, pages)
            for i in range(maxVal):
                pageNum  = makeUnicode(i+1)
                
                subURL  = "?"+collectionDict["Base"]
                subURL += "&"+collectionDict[collection]+"="+val
                subURL += "&"+"page="+pageNum

                if debug:
                    print "Getting  ",collection,'-',val,i,nicerate(i,maxVal)
            
                URL = baseURL + subURL
                savename = setFile(getCollectionsDir(),val+"-"+pageNum+".p")
                if not isFile(savename) or force:
                    if debug:
                        print "  Downloading",URL
                    retval = getData(base=URL, suburl=None, extra=None, savename=savename, 
                                     useSafari=useSafari, dtime=dtime, debug=debug)
                    if not retval:
                        print "  There was an error. Logging it."
                        if problems.get(collection) == None:
                            problems[collection] = []
                        problems[collection].append(subURL)
                    #https://www.discogs.com/search/%3Flimit%3D250%26sort%3Dhave%252Cdesc%26layout%3Dsm%26genre_exact%3DElectronic%26page%3D1
                if debug:
                    print "Retreived",collection,'-',val,i,nicerate(i,maxVal),"\n"
                                                                   


###############################################################################
#
# Parse Downloaded Collection Files To Create Master Artist List  (2)
#
###############################################################################
def parseCollectionFile(bsdata):

    artistDB = Counter()
    refDB    = {}
        
    for h4 in bsdata.findAll("h4"):
        spans = h4.findAll("span")
        ref = None
        if len(spans) == 0:
            ref = h4.find("a")
        else:
            ref = spans[0].find("a")
            
        if ref:
            attrs  = ref.attrs
            artist = makeUnicode(ref.text)
            href   = attrs.get('href')
            if href:
                if href.find("anv=") == -1:
                    continue
                
                artistDB[href] += 1
                refDB[href] = artist
                     
    return artistDB,refDB


def parseCollections():
    basedir  = getBaseDBDir()
    coldir   = getCollectionsDir()
    files = findExt(coldir, ext=".p")
    artistDB = Counter()
    refDB    = {}

    keys = {}
    for ifile in findPattern(basedir, pattern="collectionFrequency"):
        for k in get(ifile).keys():
            keys[k] = 1
    collectionDB = {}
    
    print "Looping over",len(files),"files.\n"
    startVal = start()
    nF = 1
    for i,ifile in enumerate(files):
        name   = getBasename(ifile)
        if keys.get(name):
            continue

        artistDB = Counter()
        refDB    = {}

        fdata  = get(ifile)
        bsdata = getHTML(fdata)
        artistDB, refDB = parseCollectionFile(bsdata)
        collectionDB[name] = {"db": artistDB, "ref": refDB}

        #if (i+1) % 10 == 0: print "  --> Found",len(artistDB),"after",i+1,"files."
        if (i+1) % 25 == 0: inter(startVal,i+1,len(files))

        if (i+1) % 250 == 0:
            savename = setFile(basedir, "collectionFrequency"+str(nF)+".yaml")
            save(savename, collectionDB)
            nF += 1
            collectionDB = {}

    end(startVal)

    savename = setFile(basedir, "collectionFrequency"+str(nF)+".yaml")
    save(savename, collectionDB)
    return



def mergeCollections():
    basedir  = getBaseDBDir()

    files = findPattern(basedir, pattern="collectionFrequency")
    files = [x for x in files if x.find("Merge") == -1]
    for i,ifile in enumerate(files):
        print "Loading",nicerate(i,len(files)),ifile
        data = get(ifile)
        print "  Found",len(data),"collections in this file."
        freq  = None
        refs  = None
        for j,collection in enumerate(data.keys()):
            db   = Counter(data[collection]["db"])
            ref  = data[collection]["ref"]
            print "    ",j,'\t',collection,'\t\t',len(db)
            
            if freq == None:
                freq = db
                refs = ref
            else:
                freq = freq + Counter(db)
                refs = dict(refs.items() + ref.items())

        print "    Sizes:",len(freq),len(refs)

        savename = ifile.replace(".yaml", "Merge.yaml")
        collectionDB = {"db": freq, "ref": refs}
        save(savename, collectionDB)

    return



def createCollectionDBs():
    basedir = getCollectionsDBDir()

    artistCounts   = Counter()
    artistDB       = {}
    artistRefs     = {}
    artistNames    = {}
    artistNameIDs  = {}

    startVal = start()
    files = findPattern(basedir, pattern="collectionFrequency")
    files = [x for x in files if x.find("Merge") != -1]
    for i,ifile in enumerate(files):
        print "Loading",nicerate(i,len(files)),ifile
        data = get(ifile)
        
        db   = Counter(data["db"])
        ref  = data["ref"]

        discIDs = {getArtistDiscID(k): 1 for k in ref.keys()}
        print "  Found",len(discIDs),"unique keys in this file."
        refs    = {getArtistDiscID(k): makeStrFromUnicode(makeUnicode(k)) for k in ref.keys()}
        names   = {getArtistDiscID(k): makeStrFromUnicode(makeUnicode(v)) for k, v in ref.iteritems()}
        nameIDs = {v: k for k, v in ref.iteritems()}

        artistDB      = dict(artistDB.items() + discIDs.items())
        artistCounts  = artistCounts + db
        artistRefs    = dict(artistRefs.items() + refs.items())
        artistNames   = dict(artistNames.items() + names.items())
        artistNameIDs = dict(artistNameIDs.items() + nameIDs.items())

        inter(startVal, i+1, len(files))
        print "  Total Unique Keys:",len(artistDB)


    artistCounts = Counter({getArtistDiscID(k): v for k, v in artistCounts.iteritems()})

    if artistDB.get(None):
        del artistDB[None]
    if artistRefs.get(None):
        del artistRefs[None]
    if artistNames.get(None):
        del artistNames[None]
    if artistNameIDs.get(None):
        del artistNameIDs[None]

    end(startVal)
            
    saveArtistCounts(artistCounts, slim = False, debug = True)
    saveArtistDB(artistDB, slim = False, debug = True)
    saveArtistRefs(artistRefs, slim = False, debug = True)
    saveArtistNames(artistNames, slim = False, debug = True)
    saveArtistNameIDs(artistNameIDs, slim = False, debug = True)




###############################################################################
#
# Search Results
#
###############################################################################
def downloadSearchResults(searchTerm, forceWrite = False, debug = True):
    if debug:
        print "downloadSearchResults(",searchTerm,")"
    baseURL   = u"https://www.discogs.com/search/"
    #subURL    = "?limit=250&q="+pathname2url(makeUnicode(searchTerm).encode("utf-8"))+"&type=artist&layout=sm"
    subURL    = "?limit=250&q="+pathname2url(makeUnicode(searchTerm).encode("utf-8"))+"&layout=sm"
    #subURL    = "?q="+searchTerm+"&type=artist&layout=sm"
    URL       = baseURL + subURL
    savename  = setFile(getSearchDir(),getSaveName(searchTerm)+".p")
    if isFile(savename) and forceWrite == False:
        return
    
    if debug:
        print "Saving search results for",searchTerm,"to",savename
    dtime     = 5
    useSafari = True    
    attempts  = 1
    retval    = False
    
    while not retval and attempts <= 3:
        retval = getData(base=URL, suburl=None, extra=None, savename=savename, 
                         useSafari=useSafari, dtime=dtime, debug=debug)
        if not retval:
            print "  There was an error. Logging it."
            attempts += 1
            if isFile(savename):
                removeFile(savename, debug)

    if retval and debug:
        print "Downloaded search results for",searchTerm


        
def parseSearchResultsFile(bsdata):
    refDB    = {}
    for h4 in bsdata.findAll("h4"):
        ref = h4.find("a")
        if ref:
            attrs  = ref.attrs
            href   = attrs.get('href')
            if href:
                if href.find("anv=") != -1:
                    continue
            discID = getArtistDiscID(href)
            
            refDB[discID] = href
                     
    return refDB




def parseDownloadedSearchResults(forceWrite = False, debug = True):
    files = findExt("/Volumes/Music/Discog/search", ".html")
    for ifile in files:
        savename = ifile.replace(".html", ".p")
        data = open(ifile).read()
        save(savename, data)    
    
    #artistDB = getArtistDB()
    files    = findExt(getSearchDir(), ext=".p")

    toGet = {}
    print "Searching through",len(files),"search files."
    startVal = start()
    for i,ifile in enumerate(files):
        if (i+1) % 25 == 0: inter(startVal, i+1, len(files))
        bsdata = getHTML(ifile)
        refDB = parseSearchResultsFile(bsdata)
        for discID,href in refDB.iteritems():
            if toGet.get(discID): continue
            #if artistDB.get(discID) or toGet.get(discID): continue
            toGet[discID] = href

    end(startVal)

    savename = setFile(getSearchDir(), "toGet.yaml")    
    print "Downloading",len(toGet),"new disc IDs."
    save(savename, toGet, debug = True)
    


def downloadSearchResultArtists(debug = False, dtime = 4):
    artistDB = getArtistDB()
    outdir   = getSearchArtistsDir()
    outdbdir = getSearchArtistsDBDir()
    baseURL  = u"https://www.discogs.com"
    newToDB  = {}
    useSafari = True
    
    
    savename = setFile(getSearchDir(), "toGet.yaml")
    toGet = get(savename, debug = True)
    print "Downloading",len(toGet),"new disc IDs."

    startVal = start()

    for i,discID in enumerate(toGet.keys()):
        
        if (i+1) % 100 == 0: inter(startVal, i+1, len(toGet))
        
        print i,'/',len(toGet)
        if discID == None:
            continue
    
        href = toGet[discID]
        
        if artistDB.get(discID) or newToDB.get(discID): continue
        #if newToDB.get(discID): continue

        try:
            savename = setFile(outdir, discID+".p")
        except:
            continue
        
        if isFile(savename):
            continue
        
        URL = baseURL + href
        URL = baseURL + pathname2url(makeUnicode(href).encode("utf-8"))
        URL = URL + "?sort=year%2Casc&limit=500&page=1"

        retval   = False
        attempts = 0
        while not retval and attempts < 3:
            retval = getData(base=URL, suburl=None, extra=None, savename=savename, 
                             useSafari=useSafari, dtime=dtime+2*attempts, debug=debug)
            attempts += 1
            #sleep()
            
        if retval:
            bsdata = getHTML(savename)
            artistData     = parse(bsdata, debug)
            savename = setFile(outdbdir, discID+".p")
            if isFile(savename):
                continue
            save(savename, artistData, debug = True)

        newToDB[discID] = 1
               
    end(startVal)
               

def mergeSearchResults(debug = True):
    newToDB  = {}
    artistDBData = {}

    modVal   = 500
        
    files    = findExt(getSearchArtistsDBDir(), ext=".p")
    for i,ifile in enumerate(files):
        if i % 100 == 0:
            print i,'/',len(files),'\t',ifile
        artistData = get(ifile)
        discID   = artistData["ID"]
        href     = artistData["URL"]
        artist   = makeStrFromUnicode(artistData["Artist"])
        modValue = getDiscIDHashMod(discID, modval=modVal)
        if artistDBData.get(modValue) == None:
            artistDBData[modValue] = {}
        newToDB[discID] = {"URL": href, "Name": artist}
        artistDBData[modValue][discID] = artistData

    saveNewDBs(newToDB)    
    mergeArtistDBs(False)

    for modValue in artistDBData.keys():
        modDBfile = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
        modDB = get(modDBfile)
        for discID in artistDBData[modValue].keys():
            modDB[discID] = artistDBData[modValue][discID]
        try:
            save(modDBfile, modDB)
        except:
            continue

    moveSearchResults()        

def moveSearchResults(debug = True):    
    modVal   = 500

    files    = findExt(getSearchArtistsDir(), ext=".p")
    for ifile in files:
        discID   = getBaseFilename(ifile)
        modValue = getDiscIDHashMod(discID, modval=modVal)
        outfile  = setSubFile(getArtistsDir(), str(modValue), discID+".p")
        moveFile(ifile, outfile, forceMove = True, debug = True)

    files    = findExt(getSearchArtistsDBDir(), ext=".p")
    for ifile in files:
        removeFile(ifile, debug = True)

        