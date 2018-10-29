# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 18:36:42 2016

@author: tgadfort
"""

import xml.etree.ElementTree as ET
import json
import sys
from collections import OrderedDict, Counter
from os.path import dirname, basename, join, exists, isfile, splitext, isdir
from os import listdir, walk
from glob import glob
import yaml
from difflib import get_close_matches
from urllib2 import url2pathname
import urllib
import re, urlparse


def saveYaml(yfile, ydata):
    print "Saving",yfile
    yaml.dump(ydata, open(yfile, "w"), encoding=None, default_flow_style=False, allow_unicode = True)

def getYaml(yfile):
    ydata = yaml.load(open(yfile))
    return ydata


def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


class cfile(file):
    #subclass file to have a more convienient use of writeline
    def __init__(self, name, mode = 'w'):
        self = file.__init__(self, name, mode)

    def wl(self, string):
        self.writelines(string + '\n')
        return None


def findNearest(item, ilist, num, cutoff):
    nearest = get_close_matches(item, ilist, n=num, cutoff=cutoff)
    return nearest


def getXMLdata(xml):
    debug = True
    if debug: print "Creating element tree from",xml
    sys.stdout.flush()

    tree = ET.parse(xml)
    dicts = tree.findall('dict/dict/dict')
    xmldata = []
    for i,val in enumerate(dicts):
        #print val.keys()
        #print val.items()
        trackdata = {}
        key  = None
        nval = 0
        for v in val.itertext():
            nval += 1
            v = v.strip()
            v = v.strip("\n")
            v = v.strip("\t")
            v = v.strip("\r")
            if len(v) == 0:
                key = None
                continue
                #print len(v),'\t['+v+']'
            if key == None:
                trackdata[v] = None
                key = v.strip()
            else:
                trackdata[key] = v.strip()
                #print "=====> ",nval,'\t',key,'\t',trackdata[key]
                key = None
        #print i,'\t',val.tag,'\t',val.findall('string')
        xmldata.append(trackdata)
        if len(xmldata) % 1000 == 0 and debug:
            print "  --> Parsed",len(xmldata),"items."
            sys.stdout.flush()
        continue
        for v in val.findall('string'):
            print v.tag,'\t',v.text,'\t',v.attrib,'\t',v.items(),'\t',v.keys()
        if i > 0:
            break

    if debug: print "Found",len(xmldata),"items."
    sys.stdout.flush()
    return xmldata



def organizeData():
    jfile = "/Users/tgadfort/Music/AlliTunes.json"
    data = json.load(open(jfile))
    artistData = {}
    for val in data:
        try:
            artist = val["Artist"]
        except:
            artist = "Unknown"
 
        if artistData.get(artist) == None:
            artistData[artist] = {}
        
        try:
            album = val['Album']
        except:
            album = "Unknown"
 
        if artistData[artist].get(album) == None:
            artistData[artist][album]          = {}
            artistData[artist][album]['dir']   = None
            artistData[artist][album]['files'] = []

        try:
            location = val['Location']
        except:
            print "No Location!"
            if True:
                print "No artist!"
                for k,v in val.iteritems():
                    print k,'\t',v
                raise()
        
        location = location.replace("file://", "")
        location = location.replace("%20", " ")
        adir  = dirname(location)
        fname = basename(location)
        if artistData[artist][album]['dir'] == None:
            artistData[artist][album]['dir'] = adir
        if isinstance(artistData[artist][album]['dir'], str):
            if artistData[artist][album]['dir'] != adir:
                artistData[artist][album]['dir'] = [artistData[artist][album]['dir'], adir]
        if isinstance(artistData[artist][album]['dir'], list):
            if adir not in artistData[artist][album]['dir']:
                artistData[artist][album]['dir'].append(adir)
        
        artistData[artist][album]['files'].append(fname)
        
    
    sfile = "/Users/tgadfort/Music/MyMusicFromiTunes.json"
    print "Saving",len(artistData),"to",sfile
    json.dump(artistData, open(sfile, "w"))
 

def showAlbums():
    sfile = "/Users/tgadfort/Music/MyMusicFromiTunes.json"
    artistData = json.load(open(sfile))
    for artist in sorted(artistData.keys()):
        print artist
        for album in sorted(artistData[artist].keys()):
            print "\t\t",len(artistData[artist][album]),'\t',album
        print ''






def createJSON(base, outdir):
    fname = sys._getframe().f_code.co_name
    xmls = glob(join(base, "*/iTunes Library.xml"))
    xmldoc = []
    for xml in xmls:
        musicdir = basename(dirname(xml))        
        outfile  = join(outdir, musicdir+".json")
        if exists(outfile):
            print fname,":",outfile,"already exists."
            continue

        jfile = outfile
        print "Creating JSON from",xml
        sys.stdout.flush()
        xmldoc = getXMLdata(xml)
        print "Saving JSON'd",xml,"to",jfile
        sys.stdout.flush()
        json.dump(xmldoc, open(jfile, "w"))
        print "Done."
        print ""
        sys.stdout.flush()
    


def trimDB(basedir, outdir, debug=False):
    fname = sys._getframe().f_code.co_name
    files = glob(join(basedir, "*.json"))


    trkdata = {}
    missing = []
    allFiles = {}
    nMiss = 0
    for ifile in files:
        print ""
        print "Loading",ifile
        data = json.load(open(ifile))
        print "Found",len(data),"entries."
        for i,entry in enumerate(data):
            album    = entry.get('Album')
            if album == None: album = "Unknown Album"
            artist   = entry.get('Artist')
            if artist == None: artist = "Unknown Artist"
            tracknum = entry.get('Track Number')
            if tracknum == None: tracknum = -1
            name       = entry['Name']
            location   = entry['Location']
            if location.find("http://") != -1:
                continue

            tmp        = location.replace("file://", "")
            filepath1  = urllib.url2pathname(urllib.unquote(str(tmp)))
            if not exists(filepath1):
                try:
                    filepath2  = filepath1.decode('utf-8')
                except:
                    filepath2  = None

                missing.append(location)
                continue

            
            fileinfo   = {"path": location, "name": name}
            allFiles[location] = 1
            #print entry
            #raise()

            if trkdata.get(artist) == None:
                trkdata[artist] = {}
                if debug: print artist
            if trkdata[artist].get(album) == None:
                trkdata[artist][album] = {}
                #if debug: print artist,'\t',album
                trkdata[artist][album]['tracks'] = {}
                trkdata[artist][album]['err'] = False
            if trkdata[artist][album]['tracks'].get(tracknum) == None:
                trkdata[artist][album]['tracks'][tracknum] = fileinfo
            else:
                trkdata[artist][album]['err'] = True
                if not isinstance(trkdata[artist][album]['tracks'][tracknum], list):
                    val = trkdata[artist][album]['tracks'][tracknum]
                    trkdata[artist][album]['tracks'][tracknum] = []
                    trkdata[artist][album]['tracks'][tracknum].append(val)
                trkdata[artist][album]['tracks'][tracknum].append(fileinfo)
            #if debug: print artist,'\t',album,'\t',tracknum,'\t',name

        print "Found",len(missing),"missing music files so far."
        print "Found",len(trkdata),"trimmed artists so far."
        print "Found",len(allFiles),"files so far."


    outfile  = join(outdir, "MissingMusic.json")
    print "Saving",len(missing),"missing music files to",outfile
    sys.stdout.flush()
    json.dump(missing, open(outfile, "w"))

    outfile  = join(outdir, "TrimmedMusic.json")
    print "Saving",len(trkdata),"trimmed artists to",outfile
    sys.stdout.flush()
    json.dump(trkdata, open(outfile, "w"))

    outfile  = join(outdir, "AllMusicFiles.json")
    print "Saving",len(allFiles),"trimmed artists to",outfile
    sys.stdout.flush()
    json.dump(allFiles, open(outfile, "w"))
    
    
def createArtistOutput(base, outdir):
    infile  = join(base, "TrimmedMusicLocations.json")
    locdata = json.load(open(infile))
    locs    = {}
    for k,v in locdata.iteritems(): locs[v] = k
    infile  = join(base, "TrimmedMusic.json")
    #outfile = join(outdir, "Output.yaml")
    trkdata = json.load(open(infile))
    #output  = OrderedDict()
    f = cfile(join(outdir, "fixes.dat"))
    for artist in sorted(trkdata.keys()):
        nearests = findNearest(artist, trkdata.keys(), 4, 0.95)
        nearests.remove(artist)
        if len(nearests) > 0:
            print artist
            f.wl('{0: <15}'.format(artist)+'\t'+", ".join(nearests))
            for album in trkdata[artist].keys():
                f.wl('\t\t'+album+' ('+locs[trkdata[artist][album]['data']]+')')
                f.wl('')
    f.close()
    

def processTrimDB(base, outdir):
    infile  = join(base, "TrimmedMusic.json")
    print "Loading",infile
    trkdata = json.load(open(infile))
    print "Found",len(trkdata),"artists."
    sys.stdout.flush()
    


def findAllMusic(basedir, outdir):
    musicdir = "/Volumes/Music"
    files = glob(join(basedir, "*.json"))
    walkFiles = {}
    for ifile in files:
        jname = splitext(basename(ifile))[0]
        ipath = join(musicdir, jname)
        if not isdir(ipath):
            print ipath
        fullpath = join(ipath, "iTunes Media", "Music")
        if not isdir(fullpath):
            print fullpath
            continue    
    
        for directory, dirnames, filenames in walk(fullpath):
            for filename in filenames:
                ext = splitext(filename)[1]
                if ext not in ['.mp3', '.m4a', '.MP3', '.mp2', '.Mp3']:
                    continue
                fname = join(directory, filename)
                walkFiles[fname] = 1
            
        print "Found",len(walkFiles),"walk files so far."
                
    outfile  = join(outdir, "AllWalkMusicFiles.json")
    print "Saving",len(walkFiles),"trimmed artists to",outfile
    sys.stdout.flush()
    json.dump(walkFiles, open(outfile, "w"))


def findMissingMusic(basedir):        
    outfile   = join(basedir, "AllWalkMusicFiles.json")
    walkFiles = json.load(open(outfile))
    print "Found",len(walkFiles),"walk files from",outfile
    sys.stdout.flush()

    outfile   = join(basedir, "AllMusicFiles.json")
    allFiles  = json.load(open(outfile))
    print "Found",len(allFiles),"itunes files from",outfile
    sys.stdout.flush()

    matches = 0
    unmatched = []    
    for i,ifile in enumerate(allFiles.keys()):
        if i % 25000 == 0:
            print i,'\t',len(allFiles),'\t',matches,'\t',len(unmatched)
        path = urllib.url2pathname(urllib.unquote(str(ifile)))
        path = path[7:]
        if walkFiles.get(path):
            del walkFiles[path]
            matches += 1
        else:
            unmatched.append(ifile)
        
    print "Found",matches,"matches between iTunes and Walk."
    print "Found",len(unmatched),"unmatched iTunes files."
    print "Found",len(walkFiles),"remaining Walk files."

    outfile  = join(outdir, "UmatchediTunes.json")
    print "Saving",len(unmatched),"trimmed artists to",outfile
    sys.stdout.flush()
    json.dump(unmatched, open(outfile, "w"))

    outfile  = join(outdir, "missingWalkFiles.json")
    print "Saving",len(walkFiles),"trimmed artists to",outfile
    sys.stdout.flush()
    json.dump(walkFiles, open(outfile, "w"))


basedir  = "/Users/tgadfort/Music/AllMyMusic"
#findMissingMusic(basedir)

basedir = "/Users/tgadfort/Music/MyMusic"
outdir  = "/Users/tgadfort/Music/AllMyMusic"
#findAllMusic(basedir, outdir)

basedir = "/Volumes/Music"
outdir  = "/Users/tgadfort/Music/MyMusic"
createJSON(basedir, outdir)

basedir = outdir
outdir  = "/Users/tgadfort/Music/AllMyMusic"
#trimDB(basedir, outdir)

basedir = outdir
outdir  = "/Users/tgadfort/Music/AllMyMusic"
#createArtistOutput(outdir, outdir)
#processTrimDB(basedir, outdir)