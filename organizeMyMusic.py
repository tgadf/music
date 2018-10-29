# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 19:26:19 2017

@author: tgadfort
"""


from glob import glob
from os.path import join, exists, basename, splitext, isdir, walk
import sys
import json
from collections import Counter
from Discog import artistdata, albumdata, match, yamldata, mp3data






def cleanEverythingList(basedir, musicdir):
    outfiles  = glob(join(itunesbase, "Everything-*.json"))
    for outfile in outfiles:
        db = json.load(open(outfile))
        print "Found",len(db),"mp3s from",outfile
        mp3s = db.keys()
        for mp3 in mp3s:
            if not exists(mp3):
                del db[mp3]
        print "Keeping",len(db),"mp3s from",outfile
        json.dump(db, open(outfile, "w"))


def createEverythingList(basedir, musicdir):
    sys.stdout.flush()
    
    files = glob(join(basedir, "*.json"))
    for ifile in files:
        jname = splitext(basename(ifile))[0]
        ipath = join(musicdir, jname)
        if not isdir(ipath):
            print "Not a path",ipath
            continue
        fullpath = join(ipath, "iTunes Media", "Music")
        if not isdir(fullpath):
            print "Could not find iTunes Media/Music:",fullpath
            continue
        
        print "----->",fullpath
        db  = {}
        fdb = {}
        for directory, dirnames, filenames in walk(fullpath):
            for filename in filenames:
                fname = join(directory, filename)
                artist,album,trackno,compilation,other = mp3data.getInfo(fname)
                if compilation: artist = "Compilation"
                if artist == None: continue
                if db.get(artist) == None:
                    db[artist] = {}
                if album == None: continue
                if db[artist].get(album) == None:
                    db[artist][album] = []
                db[artist][album].append(fname)
                fdb[fname] = [artist,album]
                if len(fdb) % 2500 == 0:
                    print "Files:",len(fdb),"\t\tArtists:",len(db)

        outfile  = join(basedir, "Everything-"+jname+".json")
        print "Saving",len(fdb),"artist files to",outfile
        sys.stdout.flush()
        json.dump(fdb, open(outfile, "w"))
            
        outfile  = join(basedir, "Artists-"+jname+".json")
        print "Saving",len(db),"artist files to",outfile
        sys.stdout.flush()
        json.dump(db, open(outfile, "w"))
        
        
        
def checkCompilationAlbums(itunesbase, itunes, discog, corrfile):
    print "\ncheckCompilationAlbums()\n"

    unknowns = []

    outfiles  = glob(join(itunesbase, "Everything-*.json"))
    albums    = {}
    trkalbums = {}
    for outfile in outfiles:
        if outfile.find("Compilation") != -1: continue
        if outfile.find("Fix Artists") != -1: continue
        if outfile.find("Investigate") != -1: continue
        if outfile.find("Multiple Artists and DJs") != -1: continue
        db = json.load(open(outfile))
        for track,v in db.iteritems():
            album  = v[1]
            artist = v[0]
            #if album in copiedalbums: continue
            if artist not in unknowns: continue
            if not exists(track): continue
            #if album.find("") == -1: continue
            if albums.get(album) == None:
                albums[album] = Counter()
            albums[album][artist] += 1
            if trkalbums.get(album) == None:
                trkalbums[album] = {}
            trkalbums[album][track] = artist

    albumCntr = Counter()
    for album in albums.keys():
        albumCntr[album] = len(albums[album].keys())

    copies = []
    filesToCopy = {}
    for item in albumCntr.most_common():
        #if item[1] <= 5: continue
        print '\n\n',item[1],'\t',item[0],'\t'
        print "==>"
        for i,name in enumerate(sorted(trkalbums[item[0]].keys())):
            print "\t",basename(name),'\t',trkalbums[item[0]][name]
            #if i > 3: break
        copies.append(item[0])
        filesToCopy[item[0]] = trkalbums[item[0]].keys()
        
    print json.dumps(copies)
    json.dump(filesToCopy, open(join(itunesbase, "filesToCopy.json"), "w"))
    #setAndMoveCompilationAlbums(itunesbase, itunes, discog, corrfile)
