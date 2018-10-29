# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 20:41:53 2017

@author: tgadfort
"""

from os.path import join, exists, getsize
from Discog import fileops
from re import match, sub, search
import json
import pickle
from collections import Counter, OrderedDict
from random import randrange


def getLineData(testString, line):
    if match(testString, line):
        value = sub(testString, '', line)
        return value
    return None


def moveFile(data):
    for i,line in enumerate(data):
        if len(line) > 0:
            if line[0] == "#":
                continue
        return data[i:]



def foundKey(key, prefix, line):
    if match(prefix+key+"=", line):
        return True
    return False



def getTitle(line):
    val = search("TTITLE(\d+)=", line)
    if val:
        return sub(val.group(), "", line)
    return None


def foundTitle(line):
    val = match("TTITLE(\d+)=", line)
    if val != None: return True
    return False



def addValue(retval, key, prefix, line):
    value = sub(prefix+key+"=", "", line)
    if retval.get(key) == None:
        retval[key] = value
    else:
        retval[key] = " ; ".join([retval[key], value])
    return retval


def addTitle(retval, title):
    if retval.get("TRACKS") == None:
        retval["TRACKS"] = OrderedDict()
    retval["TRACKS"][len(retval["TRACKS"])+1] = title
    return retval
    
    
    
def setArtistAlbum(retval):
    title  = retval["TITLE"]
    cnt    = title.count(" / ")
    if cnt != 1:
        #print "How do we parse this title:",title
        artist = "UNKNOWNARTIST"
        album  = title
    else:
        pos    = title.find(" / ")
        artist = title[:pos]
        album  = title[pos+3:]
    retval["ARTIST"] = artist
    retval["ALBUM"]  = album
    del retval["TITLE"]
    return retval
    
    

def parseCDDB(ifile):
    data = open(ifile).readlines()
    data = [x.replace("\n", "") for x in data]
    data = moveFile(data)

    retval={}
    while len(data) > 0:
        key = "DISCID"
        while foundKey(key, "", data[0]):
            retval = addValue(retval, key, "", data[0])
            data = data[1:]

        key = "TITLE"
        while foundKey(key, "D", data[0]):
            retval = addValue(retval, key, "D", data[0])
            data = data[1:]

        key = "YEAR"
        while foundKey(key, "D", data[0]):
            retval = addValue(retval, key, "D", data[0])
            data = data[1:]

        key = "GENRE"
        while foundKey(key, "D", data[0]):
            retval = addValue(retval, key, "D", data[0])
            data = data[1:]

        while foundTitle(data[0]):
            retval = addTitle(retval, getTitle(data[0]))
            data = data[1:]

        break

    retval = setArtistAlbum(retval)
    return retval



def parseFiles(dbdir = "/Volumes/Music/CDDB", fdir = None):
    if fdir == None:
        print "No fdir"
        return

    filename = join(dbdir, "raw", fdir+".json")
    if exists(filename):
        files = json.load(open(filename))
    else:
        files = fileops.getFiles(fdir)

    data = {}
    cntr = 1
    for i,ifile in enumerate(files):
        if ifile.find("Artists.p") != -1:
            continue
        if ifile.find("DB.p") != -1:
            continue
        fdata  = parseCDDB(ifile)
        artist = fdata["ARTIST"]
        if data.get(artist) == None:
            data[artist] = {}
        del fdata["ARTIST"]
        album  = fdata["ALBUM"]
        if data[artist].get(album) == None:
            data[artist][album] = {}
        del fdata["ALBUM"]
        discID  = fdata["DISCID"]
        del fdata["DISCID"]
        data[artist][album][discID] = fdata

        if i % 1000 == 0:
            print i,'/',len(files),'\t',ifile,'\t',artist

        if i % 25000 == 0 and i > 0:
            savename = join(dbdir, "proc", fdir+"-"+str(cntr)+".p")
            print "Saving",len(data),"artists to",savename
            pickle.dump(data, open(savename, "w"))
            size = round(getsize(savename)/1e6, 2)
            print savename,'size ->',size,"MB"
            data = {}
            cntr += 1

    savename = join(dbdir, "proc", fdir+"-"+str(cntr)+".p")
    print "Saving",len(data),"artists to",savename
    pickle.dump(data, open(savename, "w"))
    size = round(getsize(savename)/1e6, 2)
    print savename,'size ->',size,"MB"
    data = {}
    cntr += 1


def findArtistsInFiles(dbdir = "/Volumes/Music/CDDB", fdir = None):
    if fdir == None:
        print "No fdir"
        return

    files    = fileops.getFiles(join(dbdir, "proc"), pattern = fdir, filetype="p")
    artistDB = {}
    for i,ifile in enumerate(sorted(files)):
        if ifile.find("Artists.p") != -1:
            continue
        if ifile.find("DB.p") != -1:
            continue
        print i,'\t',ifile,'\t',len(artistDB)
        data    = pickle.load(open(ifile))
        for artist in data.keys():
            if artistDB.get(artist) == None:
                artistDB[artist] = []
            artistDB[artist].append(ifile)


    savename = join(dbdir, "proc", fdir+"-Artists.p")
    print "Saving",len(artistDB),"artists locations to",savename
    pickle.dump(artistDB, open(savename, "w"))





def makeArtistsFiles(dbdir = "/Volumes/Music/CDDB"):
    savename = join(dbdir, "proc", "DB.p")
    db = pickle.load(open(savename))
    print "Found",len(db),"artists in",savename
    
    aLen  = Counter()
    aCntr = {}
    for artist,adata in db.iteritems():
        aLen[len(adata)] += 1
        if aCntr.get(len(adata)) == None:
            aCntr[len(adata)] = {}
        for afile in adata:
            if aCntr[len(adata)].get(afile) == None:
                aCntr[len(adata)][afile] = {}
            aCntr[len(adata)][afile][artist] = 1

    for item in aLen.most_common(10000):
        print item
    print ''
    
    savename = join(dbdir, "proc", "DBcntr.p")
    print "Saving",len(aCntr),"artists to",savename
    pickle.dump(aCntr, open(savename, "w"))



def mergeArtistsFiles(dbdir = "/Volumes/Music/CDDB"):
    files = fileops.getFiles(join(dbdir, "proc"), pattern = "Artists", filetype="p")
    print files

    db = {}
    for ifile in files:
        data = pickle.load(open(ifile))
        print "Found",len(data),"from",ifile
        for artist,afiles in data.iteritems():
            if db.get(artist) == None:
                db[artist] = afiles
            else:
                db[artist] = list(set(afiles+db[artist]))

    savename = join(dbdir, "proc", "DB.p")
    print "Saving",len(db),"to",savename
    pickle.dump(db, open(savename, "w"))

    
    

dbdir = "/Volumes/Music/CDDB"
fdirs = ["country", "jazz", "reggae", "blues", "misc", 
         "rock", "classical", "folk", "newage", "soundtrack"]
extras =["data"]
#for fdir in fileops.getDirs(dbdir):



#parseFiles(dbdir, fdir)
    