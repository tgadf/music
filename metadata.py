import argparse
from mutagen.id3 import ID3, TYER
from mutagen.easyid3 import EasyID3
import shutil
import os
from collections import Counter
import re
import json
import datetime

def getTags():
    tags = open("id3v2.dat").readlines()
    tags = [x.strip("\n") for x in tags]
    tdata = {}
    for tag in tags:
        section = tag[:6].strip()
        tag = tag[7:].strip()
        name = tag[:4]
        tag = tag[5:].strip()
        descr = tag[1:-1]
        descr = descr.replace("#"+name, "").strip()
        descr = descr.replace("#sec"+section, "").strip()
        tdata[name] = descr
    return tdata


def parseDateLocation(setlist):
    data = open(setlist).readlines()
    data = [x.strip("\n") for x in data]

    date = None
    location = None
    for j in range(len(data)):
        line = data[j]
        if line.find("selected=\"selected\"") != -1:
            if line.count(".") >= 2:
                date = line
                break
        if line.find("href=\"\"javascript:void(0)") != -1:
            location = line
            k = 1
            print location
            while location.find("</div>") == -1:
                location += "XXX"
                location += data[j+k]
                print len(location)
                k += 1
    
    pos = date.find(">")
    date = date[pos+1:]
    pos = date.find("<")
    date = date[:pos]
    date = date.replace(".", "-")
    return date


def parseSetlist(setlist):
    data = open(setlist).readlines()
    data = [x.strip("\n") for x in data]

    table=None
    slist=[]
    for line in data:
        if line.find("Song Title") != -1 and line.find("<table") != -1:
            table = line
            break
    if not table:
        print "No table in",setlist
        f()
    lines = table.split("<tr")
    for line in lines:
        if line.find("Song Title") != -1 and line.find("Venue") != -1:
            continue
        cols = line.split("<td")
#        print ""
#        print ""
#        print ""
#        print len(cols)
        if len(cols) >= 9:
#            for j in range(len(cols)):
            col = cols[2]
#            print "\t"+str(2)+"\t"+col
            pos = col.find("javascript:void(0)")
            if pos != -1:
                song = col[pos:]
            else:
                print "Can not parse:",col
                f()
            pos = song.find(">")
            song = song[pos+1:]
            pos = song.find("</a>")
            song = song[:pos]
            slist.append(song)
            print "  --->",len(slist),'\t',song
    return slist

def songLength(length):
    ms = int(length)
    seconds = ms / 1000
    minutes = int(float(seconds / 60.0))
    seconds = int(float(seconds % 60))
    return minutes,seconds


def parseTour(tourname):
    data = open(tourname).readlines()
    data = [x.strip("\n") for x in data]

    tour={}
    for k in range(len(data)):
        line = data[k]
        if line.find("Date") != -1 and line.find("Venue") != -1:
            continue
        line = line.replace("Download this Show", "")
        line = line.strip()
        if len(line) < 10:
            continue
        people = line[:4]
        date = line[4:14].strip()
        vals = date.split("-")
        location = line[15:].strip()        
        tour[date] = location
        print date,'\t',
        date = vals[1]+"-"+vals[2]+"-"+vals[0]
        tour[date] = location
        print date


    return tour


def analyze(directory, shortname):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue

        print ""
        print "=================================",directory,"================================="
        print ""

        basename = os.path.basename(root)
        dirname  = os.path.dirname(root)
        print dirname,'\t',basename
        extra = None
        dirs = []
        if dirname == directory:
            entdstdir = "enter/"+shortname
            fixdstdir = "fix/"+shortname
            errdstdir = "err/"+shortname
        else:
            extra = root.replace(directory, "")
            if extra[0] == "/": extra = extra[1:]
            dirs = extra.split("/")
            if len(dirs) > 1:
                print dirs
                dirs = dirs[:-1]
            else:
                dirs = None
                print "How did that happen?"
                print extra
                f()

            entdstdir = "enter/"+shortname
            fixdstdir = "fix/"+shortname
            errdstdir = "err/"+shortname
        if False:
            print '\tDir   =',directory
            print '\tExtra =',extra
            print '\tShort =',shortname
            print '\t',entdstdir
            print '\t',fixdstdir
            print '\t',errdstdir
            print ''
            continue

        cmd = None
        errcmd = "mv "+basename+"err/"+shortname
        fixcmd = "mv "+basename+"fix/"+shortname
        entercmd = "mv "+basename+"enter/"+shortname
        reason = "Good"

        isGood,reason = inspectDir(root, mp3s, False)
        if isGood:
            cmd = entercmd
        elif reason.find("ID3") != -1:
            cmd = errcmd
        else:
            cmd = fixcmd

            
        if cmd == entercmd:
            dstdir = entdstdir
        elif cmd == errcmd:
            dstdir = errdstdir
        else:
            dstdir = fixdstdir
        
        print "------>",dstdir
        print "dirs ->",dirs
        print "name ->",basename
        for dirval in dirs:
            dirpath = os.path.join(dstdir,dirval)
            if not os.path.exists(dstdir):
                print "Making",dstdir
                os.mkdir(dstdir)
            dstdir = dirpath

        print "Dstdir =>",dstdir
        print "Root   =>",root
        print "Reason =>",reason
        if not os.path.exists(dstdir):
            print "Making",dstdir
            os.mkdir(dstdir)
        #print "shutil.move(",root,",",dstdir,")"
        shutil.move(root,dstdir)

        print ""
        print "==================================================================================================="




def writeMetadata(root, mp3s, artist, album, shortname):
    basename = os.path.basename(root)
    vals = basename.split('.')
    date = vals[0].replace("dmb", "")
    for k,v in audio.iteritems():
        print k,v
    f()
    #if len(audio['album'][0]) > 5: 
    #    print "mv "+basename+" ../dmb-enter/"
    #    break

    length = audio['length'][0]
    minutes,seconds = songLength(length)
    
    tracknumber = k+1
    album = "Live at "+tourinfo[date]+" "+date
    print str(tracknumber)+" "+audio['tracknumber'][0]+"  "+str(minutes)+":"+str(seconds)+"\t"+mp3+"\t"+album
    audio['tracknumber'] = str(tracknumber)
    audio['album'] = album
    audio['artist'] = artist
    audio.save()


def findMp3s(root, files):
    mp3s=[]
    for ifile in files:
        ext = ifile[-4:]
        if ext == ".mp3" or ext == ".Mp3" or ext == ".MP3":
            mp3s.append(os.path.join(root, ifile))
    return mp3s


def printID3s(mp3s):
    for i in range(len(mp3s)):
        mp3 = mp3s[i]
        try:
            audio = EasyID3(mp3)
        except:
            print "Bad ID3 tag for",mp3
            continue

        print mp3,'\t',zip(audio.keys(), audio.values())


    
def showTrkNoData(debug, trackname, pattern, retvals, mvals):
    if mvals:
        mvals = [int(x) for x in mvals]
    if debug:
        print trackname,'\tPattern -> \"'+pattern+'\"\tResults ->',retvals,'\t==> ',mvals
    return mvals


