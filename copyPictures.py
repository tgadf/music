#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:56:07 2017

@author: tgadfort
"""

import sys
import re
from collections import OrderedDict
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fileio import get, setFile, getDirname, getBasename, setSubFile, mkSubDir, copyFile



def getTopLevelAlbumKeys(dbdata):
    albums = []
    for item in dbdata["RKCustomSortOrder"]:
        if item["containerUuid"] == "'TopLevelAlbums'":
            albums.append(item["objectUuid"])
    return albums



def getFavoritesInfo(dbdata):
    albumInfo = {}
    for item in dbdata["RKAlbum"]:
        if item['folderUuid'] == "'LibraryFolder'":
            if item["name"] == "'Favorites'":
                album = item["uuid"]
                name  = item["name"]
                albumInfo[album] = name               
    return albumInfo



def getAlbumInfo(dbdata):
    albumInfo = {}
    for item in dbdata["RKAlbum"]:
        print item['folderUuid'], "'TopLevelAlbums'"
        if item['folderUuid'] == "'TopLevelAlbums'":
            album = item["uuid"]
            name  = item["name"]
            if name.startswith('\'') and name.endswith('\''):
                name = name[1:-1]
            albumInfo[album] = name
    return albumInfo



def getPhotoInfo(dbdata):
    photoInfo = {}
    for item in dbdata["RKMaster"]:
        photo = item["uuid"]
        name  = item["imagePath"]
        photoInfo[photo] = name
    return photoInfo



def getAlbumPhotos(dbdata, albums, basePath = "/Users/tgadfort/Pictures/Photos Library.photoslibrary/Masters"):
    albumPhotos = {}
    for album,albumName in albums.iteritems():
        print "Getting Sort Order for",albumName
        albumPhotos[album] = []
        for item in dbdata["RKCustomSortOrder"]:
            objectID    = item["containerUuid"]
            containerID = item["objectUuid"]
            if objectID == album:
                albumPhotos[album].append(containerID)

    photoMap = {}
    albums["Favorites"] = "Favorites"
    photoMap["Favorites"] = []
    for album,photos in albumPhotos.iteritems():
        print "Getting Versions for",albums[album]
        photoMap[album] = []
        for photo in photos:
            for item in dbdata["RKVersion"]:
                if item['isFavorite'] == '1':
                    masterUuid = item["masterUuid"]
                    photoMap["Favorites"].append(masterUuid)
                if item["uuid"] == photo:
                    masterUuid = item["masterUuid"]
                    photoMap[album].append(masterUuid)

    albumData = {}
    for album,photos in photoMap.iteritems():
        print "Getting Masters for",albums[album]
        albumData[album] = {}
        for photo in photos:
            for item in dbdata["RKMaster"]:
                if item["uuid"] == photo:
                    image    = item['imagePath']
                    image    = image[1:-1]
                    subdir   = getDirname(image)
                    basename = getBasename(image)
                    ipath    = setSubFile(basePath, subdir, basename)
                    albumData[album][photo] = ipath
            
    return albumData,albums



def copyAlbumPhotos(albumData, albumNames, destdir = '/Volumes/Seagate/Pictures/FromiMac', debug = True, copy = True):
    if debug: print "Copying albums"
    for album, albumPhotos in albumData.iteritems():
        albumName = albumNames[album]
        dstdir    = mkSubDir(destdir, albumName, debug)
        for photo,photoPath in albumPhotos.iteritems():
            src = photoPath
            basename = getBasename(photoPath)
            dst = setFile(dstdir, basename)
            copyFile(src, dst, forceCopy = False, debug = debug)



def parseValues(values, schema, table, debug = False):
    if not (values.startswith('VALUES') and values.endswith(';')):
        raise ValueError("Could not parse Values:",values)

    values = values[len("VALUES")+1:-2]
    values = values.split(',')
    values = dict(zip(schema.keys(), values))
    if debug:
        print table
        print "\t",values
    return values
    


def getSchema(line):
    if not (line.startswith('CREATE TABLE') and line.endswith(';')):
        raise ValueError("Could not parse Values:",line)

    line = line[len("CREATE TABLE "):-1]
    vals = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+',line)
    try:
        table = vals[0]
        keys  = vals[1]
        keys  = keys[1:-1]
    except:
        raise ValueError("Could not find table and keys in",vals)
    
    values = OrderedDict()
    for x in keys.split(", "):
        v = x.split()
        values[v[0]] = " ".join(v[1:])
        
    return table,values
        


def getDBdata(basedir = "/Users/tgadfort/Pictures" , debug = False):
    if debug: print "Getting Photos DB Data."

    filename = setFile(basedir, "dbinfo.dat")
    dbdata   = get(filename, debug=True)


    keys   = {}
    line   = None
    i      = 0
    schema = {}
    data   = {}
    while i < len(dbdata):
        val = dbdata[i]
        while not val.endswith(';'):
            i += 1
            val += dbdata[i]
            
        i += 1         
        line = val
        
        if re.search(r'PRAGMA (.*)', line):
            continue
        if re.search(r'CREATE TABLE', line):
            table,keys = getSchema(line)
            schema[table] = keys
            continue
        if re.search(r'CREATE (INDEX|TRIGGER)', line):
            continue
        if re.search(r'BEGIN TRANSACTION', line):
            continue
        if re.search(r'COMMIT', line):
            continue
        if re.search(r'INSERT INTO sqlite_master', line):
            continue
        if re.search(r'DELETE FROM sqlite_sequence', line):
            continue
        
        
        mvals = re.search( r'(.*) (.*) VALUES', line, re.M|re.I)
        try:
            command = mvals.group(1)
            table   = mvals.group(2)
            table   = table[1:-1]
            line    = re.sub(command, "", line)
            line    = re.sub(table, "", line)
            line    = re.sub(r'\"\" ', "", line)
            line    = line.strip()
        except:
            raise ValueError("Could not parse",line)

        if table in ["RKCustomSortOrder", "RKAlbum", "RKMaster", "RKVersion", "RKVersion_stringNote"]:
            if data.get(table) == None:
                data[table] = []
            data[table].append(parseValues(line, schema[table], table, debug = False))

    return data



#dbdata = getDBdata()