def findTrkNo(currtrackname):
    mvals = None
    debug = False

    trackname = currtrackname.replace("11 O'Clock", "")
    #trackname = trackname.replace(".mp3", "")
    #trackname = trackname.replace("mp3", "")
    if debug:
        print "Trackname =>",trackname

    ######################################################################
    pattern = "SIDE [1-9]_[0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split("_")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "Track[0-9][0-9] [0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split()
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "Disc [1-9] - [0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split("-")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "disc[1-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][4:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "disc [1-9] t[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split('t')
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "CD[1-9]-[0-9][0-9]-"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][2:-1]
        mvals = mvals.split("-")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "Part_[1-9]_Tr\.[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split("_Tr.")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "Part_[1-9]_Tr[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = mvals.split("_Tr")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "disc one [0-9][0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][9:]
        mvals = [ 1, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "disc two [0-9][0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][9:]
        mvals = [ 2, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "\[[1-9]-[0-9][0-9]\]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split('-')
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[0-9][0-9] tr[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("tr")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "t[0-9][0-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = [ mvals[:2], mvals[2:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "D[1-9]T[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("T")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "D[1-9]t[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("t")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9]tr[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("tr")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9]tk[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("tk")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9] tr[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("tr")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9]t[0-9][0-9]\."
    #print "HERE",pattern,trackname
    retvals = re.findall(pattern, trackname)
    #print "RET",retvals
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("t")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)
    


    ######################################################################
    pattern = "s[1-9]t[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("t")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9][0-9][0-9]\_"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "d[1-9]t[0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("t")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "tr[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][2:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "t[0-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "t[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "D[1-9] Track [0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = mvals.split("Track")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]-Track [0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][:-1]
        mvals = mvals.split("-Track")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]-Track [0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][:-1]
        mvals = mvals.split("-Track")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "Track[0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][5:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "D[0-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "A[1-9] - "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-3]
        mvals = [ 1, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "B[1-9] - "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-3]
        mvals = [ 2, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "C[1-9] - "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-3]
        mvals = [ 3, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)



    ######################################################################
    pattern = "D[1-9] - "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[-1][1:-3]
        mvals = [ 4, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)




    ######################################################################
    ######################################################################
    ######################################################################


    ######################################################################
    pattern = "- [0-9][0-9] -"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][2:-2]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "- [0-9][0-9][0-9][0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][2:]
        mvals = [ mvals[:2], mvals[2:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = " -[1-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][2:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9][0-9]\. "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-2]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9]\. "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-2]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9]-[0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = mvals.split("-")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9][0-9][0-9]-"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9][0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9]-[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = mvals.split("-")
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[1-9][0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9] - "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-3]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]-"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9]\."
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9] "
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0][:-1]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)






    ######################################################################
    ######################################################################
    ######################################################################

    ######################################################################
    pattern = "one"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = [ 0, 1 ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)

    ######################################################################
    pattern = "two"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = [ 0, 2 ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)

    ######################################################################
    pattern = "SIDE A"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = [ 1, 1 ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)

    ######################################################################
    pattern = "SIDE B"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = [ 2, 1 ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)

    ######################################################################
    pattern = "[1-9][0-9][0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0]
        mvals = [ mvals[:1], mvals[1:] ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9][0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)


    ######################################################################
    pattern = "[0-9]"
    retvals = re.findall(pattern, trackname)
    if retvals:
        mvals = retvals[0]
        mvals = [ 0, mvals ]
        return showTrkNoData(debug, trackname, pattern, retvals, mvals)

    return [None,None]




    
    trk1a = re.compile(r'[0-9][0-9] - ')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = [ 0,mo1a.group()[:-3] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r's[1-9]-[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    #print trackname,'\t',mo1a
    if mo1a: mvals = mo1a.group()[1:-1].split('-')
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'disc[1-9][0-9][0-9]')
    mo1a = trk1a.search(trackname)
    if mo1a: 
        mval = mo1a.group()[4:]
        mvals = [ mval[:1], mval[1:] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'disc[1-9]track[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = mo1a.group()[4:-1].split("track")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'A[0-9][0-9] ')
    trk1b = re.compile(r'B[0-9][0-9] ')
    trk1c = re.compile(r'a[0-9][0-9] ')
    trk1d = re.compile(r'b[0-9][0-9] ')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    mo1d = trk1d.search(trackname)
    if mo1a:   mvals = [ 1, mo1a.group()[1:-1] ]
    if mo1b:   mvals = [ 2, mo1b.group()[1:-1] ]
    if mo1c:   mvals = [ 1, mo1c.group()[1:-1] ]
    if mo1d:   mvals = [ 2, mo1d.group()[1:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'A[0-9][0-9].')
    trk1b = re.compile(r'B[0-9][0-9].')
    trk1c = re.compile(r'a[0-9][0-9].')
    trk1d = re.compile(r'b[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    mo1d = trk1d.search(trackname)
    if mo1a:   mvals = [ 1, mo1a.group()[1:-1] ]
    if mo1b:   mvals = [ 2, mo1b.group()[1:-1] ]
    if mo1c:   mvals = [ 1, mo1c.group()[1:-1] ]
    if mo1d:   mvals = [ 2, mo1d.group()[1:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'd[1-9] tr[0-9][0-9].')
    trk1b = re.compile(r'd[1-9] t[0-9][0-9] ')
    trk1c = re.compile(r'd[1-9] t[0-9][0-9]')
    trk1d = re.compile(r'd[1-9]tr[0-9][0-9].')
    trk1e = re.compile(r'd[1-9]_t[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    mo1d = trk1d.search(trackname)
    mo1e = trk1e.search(trackname)
    #print trackname,'\t',mo1a,mo1b,mo1c
    if mo1a: mvals = mo1a.group()[1:-1].split("tr")
    elif mo1b: mvals = mo1b.group()[1:-1].split("t")
    elif mo1c: mvals = mo1c.group()[1:].split("t")
    elif mo1d: mvals = mo1d.group()[1:-1].split("tr")
    elif mo1e: mvals = mo1e.group()[1:-1].split("_t")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'd[1-9]t[1-9][0-9][0-9].')
    trk1b = re.compile(r'd[0-9][0-9]t[0-9][0-9].')
    trk1c = re.compile(r'd[1-9]t[0-9][0-9].')
    trk1d = re.compile(r'd[1-9]t[1-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    mo1d = trk1d.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split('t')
    elif mo1b: mvals = mo1b.group()[1:-1].split('t')
    elif mo1c: mvals = mo1c.group()[1:-1].split('t')
    elif mo1d:
        mval  = mo1d.group()[1:-1].split('t')
        mvals = [ mval[0], mval[1][1:] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals


    trk1a = re.compile(r'd[0-9][0-9]t[0-9][0-9] ')
    trk1b = re.compile(r'd[1-9]t[0-9][0-9] ')
    trk1c = re.compile(r'd[1-9]t[1-9] ')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split('t')
    elif mo1b: mvals = mo1b.group()[1:-1].split('t')
    elif mo1c: mvals = mo1c.group()[1:-1].split('t')
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals


    trk1a = re.compile(r'd[0-9][0-9]t[0-9][0-9]_')
    trk1b = re.compile(r'd[1-9]t[0-9][0-9]_')
    trk1c = re.compile(r'd[1-9]t[1-9]_')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split('t')
    elif mo1b: mvals = mo1b.group()[1:-1].split('t')
    elif mo1c: mvals = mo1c.group()[1:-1].split('t')
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r's[0-9][0-9]t[0-9][0-9].')
    trk1b = re.compile(r's[1-9]t[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split('t')
    elif mo1b: mvals = mo1b.group()[1:-1].split('t')
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'set[1-9]t[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = mo1a.group()[3:-1].split("t")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'[1-9]Track[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = mo1a.group()[:-1].split("Track")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trk1a = re.compile(r'cd[1-9]song[0-9][0-9].')
    trk1b = re.compile(r'cd[1-9]song[1-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    if mo1a:   mvals = mo1a.group()[2:-1].split("song")
    elif mo1b: mvals = mo1b.group()[2:-1].split("song")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'CD[1-9]_[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a:   mvals = mo1a.group()[2:-1].split("_")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'Disc [1-9] - [0-9][0-9].')
    mo1a = trk1a.search(trackname)
    #print trackname,'\t',mo1a
    if mo1a:   mvals = mo1a.group()[5:-1].split(" - ")
    #print mvals
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'D[0-9][0-9]T[0-9][0-9].')
    trk1b = re.compile(r'D[1-9]T[0-9][0-9].')
    trk1c = re.compile(r'D[1-9]_T[0-9][0-9]-')
    trk1d = re.compile(r'D[1-9] t[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    mo1c = trk1c.search(trackname)
    mo1d = trk1d.search(trackname)
    #print trackname,'\t',mo1a,mo1b,mo1c
    if mo1a: mvals = mo1a.group()[1:-1].split("T")
    elif mo1b: mvals = mo1b.group()[1:-1].split("T")
    elif mo1c: mvals = mo1c.group()[1:-1].split("_T")
    elif mo1d: mvals = mo1d.group()[1:-1].split("t")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'D[1-9]-[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split("-")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'CD[1-9] ')
    mo1a = trk1a.search(trackname)
    if mo1a:
        disc = mo1a.group()[2:-1]
        tmpname = trackname.replace(mo1a.group(), "")
        trk1a = re.compile(r'[1-9][0-9]')
        trk1b = re.compile(r' [1-9]')
        mo1a = trk1a.search(tmpname)
        mo1b = trk1b.search(trackname)
        if mo1a:   mvals = [ disc, mo1a.group() ]
        elif mo1b: mvals = [ disc, mo1b.group()[1:] ]
        #print tmpname,'\t',disc,'\t',mvals
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'D[1-9]-Track[0-9][0-9]-')
    trk1b = re.compile(r'D[1-9] Track [0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1a.search(trackname)
    if mo1a: mvals = mo1a.group()[1:-1].split("Track")
    if mo1b: mvals = mo1b.group()[1:-1].split("Track")
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'Track[1-9][0-9][0-9].')
    trk1b = re.compile(r'Track[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    if mo1a: 
        mvals = [ mo1a.group()[5:-3], mo1a.group()[6:-1] ]
    elif mo1b: 
        mvals = [ 1, mo1b.group()[5:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'Track [0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: 
        mvals = [ 0, mo1a.group()[6:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r't[0-9][0-9].')
    trk1b = re.compile(r't[1-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    print trackname,mo1a.group(),mo1b.group()
    if mo1a: mvals = [ 0,mo1a.group()[1:-1] ]
    elif mo1b: mvals = [ 0,mo1b.group()[1:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r't-[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    if mo1a: mvals = [ 0,mo1a.group()[2:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'tr[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    #print trackname,'\t',mo1a
    if mo1a: 
        mvals = [ 0, mo1a.group()[2:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'missing[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    #print trackname,'\t',mo1a
    if mo1a: 
        mvals = [ 0, mo1a.group()[7:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals


    trk1a = re.compile(r' [1-9][0-9][0-9] ')
    trk1b = re.compile(r'[1-9][0-9][0-9] ')
    trk1c = re.compile(r'-[1-9][0-9][0-9]-')
    trk1d = re.compile(r'[1-9][0-9][0-9].')
    mo1a = trk1a.search(trackname)    
    mo1b = trk1b.search(trackname)    
    mo1c = trk1c.search(trackname)    
    mo1d = trk1d.search(trackname)
    #print trackname,'\t',mo1a, mo1b, mo1c.group(), mo1d.group()
    if mo1a or mo1b or mo1c or mo1d:
        mvals = None
        if mo1a:   mvals = int(mo1a.group()[1:-1])
        elif mo1b: mvals = int(mo1b.group()[:-1])
        elif mo1c: mvals = int(mo1c.group()[1:-1])
        elif mo1d: mvals = int(mo1d.group()[:-1])
        if mvals:
            mval = mvals % 100
            dval = (mvals - mval)/100
            mvals = [ dval,mval ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'[0-9][0-9].')
    trk1b = re.compile(r'[0-9][0-9]_')
    mo1a = trk1a.search(trackname)
    mo1b = trk1b.search(trackname)
    if mo1a: mvals = [ 0,mo1a.group()[:-1] ]
    if mo1b: mvals = [ 0,mo1b.group()[:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    trkvals = trackname.split()
    if len(trkvals) > 0:
        try:
            trkno = int(trkvals[0])
            mvals = [ 0, trkno ]
        except:
            mvals = None
        if mvals:
            return mvals



    try:
        trkno = int(trackname[:2])
    except:
        trkno = None
    if trkno:
        mvals = None
        try:
            trknotest = int(trackname[:3])
        except:
            mvals = [ 0, trkno ]
        if mvals:
            return mvals



    trk1a = re.compile(r'd[1-9][0-9][0-9]')
    mo1a = trk1a.search(trackname)
    if mo1a: 
        mval = mo1a.group()[1:]
        mvals = [ mval[:1], mval[1:] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'[1-9][0-9][0-9]')
    mo1a = trk1a.search(trackname)
    if mo1a:
        mval = mo1a.group()
        mvals = [ mval[:1], mval[1:] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals



    trk1a = re.compile(r'[0-9][0-9] ')
    trk1b = re.compile(r'[0-9][0-9].')
    mo1a = trk1a.search(trackname)
    mo1b = trk1a.search(trackname)
    if mo1a: mvals = [ 0,mo1a.group()[:-1] ]
    if mo1b: mvals = [ 0,mo1b.group()[:-1] ]
    if mvals:
        mvals = [int(x) for x in mvals]
        return mvals




    return [None,None]




def isValid(yr,mn,dy):
    debug = False
    if debug:
        print "Year  ->",yr
        print "Month ->",mn
        print "Day   ->",dy
    old = datetime.date(1950, 1, 1)
    today = datetime.date.today()
    try:        
        year = int(yr)
    except:
        if debug: 
            print "Not a valid integer",yr
        return False

    try:        
        mon = int(mn)
    except:
        if debug: 
            print "Not a valid integer",mn
        return False

    try:        
        day = int(dy)
    except:
        if debug: 
            print "Not a valid integer",day
        return False


    try:
        thisdate = datetime.date(year, mon, day)
    except:
        return False
    if thisdate < old or thisdate > today:
        return False

    return True


def findDate(torr):
    albumdate = findDateRaw(torr)
    #print 'Date -->',torr,'\t',albumdate,'\t',type(albumdate)
    if albumdate:
        if isinstance(albumdate, tuple):
            if len(albumdate) == 3:
                datename = [albumdate[1], albumdate[2], albumdate[0]]
                datename = [str(x) for x in datename]
                sdate = "-".join(datename)
            else:
                sdate = "-".join(str(albumdate))
        else:
            sdate = str(albumdate)
    else:
        sdate = "None"
    return sdate


def findDateRaw(foldername):
    debug = False

    #DAY1  = "[0-3][0-9]"
    DAY1  = "(0[1-9]|1[0-9]|2[0-9]|3[0-1])"
    DAY2  = "([1-9]|1[0-9]|2[0-9]|3[0-1])"
    #MON1  = "[0-1][0-9]"
    MON1  = "(0[1-9]|1[012])"
    MON2  = "([1-9]|1[012])"
    MON3  = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    #MON1  = "^(0?[1-9]|1[012])$"
    YEAR1 = "[1-2][0-9][0-9][0-9]"
    YEAR2 = "[5-9][0-9]"
    YEAR3 = "([5-9][0-9]|0[1-9]|1[0-6])"
    #YEAR4 = "[0-9][0-9]"

    delims = ['-', '.', ' ', '_']
    dlms   = [ x.replace(".", "\.") for x in delims ]



    ##################################################################
    ##################################################################
    ##################################################################

    ##################################################################
    ## Ex YEAR1+MON1+DAY1  or  YEAR1+DAY1+MON1
    for j in range(len(delims)):
        compstr = YEAR1+dlms[j]+MON1+dlms[j]+DAY1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR1+dlms[j]+DAY1+dlms[j]+MON1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON1+DAY1+YEAR1  or  DAY1+MON1+YEAR1
    for j in range(len(delims)):
        compstr = MON1+dlms[j]+DAY1+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY1+dlms[j]+MON1+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex YEAR1+MON2+DAY1  or  YEAR1+DAY1+MON2
    for j in range(len(delims)):
        compstr = YEAR1+dlms[j]+MON2+dlms[j]+DAY1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR1+dlms[j]+DAY1+dlms[j]+MON2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON2+DAY1+YEAR1  or  DAY1+MON2+YEAR1
    for j in range(len(delims)):
        compstr = MON2+dlms[j]+DAY1+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY1+dlms[j]+MON2+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex YEAR3+MON1+DAY1  or  YEAR3+DAY1+MON1
    for j in range(len(delims)):
        compstr = YEAR3+dlms[j]+MON1+dlms[j]+DAY1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[0]) < 30: 
                vals[0] = str(2000+int(vals[0]))
            else:
                vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR3+dlms[j]+DAY1+dlms[j]+MON1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[0]) < 30: 
                vals[0] = str(2000+int(vals[0]))
            else:
                vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON1+DAY1+YEAR3  or  DAY1+MON1+YEAR3
    for j in range(len(delims)):
        compstr = MON1+dlms[j]+DAY1+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[2]) < 30: 
                vals[2] = str(2000+int(vals[2]))
            else:
                vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY1+dlms[j]+MON1+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[2]) < 30: 
                vals[2] = str(2000+int(vals[2]))
            else:
                vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex YEAR3+MON2+DAY1  or  YEAR3+DAY1+MON2
    for j in range(len(delims)):
        compstr = YEAR3+dlms[j]+MON2+dlms[j]+DAY1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[0]) < 30: 
                vals[0] = str(2000+int(vals[0]))
            else:
                vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR3+dlms[j]+DAY1+dlms[j]+MON2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[0]) < 30: 
                vals[0] = str(2000+int(vals[0]))
            else:
                vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON2+DAY1+YEAR3  or  DAY1+MON2+YEAR3
    for j in range(len(delims)):
        compstr = MON2+dlms[j]+DAY1+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[2]) < 30: 
                vals[2] = str(2000+int(vals[2]))
            else:
                vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY1+dlms[j]+MON2+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if int(vals[2]) < 30: 
                vals[2] = str(2000+int(vals[2]))
            else:
                vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex YEAR1+MON2+DAY2  or  YEAR1+DAY2+MON2
    for j in range(len(delims)):
        compstr = YEAR1+dlms[j]+MON2+dlms[j]+DAY2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR1+dlms[j]+DAY2+dlms[j]+MON2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON2+DAY2+YEAR1  or  DAY2+MON2+YEAR1
    for j in range(len(delims)):
        compstr = MON2+dlms[j]+DAY2+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY2+dlms[j]+MON2+dlms[j]+YEAR1
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex YEAR3+MON2+DAY2  or  YEAR3+DAY2+MON2
    for j in range(len(delims)):
        compstr = YEAR3+dlms[j]+MON2+dlms[j]+DAY2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]

        compstr = YEAR3+dlms[j]+DAY2+dlms[j]+MON2
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            vals[0] = str(1900+int(vals[0]))
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]



    ##################################################################
    ## Ex MON2+DAY2+YEAR3  or  DAY2+MON2+YEAR3
    for j in range(len(delims)):
        compstr = MON2+dlms[j]+DAY2+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

        compstr = DAY2+dlms[j]+MON2+dlms[j]+YEAR3
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            vals = m1.group().split(delims[j])
            vals[2] = str(1900+int(vals[2]))
            if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]





    ##################################################################
    ##################################################################
    ##################################################################







    ##################################################################
    ## Ex DAY1+MON3+YEAR3
    m1 = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}', foldername)
    m2 = re.findall(r'\d\d\.(?:January|February|March|April|May|June|July|August|September|October|November|December)\.\d{4}', foldername)
    m3 = re.findall(r'\d\d-(?:January|February|March|April|May|June|July|August|September|October|November|December)-\d{4}', foldername)
    m4 = re.findall(r'\d\d(?:January|February|March|April|May|June|July|August|September|October|November|December)\d{4}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    if len(m2) > 0: vals = m2[0].split(".")
    if len(m3) > 0: vals = m3[0].split("-")
    if len(m4) > 0: vals = [ m4[0][:2], m4[0][2:-4], m4[0][-4:] ]
    if len(vals) == 3:
        try:
            vals[1] = strptime(vals[1],'%B').tm_mon
        except:
            vals[1] = -1
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]

    m1 = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{2}', foldername)
    m2 = re.findall(r'\d\d\.(?:January|February|March|April|May|June|July|August|September|October|November|December)\.\d{2}', foldername)
    m3 = re.findall(r'\d\d-(?:January|February|March|April|May|June|July|August|September|October|November|December)-\d{2}', foldername)
    m4 = re.findall(r'\d\d(?:January|February|March|April|May|June|July|August|September|October|November|December)\d{2}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    if len(m2) > 0: vals = m2[0].split(".")
    if len(m3) > 0: vals = m3[0].split("-")
    if len(m4) > 0: vals = [ m4[0][:2], m4[0][2:-2], m4[0][-2:] ]
    if len(vals) == 3:
        try:
            vals[1] = strptime(vals[1],'%B').tm_mon
        except:
            vals[1] = -1
        if int(vals[2]) < 30: 
            vals[2] = str(2000+int(vals[2]))
        else:
            vals[2] = str(1900+int(vals[2]))
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    ##################################################################
    ## Ex DAY1+MON3+YEAR3
    m1 = re.findall(r'\d\d\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}', foldername)
    m2 = re.findall(r'\d\d\.(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.\d{4}', foldername)
    m3 = re.findall(r'\d\d-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4}', foldername)
    m4 = re.findall(r'\d\d(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{4}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    if len(m2) > 0: vals = m2[0].split(".")
    if len(m3) > 0: vals = m3[0].split("-")
    if len(m4) > 0: vals = [ m4[0][:2], m4[0][2:5], m4[0][5:] ]
    if len(vals) == 3:
        try:
            vals[1] = strptime(vals[1],'%b').tm_mon
        except:
            vals[1] = -1
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]

    m1 = re.findall(r'\d\d\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{2}', foldername)
    m2 = re.findall(r'\d\d\.(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.\d{2}', foldername)
    m3 = re.findall(r'\d\d-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}', foldername)
    m4 = re.findall(r'\d\d(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{2}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    if len(m2) > 0: vals = m2[0].split(".")
    if len(m3) > 0: vals = m3[0].split("-")
    if len(m4) > 0: vals = [ m4[0][:2], m4[0][2:5], m4[0][5:] ]
    if len(vals) == 3:
        try:
            vals[1] = strptime(vals[1],'%b').tm_mon
        except:
            vals[1] = -1
        if int(vals[2]) < 30: 
            vals[2] = str(2000+int(vals[2]))
        else:
            vals[2] = str(1900+int(vals[2]))
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]




    ##################################################################
    ## Ex DAY1+MON3+YEAR3
    m1 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d\d\s\d{4}', foldername)
    m2 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d\s\d{4}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    elif len(m2) > 0: vals = m2[0].split()
    if len(vals) == 3:
        try: vals[0] = strptime(vals[0],'%b').tm_mon
        except: vals[0] = -1
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

    m1 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d\d,\s\d{4}', foldername)
    m2 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d,\s\d{4}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    elif len(m2) > 0: vals = m2[0].split()
    if len(vals) == 3:
        vals[1] = vals[1][:-1]
        try: vals[0] = strptime(vals[0],'%b').tm_mon
        except: vals[0] = -1
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

    m1 = re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d\dst\s\d{4}', foldername)
    m2 = re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d\dnd\s\d{4}', foldername)
    m3 = re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d\dth\s\d{4}', foldername)
    vals = []
    if len(m1) > 0: vals = m1[0].split()
    elif len(m2) > 0: vals = m2[0].split()
    elif len(m3) > 0: vals = m3[0].split()
    if len(vals) == 3:
        vals[1] = vals[1][:-2]
        try: vals[0] = strptime(vals[0],'%B').tm_mon
        except: vals[0] = -1
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]



    ##################################################################
    ##################################################################
    ##################################################################


    ##################################################################
    ## Ex MON1DAY1YR3  or  YR3MON1DAY1
    compstr = MON1+DAY1+YEAR3
    d1 = re.compile(compstr)
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group()
        vals = [ vals[:2], vals[2:4], vals[4:] ]
        if int(vals[2]) < 30: 
            vals[2] = str(2000+int(vals[2]))
        else:
            vals[2] = str(1900+int(vals[2]))
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]

    compstr = YEAR3+MON1+DAY1
    d1 = re.compile(compstr)
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group()
        vals = [ vals[:2], vals[2:4], vals[4:] ]
        if int(vals[0]) < 30: 
            vals[0] = str(2000+int(vals[0]))
        else:
            vals[0] = str(1900+int(vals[0]))
        if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]



    ##################################################################
    ## Ex YEAR1
    compstr = YEAR1
    d1 = re.compile(compstr)
    m1 = d1.search(foldername)
    if m1:
        vals = [1, 1, m1.group()]
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]



    ##################################################################
    ## Ex YEAR3
    compstr = YEAR3
    d1 = re.compile(compstr)
    m1 = d1.search(foldername)
    if m1:
        vals = [1, 1, m1.group()]
        if int(vals[2]) < 30: 
            vals[2] = str(2000+int(vals[2]))
        else:
            vals[2] = str(1900+int(vals[2]))
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]


    return None


    ##################################################################
    ## Ex MON1+DAY1+YEAR1
    for j in range(len(delims)):
        compstr = MON1+dlms[j]+DAY1+dlms[j]+YEAR1
        if debug: print foldername,'\t',delim,'\t',dlms[j],'\t',compstr
        d1 = re.compile(compstr)
        m1 = d1.search(foldername)
        if m1:
            if debug: print 'dlm --(',dlms[j],')\t\t',m1.group()
            vals = m1.group().split(delims[j])
            if debug: print 'vals--',vals
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]


    return None


    ##################################################################
    ## Ex YEAR-MN-DY
    d1 = re.compile(r'[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]')
    d2 = re.compile(r'[1-2][0-9][0-9][0-9]\.[0-1][0-9]\.[0-3][0-9]')
    d3 = re.compile(r'[1-2][0-9][0-9][0-9] [0-1][0-9] [0-3][0-9]')
    d4 = re.compile(r'[1-2][0-9][0-9][0-9]_[0-1][0-9]_[0-3][0-9]')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    m3 = d3.search(foldername)
    m4 = d4.search(foldername)
    print foldername,'\t',m1,m2,m3,m4
    if m1 or m2 or m3 or m4:
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if m3: vals = m3.group().split(" ")
        if m4: vals = m4.group().split("_")
        print vals
        if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]



    ##################################################################
    ## Ex YEAR-DY-MN
    d1 = re.compile(YEAR1+"-"+DAY1+"-"+MON1)
    d2 = re.compile(YEAR1+"\."+DAY1+"\."+MON1)
    d3 = re.compile(YEAR1+" "+DAY1+" "+MON1)
    d4 = re.compile(YEAR1+"_"+DAY1+"_"+MON1)
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    m3 = d3.search(foldername)
    m4 = d4.search(foldername)    
    if m1 or m2 or m3 or m4:
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if m3: vals = m3.group().split(" ")
        if m4: vals = m4.group().split("_")
        if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]


    return None

    ##################################################################
    ## Ex MN-DY-YEAR
    d1 = re.compile(r'[0-1][0-9]-[0-3][0-9]-[1-2][0-9][0-9][0-9]')
    d2 = re.compile(r'[0-1][0-9]\.[0-3][0-9]\.[1-2][0-9][0-9][0-9]')
    d3 = re.compile(r'[0-1][0-9] [0-3][0-9] [1-2][0-9][0-9][0-9]')
    d4 = re.compile(r'[0-1][0-9]_[0-3][0-9]_[1-2][0-9][0-9][0-9]')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    m3 = d3.search(foldername)
    m4 = d4.search(foldername)    
    if m1 or m2 or m3 or m4:
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if m3: vals = m3.group().split(" ")
        if m4: vals = m4.group().split("_")
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]



    ##################################################################
    ## Ex DY-MN-YEAR
    d1 = re.compile(r'[0-1][0-9]-[0-3][0-9]-[1-2][0-9][0-9][0-9]')
    d2 = re.compile(r'[0-1][0-9]\.[0-3][0-9]\.[1-2][0-9][0-9][0-9]')
    d3 = re.compile(r'[0-1][0-9] [0-3][0-9] [1-2][0-9][0-9][0-9]')
    d4 = re.compile(r'[0-1][0-9]_[0-3][0-9]_[1-2][0-9][0-9][0-9]')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    m3 = d3.search(foldername)
    m4 = d4.search(foldername)    
    if m1 or m2 or m3 or m4:
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if m3: vals = m3.group().split(" ")
        if m4: vals = m4.group().split("_")
        if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]




    ##################################################################
    ## Ex 1984-05-9
    d1 = re.compile(r'\d\d\d\d-\d\d-\d')
    d2 = re.compile(r'\d\d\d\d\.\d\d\.\d')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    if m1 or m2:
        vals = None
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if vals:
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]


    ##################################################################
    ## Ex 1984-05-9
    d1 = re.compile(r'\d\d\d\d-\d-\d\d')
    d2 = re.compile(r'\d\d\d\d\.\d\.\d\d')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    if m1 or m2:
        vals = None
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if vals:
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]


    ##################################################################
    ## Ex 1984-5-9
    d1 = re.compile(r'\d\d\d\d-\d-\d')
    d2 = re.compile(r'\d\d\d\d\.\d\.\d')
    m1 = d1.search(foldername)
    m2 = d2.search(foldername)
    if m1 or m2:
        vals = None
        if m1: vals = m1.group().split("-")
        if m2: vals = m2.group().split(".")
        if vals:
            if isValid(vals[0],vals[1],vals[2]): return vals[0],vals[1],vals[2]
            if isValid(vals[0],vals[2],vals[1]): return vals[0],vals[2],vals[1]


    ##################################################################
    ## Ex 05-09-1984
    d1 = re.compile(r'\d\d-\d\d-\d\d\d\d')
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group().split("-")
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]


    ##################################################################
    ## Ex 05-9-1984
    d1 = re.compile(r'\d\d-\d\d-\d\d\d\d')
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group().split("-")
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]


    ##################################################################
    ## Ex 5-09-1984
    d1 = re.compile(r'\d-\d\d-\d\d\d\d')
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group().split("-")
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]


    ##################################################################
    ## Ex 5-9-1984
    d1 = re.compile(r'\d-\d-\d\d\d\d')
    m1 = d1.search(foldername)
    if m1:
        vals = m1.group().split("-")
        if isValid(vals[2],vals[0],vals[1]): return vals[2],vals[0],vals[1]
        if isValid(vals[2],vals[1],vals[0]): return vals[2],vals[1],vals[0]



    date1 = re.compile(r'\d\d-\d\d-\d\d')
    mo1 = date1.search(foldername)
    if mo1:
        if mo1: mo = mo1.group().split("-")
        y = mo[2]
        if int(y) < 50:
            y = "20"+y
        else:
            y = "19"+y
        m = mo[0]
        d = mo[1]
        return y,m,d




    date1 = re.compile(r'\d-\d\d-\d\d')
    date2 = re.compile(r'\d-\d-\d\d')
    mo1 = date1.search(foldername)
    mo2 = date2.search(foldername)
    if mo1 or mo2:
        if mo1: mo = mo1.group().split("-")
        if mo2: mo = mo2.group().split("-")
        y = mo[2]
        if int(y) < 50:
            y = "20"+y
        else:
            y = "19"+y
        m = mo[0]
        d = mo[1]
        return y,m,d


    date1 = re.compile(r'\d\d\d\d-\d\d\d\d')
    mo1 = date1.search(foldername)
    if mo1: return mo1.group()


    date1 = re.compile(r'\d\d\d\d\d\d\d\d')
    mo1 = date1.search(foldername)
    if mo1:
        val = mo1.group()
        y1 = val[:4]
        y2 = val[4:]
        if int(y1) > 1950 and int(y1) < 2050:
            y = val[:4]
            m = val[4:6]
            d = val[6:]
            return y,m,d
        elif int(y2) > 1950 and int(y2) < 2050:
            y = val[4:]
            m = val[:2]
            d = val[2:4]
            return y,m,d
        else:
            return val


    date1 = re.compile(r'\d\d\d\d\d\d')
    mo1 = date1.search(foldername)
    if mo1:
        val = mo1.group()
        y1 = val[:2]
        y2 = val[4:]
        if int(y1) > 31:
            y = "19"+y1
            m = val[2:4]
            d = val[4:]
            return y,m,d
        if int(y2) > 31:
            y = "19"+y2
            m = val[:2]
            d = val[2:4]
            return y,m,d
        return val

    date1 = re.compile(r'\d\d\d\d')
    mo1 = date1.search(foldername)
    if mo1: return mo1.group()


    return None



def getTrackNumbers(mp3s, trknomap, force = False):
    ntrks = 0
    for k1,v1 in trknomap.iteritems():
        ntrks += len(v1.keys())
    #print ntrks,'\t',len(mp3s)
    if ntrks == len(mp3s) or force:
        trknums=[]
        for k in range(len(mp3s)): trknums.append(0)
        discs = sorted(trknomap.keys())
        for idisc in range(len(discs)):
            nprev = 0
            for ii in range(idisc, 0, -1):
                nprev += len(trknomap[discs[ii-1]])
            for trkno,mp3no in trknomap[discs[idisc]].iteritems():
                #print mp3no,'\t',trkno,'\t',trkno + nprev
                trknums[mp3no] = trkno + nprev
        return trknums
    return None




def writeTrackNumbers(directory, test, force):
    if force: test = False
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        trknomap={}
        nTrks = 0
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            try:
                audio = EasyID3(mp3)
            except:
                foundBadID3 = True
                break

            if audio.get('tracknumber'):
                tracknumber = audio['tracknumber'][0]
                if len(tracknumber) > 0 and tracknumber != "0": nTrks += 1


            trknovals = findTrkNo(os.path.basename(mp3))
            #print mp3,'\t',trknovals
            if trknovals[0] != None:
                disc = trknovals[0]
                tkno = trknovals[1]                
                if trknomap.get(disc) == None:
                    trknomap[disc] = {}
                if trknovals[1] != None:
                    trknomap[disc][tkno] = k



        print "\n==========================================================================="
        if nTrks == len(mp3s) and not force:
            print "No need to inspect",root
            continue
        else:
            print "Inspect:",root,"  \t(",nTrks," / ",len(mp3s),")"
        trknos = getTrackNumbers(mp3s, trknomap, force)
        if trknos:
            if test:
                print "  Found track number order."
                continue
            else:
                print "  Found track number order. Writing metadata."

            for k in range(len(mp3s)):
                mp3 = mp3s[k]
                try:
                    audio = EasyID3(mp3)
                except:
                    break
                trkno = k+1
                audio['tracknumber'] = str(trknos[k])
                audio.save()
        else:
            print "  Could not determine track order."
            if len(mp3s) > 0:
                print "  -->",os.path.basename(mp3s[0])
            print "  -->",trknomap
            print ""
            print ""


def writeArtist(directory, artist, force):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        print "\n==========================================================================="
        print "  Writing artist",artist,"to metadata."
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            audio = EasyID3(mp3)
            audio['artist'] = artist
            audio.save()

def fixFoldername(root, directory, artist = None):
    foldername = root.replace(directory,"")
    if foldername[0] == "/": foldername = foldername[1:]
    foldername = foldername.replace("/", " -- ")
    foldername = foldername.replace(".flacf", "")
    foldername = foldername.replace(".shnf", "")
    foldername = foldername.replace(".flac", "")
    foldername = foldername.replace(".shn", "")
    if artist:
        if foldername[:len(artist)].title() == artist.title():
            foldername = foldername[len(artist):]
    foldername = foldername.strip()
    f0 = foldername[0]
    if f0 == "-" or f0 == "_" or f0 == "." or f0 == ";":
        foldername = foldername[1:]
        foldername = foldername.strip()
    f0 = foldername[0]
    if f0 == "-" or f0 == "_" or f0 == "." or f0 == ";":
        foldername = foldername[1:]
        foldername = foldername.strip()
    foldername = foldername.replace(".", "-")
    foldername = foldername.replace("_", "-")
    foldername = foldername.replace("1976-00-00 - 1981-08-31 - The Boy Tour -- ", "The Boy Tour -- ")
    foldername = foldername.replace("1987-04-02 - 1988-11-04 - ", "")
    foldername = foldername.replace("1982-12-01 - 1983-12-18 - ", "")
    foldername = foldername.replace("1984-07-08 - 1987-03-27 - ", "")
    return foldername


def writeAlbumName(directory, albumname):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        print "\n==========================================================================="
        print "  Writing album",albumname,"to metadata for",root
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            audio = EasyID3(mp3)
            audio['album'] = albumname
            audio.save()




def writeAlbum(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        albums=Counter()
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            try:
                audio = EasyID3(mp3)
                if audio.get('album'):
                    album = audio['album'][0]
                    if len(album) > 0:
                        albums[album] += 1
            except:
                continue
        album = None
        if len(albums) > 0:
            for k,v in albums.most_common(1):
                album = k
                break
        if album:
            print "\n==========================================================================="
            print "  Writing album",album,"to metadata for",root
            for k in range(len(mp3s)):
                mp3 = mp3s[k]
                audio = EasyID3(mp3)
                audio['album'] = album
                audio.save()
        else:
            foldername = fixFoldername(root, directory)
            albumdate = findDate(foldername)
            if albumdate:
                if isinstance(albumdate, tuple):
                    if len(albumdate) == 3:
                        datename = [albumdate[1], albumdate[2], albumdate[0]]
                        album = "Live on " + "-".join(datename) + " -- "+foldername
                    else:
                        album = "Live in " + "-".join(albumdate) + " -- " + foldername
                else:
                    album = "Live on " + albumdate + " -- "+foldername
            else:
                album = foldername
            album = unicode(album, errors='ignore').title()
            print "  Writing album",album,"to metadata for",root
            for k in range(len(mp3s)):
                mp3 = mp3s[k]
                audio = EasyID3(mp3)
                audio['album'] = album
                audio.save()
            print "\t---> Album coming from command line. Done."



def fixlen(name, size):
    nname = str(name)
    while len(nname) < size:
        nname += " "
    return nname


def showID3s(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        print "\n=================================",root,"================================="
        print fixlen("Name",50),fixlen("Trk",10),fixlen("Artist",40),fixlen("Album",40)
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            try:
                audio = EasyID3(mp3)
            except:
                foundBadID3 = True
                break

            print fixlen(os.path.basename(mp3),50),fixlen(audio.get("tracknumber"),10),fixlen(audio.get("artist"),40),fixlen(audio.get("album"),40)
        print "==================================================================\n"

            

def inspectDir(root, mp3s, show = True):
    foundBadID3=False
    foundTrackNo=False
    foundUnknown=False
    foundAlbum=False
    foundArtist=False
    isGood=None
    doIDs=[True, True, True]
    n0s = 0
    reason = "Good"
        

    for k in range(len(mp3s)):
        mp3 = mp3s[k]
        try:
            audio = EasyID3(mp3)
        except:
            foundBadID3 = True
            reason = "Broken ID3."
            break


        if doIDs[0]:
            if audio.get('tracknumber'):
                tracknumber = audio['tracknumber'][0]
                if tracknumber == "0":
                    n0s += 1
                    foundTrackNo = True
                    if n0s > 1:
                        foundTrackNo = False
                        doIDs[0] = False
                        reason = "Tracknumber is zero."
                elif len(tracknumber) > 0:
                    foundTrackNo = True
                else:
                    foundTrackNo = False
                    doIDs[0] = False
                    reason = "Tracknumber is empty."
            else: 
                foundTrackNo = False
                doIDs[0] = False
                reason = "No Tracknumber."


        if doIDs[1]:
            if audio.get('album'):
                album = audio['album'][0]
                if album.title().find("Unknown") != -1:
                    reason = "Unknown Album."
                    foundUnknown = True
                if len(album) > 0:
                    foundAlbum = True
                else:
                    foundAlbum = False
                    doIDs[1] = False
                    reason = "Album is empty."
            else:
                foundAlbum = False
                doIDs[1] = False
                reason = "No Album."


        if doIDs[2]:
            if audio.get('artist'):
                artist = audio['artist'][0]
                if artist.title().find("Unknown") != -1:
                    foundUnknown = True
                    reason = "Unknown Artist."
                if len(artist) > 0:
                    foundArtist = True
                else:
                    foundArtist = False
                    doIDs[2] = False
                    reason = "Artist is empty."
            else:
                foundArtist = False
                doIDs[2] = False
                reason = "No Artist."


    isGood = (not foundBadID3) & foundTrackNo & (not foundUnknown) & foundAlbum & foundArtist
    if show:
        print "======================================================================================="
        print "Inspect [",root,"]"
        print " -> Found",len(mp3s),"mp3s."
        if foundBadID3:      print " -> Track ID3 is corrupt."
        if not foundTrackNo: print " -> Track numbers not written."
        if foundUnknown:     print " -> Track badly written artist or album."
        if not foundAlbum:   print " -> Track album not written."
        if not foundArtist:  print " -> Track artist not written."
        if isGood:
           print " -> Folder looks good."
        else:
           print " -> Bad folder."
        print "======================================================================================="
        print ""

    return isGood,reason



def inspect(directory):
    show = True
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        isGood,reason = inspectDir(root, mp3s, show)


def check(directory, shortname, artist, test, cities):
    writeAll = False
    onlyTest = not test
    onlyTrackNumbers = False
    onlyArtist = False
    onlyAlbum = False
    if onlyTest:
        onlyTrackNumbers = False
        onlyArtist = False
        onlyAlbum = False
    if writeAll:
        onlyTest = False
        onlyTrackNumbers = False
        onlyArtist = False
        onlyAlbum = False
    

    albumtypes={}
    albumcounter=Counter()
    atypes=["BadID3","TrkNo","Unknw","Album","Artist","Empty"]
    results={}
    for at in atypes:
        albumtypes[at] = []
    print "BadID3\tTrkNo\tUnkwn\tAlbum\tArt\t\tName"


    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        foldername = root.replace(directory,"")
        if foldername[0] == "/": foldername = foldername[1:]
        foldername = foldername.replace("/", " -- ")
        foldername = foldername.replace(".flacf", "")
        foldername = foldername.replace(".shnf", "")
        foldername = foldername.replace(".flac", "")
        foldername = foldername.replace(".shn", "")
        if foldername[:len(artist)].title() == artist.title():
            foldername = foldername[len(artist):]
        foldername = foldername.strip()
        f0 = foldername[0]
        if f0 == "-" or f0 == "_" or f0 == "." or f0 == ";":
            foldername = foldername[1:]
            foldername = foldername.strip()
        f0 = foldername[0]
        if f0 == "-" or f0 == "_" or f0 == "." or f0 == ";":
            foldername = foldername[1:]
            foldername = foldername.strip()
        foldername = foldername.replace(".", "-")
        foldername = foldername.replace("_", "-")
        foldername = foldername.replace("1976-00-00 - 1981-08-31 - The Boy Tour -- ", "The Boy Tour -- ")
        foldername = foldername.replace("1987-04-02 - 1988-11-04 - ", "")
        foldername = foldername.replace("1982-12-01 - 1983-12-18 - ", "")
        foldername = foldername.replace("1984-07-08 - 1987-03-27 - ", "")
        foundBadID3=False
        foundTrackNo=False
        foundUnknown=False
        foundAlbum=False
        foundArtist=False
        nameOrder=True
        TrknameOrder=True
        ptrknovals=[None,None]
        trknos=[]
        trknomap={}
        for k in range(len(mp3s)):
            mp3 = mp3s[k]
            try:
                audio = EasyID3(mp3)
            except:
                foundBadID3 = True
                break

            
            trkno = str(k+1)
            if mp3.find(trkno) == -1:
                nameOrder = False


            trknovals = findTrkNo(os.path.basename(mp3))
            if trknovals[0] != None:
                disc = trknovals[0]
                tkno = trknovals[1]                
                if trknomap.get(disc) == None:
                    trknomap[disc] = {}
                if trknovals[1] != None:
                    trknomap[disc][tkno] = k


            #print mp3,'\t',trknovals
            if trknovals[0] != None:
                if ptrknovals[0] == None:
                    ptrknovals[0] = trknovals[0]
                    ptrknovals[1] = trknovals[1]
                    trknos.append(trknovals[1])
                else:
                    discdiff = trknovals[0] - ptrknovals[0]
                    trkdiff  = trknovals[1] - ptrknovals[1]
                    if discdiff == 0 and trkdiff == 1:
                        ptrknovals[0] = trknovals[0]
                        ptrknovals[1] = trknovals[1]
                        trknos.append(trknovals[1])
                    elif discdiff == 1 and trkdiff < 0:
                        ptrknovals[0] = trknovals[0]
                        ptrknovals[1] = trknovals[1]
                        trknos.append(trknos[-1]+1)
                    else:
                        TrknameOrder = False
            else:
                TrknameOrder = False

            if ptrknovals[0] == None:
                TrknameOrder = False
      


            if audio.get('tracknumber'):
                tracknumber = audio['tracknumber'][0]
                if len(tracknumber) > 0 and tracknumber != "0": foundTrackNo = True
                
            if audio.get('album'):
                album = audio['album'][0]
                if album.title().find("Unknown") != -1: foundUnknown = True
                if len(album) > 0: foundAlbum = True

            if audio.get('artist'):
                artistname = audio['artist'][0]
                if artistname.title().find("Unknown") != -1: foundUnknown = True
                if len(artistname) > 0: foundArtist = True


        ####################################################################################################
        ##
        ## Print
        ##
        ####################################################################################################
        print root
        print "\t---> Found",len(mp3s),"mp3s."
        if foundBadID3:
            print "\t---> Bad ID3 in metadata."
            continue





        ####################################################################################################
        ##
        ## Order from Name!
        ##
        ####################################################################################################
        if not foundTrackNo:
            trknums = getTrackNumbers(mp3s, trknomap)
            if trknums:
                print "\t---> Track numbers found using out-of-order findTrkNo() function. Fixing track numbers."
                trknos = trknums
                TrknameOrder = True
                #for k in range(len(mp3s)):
                #    print k,'\t',trknos[k],'\t',mp3s[k]
            else:
                print "\t---> Track numbers not found using out-of-order findTrkNo() function."





        ####################################################################################################
        ##
        ## Order from Name!
        ##
        ####################################################################################################
        if TrknameOrder and not foundTrackNo:
            if not onlyTest:
                print "\t---> Track numbers found using new findTrkNo() function. Writing metadata."
                foundTrackNo = True
                nameOrder = True
                for k in range(len(mp3s)):
                    mp3 = mp3s[k]
                    audio = EasyID3(mp3)
                    trkno = k+1
                    audio['tracknumber'] = str(trknos[k])
                    audio.save()
                print "\t---> Track numbers come from name. Writing metadata - Done."
            else:
                print "\t---> Track numbers found using new findTrkNo() function."
        else:
            print "\t---> No idea about track numbers from findTrkNo()."



        ####################################################################################################
        ##
        ## Order from Name!
        ##
        ####################################################################################################
        if nameOrder:
            if not foundTrackNo:
                print "\t---> Track numbers come from name."
                if not onlyTest:
                    print "\t---> Track numbers come from name. Writing metadata."
                    for k in range(len(mp3s)):
                        mp3 = mp3s[k]
                        audio = EasyID3(mp3)
                        trkno = k+1
                        audio['tracknumber'] = str(trkno)
                        audio.save()
                    print "\t---> Track numbers come from name. Writing metadata for track number and continuing - Done."
            else:
                print "\t---> Track numbers already written."
        else:
            if not foundTrackNo:
                print "\t---> No idea about track numbers."
            else:
                print "\t---> Track numbers already written."
        if onlyTrackNumbers: continue





        ####################################################################################################
        ##
        ## Artist
        ##
        ####################################################################################################
        if not foundArtist:
            print "\t---> Artist coming from command line."
            if not onlyTest:
                print "\t---> Artist coming from command line. Writing metadata."
                for k in range(len(mp3s)):
                    mp3 = mp3s[k]
                    audio = EasyID3(mp3)
                    audio['artist'] = artist
                    audio.save()
                print "\t---> Artist coming from command line. Done."
        else:
            print "\t---> Artist already written."
        if onlyArtist: continue





        ####################################################################################################
        ##
        ## Album
        ##
        ####################################################################################################
        if not foundAlbum:
            albumdate = findDate(foldername)
            if albumdate:
                if isinstance(albumdate, tuple):
                    if len(albumdate) == 3:
                        datename = [albumdate[1], albumdate[2], albumdate[0]]
                        album = "Live on " + "-".join(datename) + " -- "+foldername
                    else:
                        album = "Live in " + "-".join(albumdate) + " -- " + foldername
                else:
                    album = "Live on " + albumdate + " -- "+foldername
            else:
                album = foldername
            album = unicode(album, errors='ignore').title()

            print "\t---> Album coming from command line:",album
            if not onlyTest:
                print "\t---> Album coming from command line. Writing metadata."
                for k in range(len(mp3s)):
                    mp3 = mp3s[k]
                    audio = EasyID3(mp3)
                    audio['album'] = album
                    audio.save()
                print "\t---> Album coming from command line. Done."
        else:
            print "\t---> Album already written."
        if onlyAlbum: continue



        continue
        

        ####################
        ## Order from Name!
        ####################
        print root
        if nameOrder:
            if foundAlbum:
                print "\tArtist ->",artist
                print "\tAlbum ->",album
                print "\tFill order with name order."
            else:
                print "\tArtist ->",artist
                albumdate = findDate(foldername)
                if albumdate:
                    if len(albumdate) == 3:
                        tmp = albumdate[0]
                        albumdate[0] = albumdate[1]
                        tmp = albumdate[1]
                        albumdate[1] = albumdate[2]
                        album = "Live on "+"-"+albumdate[1]+"-"+albumdate[2]+"-"+albumdate[0] + " -- "+foldername
                    else:
                        album = "Live in "+"-"+"-".join(albumdate) + " -- " + foldername
                else:
                    album = foldername
                print "\tFull album with folder name. \t(",album,")",'\t'
                print "\tFill order with name order."
        else:
            if foundAlbum:
                print "\tArtist ->",artist
                print "\tAlbum ->",album
                if foundTrackNo:
                    print "\tTrack number from ID3."
                else:
                    print "No Track Number info."
            else:
                print "\tArtist ->",artist
                albumdate = findDate(foldername)
                if albumdate:
                    if len(albumdate) == 3:
                        tmp = albumdate[0]
                        albumdate[0] = albumdate[1]
                        tmp = albumdate[1]
                        albumdate[1] = albumdate[2]
                        album = "Live on "+"-"+albumdate[1]+"-"+albumdate[2]+"-"+albumdate[0] + " -- "+foldername
                    else:
                        album = "Live in "+"-"+"-".join(albumdate) + " -- " + foldername
                else:
                    album = foldername
                print "\tFull album with folder name. \t(",album,")",'\t'
                if foundTrackNo:
                    print "\tTrack number from ID3."
                else:
                    print "No Track Number info."
        continue


        category=[]
        if foundBadID3: 
            #albumtypes["BadID3"].append(root)
            category.append("BadID3")
        if foundArtist:
            #albumtypes["Artist"].append(root)
            category.append("Artist")
        if foundAlbum:
            #albumtypes["Album"].append(root)
            category.append("Album")
        if foundUnknown:
            #albumtypes["Unknw"].append(root)
            category.append("Unknw")
        if foundTrackNo:
            #albumtypes["TrkNo"].append(root)
            category.append("TrkNo")

        if len(category) == 0:
            category = "Empty"
        else:
            category = ",".join(sorted(category))
        albumcounter[category] += 1

        print foundBadID3,'\t',foundUnknown,'\t',foundTrackNo,'\t',foundAlbum,'\t',foundArtist,'\t',category,'\t\t',root[:50]

        if category == "Album":
            printID3s(mp3s)
            print "Name Order ->",nameOrder
            f()
            

    for catval in albumcounter.most_common(5000):
        print catval[1],'\t',catval[0]

        


def fix(directory, artist, comment):
    for root, dirs, files in os.walk(directory, topdown=False):
        mp3s=[]
        for ifile in files:
            ext = ifile[-4:]
            if ext == ".mp3":
                mp3s.append(os.path.join(root, ifile))

        if len(mp3s) == 0:
            continue
        basename = os.path.basename(root)
        dirname  = os.path.dirname(root)

        album = root.replace(directory, "")
        if len(album) > 0:
            if album[0] == "/": album = album[1:]
        vals = album.split("/")
        if len(vals) > 1:
            last = vals[-1].title()
            print last
            if last == "Flac":
                vals = vals[:-1]
        album = "__".join(vals).title()
        lenartist = len(artist)
        if album[:lenartist] == artist:
            album = album[lenartist:].strip()
        if len(album) > 0:
            if album[0] == "_": album = album[1:]
        if len(album) > 0:
            if album[:2] == "- ": album = album[2:].strip()

        if len(comment) > 0:
            album = comment + " " + album
        print len(mp3s),'\t',album,'\t;;\t',root


def merge(directory):
    sname = os.path.basename(directory)
    ndirs = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        if root == directory: continue
        mp3s = findMp3s(root, files)
        if len(mp3s) == 0: continue
        dstpath = os.path.join(sname,root)
        dstpath = dstpath.replace(directory+"/", "")
        basename = os.path.basename(dstpath)
        dirname = os.path.dirname(dstpath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if os.path.exists(dstpath):
            for mp3 in mp3s:
                src = mp3
                dst = os.path.join(dstpath,"/")
                print "shutil.move(",src,",",dst,")"
                shutil.move(src,dst)
        else:
            dstdir = sname+"/"
            print "shutil.move(",root,",",dirname,")"
            shutil.move(root,dirname)
            
        ndirs += 1
        print ""
        print ""
        #print sname,root
    print "Moved",ndirs,"directories."

def main(args):
    dirval = args.dirval[0]
    if not os.path.exists(dirval):
        print "--> ",dirval," <-- is not a directory"

    if args.shortname == None:
        shortname = os.path.basename(dirval)
    else:
        shortname = args.shortname[0]

    test = args.test
    force = args.force

    if args.merge:
        merge(dirval)



    if args.track:
        writeTrackNumbers(dirval, test, force)
        return


    if args.show:
        showID3s(dirval)
        return


    if args.check:
        cities = json.load(open("cities.json"))
        if args.artist:
            artist = args.artist[0]
        else:
            artist = shortname.title()
        check(dirval, shortname, artist, test, cities)
        return

        
    if args.inspect:
        inspect(dirval)
        return

        
    if args.fix:
        if args.artist == None:
            print "Need -artist"
            f()
        if args.comment:
            comment = args.comment[0]
        else:
            comment = ""
        artist = args.artist[0]
        fix(dirval, artist, comment)
        print "Done."
        return

    if args.move:
        analyze(dirval, shortname)
        print "Done."
        return


    if args.albumname:
        writeAlbumName(dirval, args.albumname[0])
        return
        

    if args.album:
        writeAlbum(dirval)
        return
        

    if args.artist:
        writeArtist(dirval, args.artist[0], force)
        return


if __name__ == "__main__":

    if False:
        txt = "glove2006-02-25d1t08.mp3"
        print "=======>  ",txt,'  \t',
         ret = findDateRaw(txt)
        if ret == None: 
            print "\tCould not find date"
        else: 
            print "\tDate ==>",ret
        print findTrkNo(txt),'\n'
        f()

    if False:
        trkname = "CC2010-08-23_CA-11_s1-10.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'
        f()

        trkname = "ABF_d1t3_Dazed.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "105edit.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "cd2song11.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "cd1song9.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "309 - Fade Away.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "U2 1985-03-05 d2 tr01.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "SCI2006-06-29D01T04.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'
        
        trkname = "sci2006-10-29set1t08.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'
        
        trkname = "05 Help.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "19 Slow Dancing.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "U2 Las Vegas Rehearsals d10t05 Discotheque.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "u2_3_15_81_t12.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        trkname = "Unknown Artist - Unknown Title - 06 - Track06.mp3"
        print trkname,'\t\t',findTrkNo(trkname),'\n'

        f()






    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', dest='dirval', nargs=1, help='Directory with mp3s.', required=True)
    parser.add_argument('-shortname',  dest='shortname',  nargs=1, help='Shortname for -enter and -fix directories.', required=False)
    parser.add_argument('-show',  action="store_true", default=False, help='Show ID3 files?.', required=False)
    parser.add_argument('-track',  action="store_true", default=False, help='Check files?.', required=False)
    parser.add_argument('-check',  action="store_true", default=False, help='Check files?.', required=False)
    parser.add_argument('-inspect',  action="store_true", default=False, help='Check files?.', required=False)
    parser.add_argument('-move',  action="store_true", default=False, help='Move files?.', required=False)
    parser.add_argument('-merge',  action="store_true", default=False, help='Merge mp3s.', required=False)
    parser.add_argument('-fix',  action="store_true", default=False, help='Fix metadata.', required=False)
    parser.add_argument('-force',  action="store_true", default=False, help='Force write.', required=False)
    parser.add_argument('-test',  action="store_true", default=False, help='Only test.', required=False)
    parser.add_argument('-album',  action="store_true", default=False, help='Write Album.', required=False)
    parser.add_argument('-artist',  dest='artist',  nargs=1, help='Artist name.', required=False)
    parser.add_argument('-albumname',  dest='albumname',  nargs=1, help='Album name.', required=False)
    parser.add_argument('-comment',  dest='comment',  nargs=1, default = "", help='Artist name.', required=False)
    args = parser.parse_args()
    main(args)
