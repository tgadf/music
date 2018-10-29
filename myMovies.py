# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:42:05 2017

@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')
    
from fileio import save, get, setFile, getFileBasics, setDir
from search import findNearest, findMatchingWord, findExt, findSubPatternExt, findAll
from glob import glob
from os.path import join, getsize, exists
from re import search
from shutil import move, copy
from movies import getMovieDir, combineMovies


###############################################################################
#
#   1) createLocalMoviesList()
#   2) mergeKnownMovies()
#   3) mergeMatches() / mergeMatchesDB()
#
###############################################################################
def getLocalMovies():
    try:
        drives = ["Blue", "Download", "Music", "Save", "Seagate"]
        dirs   = [setDir("/Volumes/", x) for x in drives]
    except:
        print "Could not find movie volumes."
        return []
    movies = []
    for dirname in dirs:
        dirname = setDir(dirname, "Movies")
        movies += findAll(dirname)
    return movies



def getMyMoviesFile():
    outdir = getMovieDir()
    savename = setFile(outdir, "myMovies.json")
    return savename



def loadLocalMoviesList():
    savename = getMyMoviesFile()
    return get(savename)



def createLocalMoviesList():
    db = {}
    movies = getLocalMovies()
    for movie in movies:
        dname,bname,ext = getFileBasics(movie)
        if db.get(bname):
            print "Duplicate movie!"
            print int(getsize(movie)/1e6),'\t',movie
            print int(getsize(db[bname])/1e6),'\t',db[bname]
            if getsize(movie) < getsize(db[bname]):
                print "remove(\""+movie+"\")"
            elif getsize(movie) > getsize(db[bname]):
                print "remove(\""+db[bname]+"\")"
            else:
                if movie.find("Backup") != -1:
                    print "remove(\""+movie+"\")"
                elif db[bname].find("Backup") != -1:
                    print "remove(\""+db[bname]+"\")"
                elif movie.find("Seagate") != -1:
                    print "remove(\""+movie+"\")"
                elif db[bname].find("Seagate") != -1:
                    print "remove(\""+db[bname]+"\")"
            print ""
        db[bname] = movie
        
    savename = getMyMoviesFile()
    print "Saving",len(db),"my movies to",savename
    save(savename, db)
    
    
    

###############################################################################
#
#   Merge Movies
#
###############################################################################
def createOfficialMovies():
    combineMovies()

def mergeKnownMovies(matchNum = 0.95):
    outdir   = getMovieDir()
    savename = setFile(outdir, "officialMovies.yaml")
    movieDB  = get(savename)
    print "Found",len(movieDB),"years of official movies in",savename
    
    myMovies = loadLocalMoviesList()
    print "Found",len(myMovies),"my movies in", savename

    savename = setFile(outdir, "myMovies-known.json")
    try:
        knownDB  = get(savename)
    except:
        knownDB  = {}
    print "Found",len(knownDB),"my known movies in", savename
    for movie in knownDB.keys():
        del myMovies[movie]
        

    nNewMatches  = 0
    nOldMatches  = 0
    nNoMatches   = 0
    newMatchesDB = {}
    for year,ydata in movieDB.iteritems():
        print "====>",year
        for mtype,mdata in ydata.iteritems():
            print "    ",mtype
            for movie,mmatch in mdata.iteritems():
                if mmatch:
                    nOldMatches += 1
                    continue
                if mmatch == None:
                    testmovie = movie + u" ["+year+"]"
                    nearest   = findNearest(testmovie, myMovies.keys(), 1, matchNum)                    
                    if len(nearest) == 0:
                        for dyear in [1, -1, 2, -2]:
                            testmovie = movie + u" ["+str(int(year)+dyear)+"]"
                            dval = (1 - matchNum)/2
                            nearest = findNearest(testmovie, myMovies.keys(), 1, matchNum + dval)
                            if len(nearest) > 0:
                                break
                    matches  = nearest
                    if len(matches) > 0:
                        #print "\n====>",year
                        #print "    ",mtype
                        print "        ",movie,"  :  ",matches[0]
                        if newMatchesDB.get(year) == None:
                            newMatchesDB[year] = {}
                        if newMatchesDB[year].get(mtype) == None:
                            newMatchesDB[year][mtype] = {}
                        newMatchesDB[year][mtype][movie] = matches[0]
                        nNewMatches += 1
                    else:
                        nNoMatches  += 1


    print "Found",nNewMatches,"new (near) matches."
    print "Found",nOldMatches,"old (exact) matches."
    print "Found",nNoMatches,"no matches."
    savename = setFile(outdir, "officialMovies-new.yaml")
    save(savename, newMatchesDB)
    print "Saved",len(newMatchesDB),"official yearly movies <-> matches to",savename
    

def mergeMatchesDB():
    outdir   = getMovieDir()
    savename = setFile(outdir, "officialMovies.yaml")
    movieDB = get(savename)
    print "Found",len(movieDB),"years of official movies in",savename
    
    savename = setFile(outdir, "myMovies-known.json")
    knownDB = get(savename)
    print "Found",len(knownDB),"my known movies in", savename
    
    nNew = 0
    for year,ydata in movieDB.iteritems():
        if movieDB.get(year) == None:
            print "Error with movieDB[",year,"]"
            raise()
        for mtype,mdata in ydata.iteritems():
            if movieDB[year].get(mtype) == None:
                print "Error with movieDB[",year,"][",mtype,"]"
                raise()
            for movie,mmatch in mdata.iteritems():
                if mmatch == None:
                    continue
                if knownDB.get(mmatch) == None:
                    knownDB[mmatch] = [year, mtype, movie]
                    nNew += 1

       
    savename = setFile(outdir, "officialMovies.yaml")
    print "Found",nNew,"new matches in",savename
    savename = setFile(outdir, "myMovies-known.json")
    print "Saving",len(knownDB),"known movies to", savename
    save(savename, knownDB)
    refillKnownMovies()



def refillKnownMovies():
    outdir   = getMovieDir()
    savename = setFile(outdir, "officialMovies.yaml")
    movieDB  = get(savename)
    print "Found",len(movieDB),"years of official movies in",savename

    savename = setFile(outdir, "myMovies-known.json")
    knownDB  = get(savename)
    print "Found",len(knownDB),"my known movies in", savename

    for movie,location in knownDB.iteritems():
        year  = location[0]
        mtype = location[1]
        name  = location[2]
        movieDB[year][mtype][name] = movie
        
    savename = setFile(outdir, "officialMovies.yaml")
    print "Saving",len(knownDB),"years of my movie matches to",savename
    save(savename, movieDB)
    
    
def mergeMatches():
    outdir   = getMovieDir()
    src = setFile(outdir, "officialMovies.yaml")
    dst = setFile(outdir, "officialMovies-new.yaml")
    tmp = setFile(outdir, "officialMovies.tmp.yaml")

    savename     = setFile(outdir, "officialMovies.yaml")
    movieDB      = get(savename)
    newMatchesDB = get(dst)

    savename = setFile(outdir, "myMovies-known.json")
    try:
        knownDB  = get(savename)
    except:
        knownDB  = {}

    print src,' ===> ',tmp
    copy(src, tmp)

    nNew = 0
    for year,ydata in newMatchesDB.iteritems():
        if movieDB.get(year) == None:
            raise ValueError("Error with movieDB[",year,"]")
        for mtype,mdata in ydata.iteritems():
            if movieDB[year].get(mtype) == None:
                raise ValueError("Error with movieDB[",year,"][",mtype,"]")
            for movie,mmatch in mdata.iteritems():
                if mmatch == None:
                    continue
                mmovies = movieDB[year][mtype].keys()
                if movie not in mmovies:
                    print "Error with movieDB[",year,"][",mtype,"][",movie,"]"
                    for k,v in movieDB[year][mtype].iteritems():
                        print k,'\t',v
                    raise()
                movieDB[year][mtype][movie] = mmatch
                knownDB[mmatch] = [year, mtype, movie]
                nNew += 1

       
    savename = src
    print "Found",nNew,"new matched movies."
    print "Saving",len(movieDB),"years of official movies in",savename
    save(savename, movieDB)
    
    savename = setFile(outdir, "myMovies-known.json")
    print "Saving",len(knownDB),"known movies to", savename
    save(savename, knownDB)

    mergeMatchesDB()
    
    
    
    
###############################################################################
#
#   New Movie Stuff
#
###############################################################################
def getNewMoviesDir():
    return "/Volumes/Download/MoviesLocal"

def getCleanedMoviesDir():
    return "/Volumes/Download/MoviesFinished"

def cleanMovie(movie):
    rms  = ["AG]", "x264", "YIFY", "VPPV", "6CH", "x264-[YTS", "ShAaNiG", "XviD"]
    rms += ["1080p", "HDRip", "GoenWae", "HDTV", "BluRay", "Brrip", "AC3-EVO"]
    rms += ["720p", "DTS-JYK", "[YTS", "x264", "-[YTS", "BRRip", "H264"]
    rms += ["WEBRip", "RARBG", "Ozlem", "anoXmous_", "AAC", "[MnM RG]"]
    rms += ["EXTENDED WEB", "DL AC3 JYK", "AC3", "Bluray", "JYK"]
    rms += ["DvdRip HighCode", "ReRip   CODY", "DVDRip Zoo", "CODY", "SuperNova"]
    rms += ["REMASTERED", "XViD", "ETRG", "DvDrip[Eng]", "WEB DL"]
    rms += ["XVID", "HQ", "Hive", "CM8", "DTS", "DVDRip", "UNRATED"]
    rms += ["WEB-DL", "[3D]", "[HSBS]", " [1080p]", " [720p]", "BrRip"]
    rms += ["BRRiP-KiNGDOM"]

    movie = movie.replace(".", " ")
    for rm in rms:
        movie = movie.replace(" "+rm, "")
    for rm in rms:
        movie = movie.replace("-"+rm, "")
    
    return movie



def findNewMovies():
    indir  = getNewMoviesDir()
    outdir = getMovieDir()
    exts  = [".mp4", ".mkv", ".avi"]
    clean = []
    movies  = []
    for ext in exts:
        movies += findExt(indir, ext=ext)
        movies += findSubPatternExt(indir, "*", pattern="*", ext=ext)
        #movies += glob(join(indir, "*"+ext))
        #movies += glob(join(indir, "*", "*"+ext))    
    for movie in movies:
        if getsize(movie) < 3e8: continue
        dname,bname,ext = getFileBasics(movie)
        if ext in exts:
            print movie
            print bname
            newbname = cleanMovie(bname)
            print newbname
            clean.append([movie, dname, ext, {bname: newbname}])

    savename = setFile(outdir, "renames.yaml")
    print "Saving",len(clean),"renames to",savename
    save(savename, clean)
    #renameMovies()


def renameMovies():
    outdir     = getCleanedMoviesDir()
    indir      = getMovieDir()

    renameFile = setFile(indir, "renames.yaml")
    renames    = get(renameFile)
    for rename in renames:
        src      = rename[0]
        ext      = rename[2]
        fix      = rename[3].values()[0]

        if not exists(src):
            continue
        srcname  = src
        dstname  = setFile(outdir, fix+ext)
        if srcname != dstname:
            print ""
            print "Renaming",srcname
            print "      to",dstname
            print ""
            move(srcname, dstname)



def fixLocalMovies(movies = None):
    if movies == None:
        movies = getLocalMovies()
    elif isinstance(movies, str):
        if movies == "Local":
            movies = findAll(getCleanedMoviesDir())
        elif exists(movies):
            movies = glob(join(movies,"*"))
    if not isinstance(movies, list):
        print "Movies is not a list in fixLocalMovies()"
        return 
        
    for movie in movies:
        dname,bname,ext = getFileBasics(movie)
        val    = bname.split()[-1]
        try:
            rval = "["+str(int(val))+"]"
        except:
            rval = val
        rname  = bname.replace(val, rval)
        src = setFile(dname,bname+ext)
        dst = setFile(dname,rname+ext)
        if src != dst:
            print ""
            print "Moving: ",src
            print "    to : ",dst
            print ""
            move(src, dst)
    


###############################################################################
#
#   Database Stuff
#
###############################################################################
def processLocalMovies():
    movies = getLocalMovies()
    for movie in movies:
        retval = search("\[\d+\]", movie)
        if retval:
            continue
            print movie
        if not retval:
            print movie
    

    
        


def emptyKnownDB():
    outdir   = getMovieDir()
    savename = setFile(outdir, "myMovies-known.json")
    knownDB  = {}
    print "knownDB set to {}"
    save(savename, knownDB)
    


def searchMyMovies(movie = None):
    myMovies = loadLocalMoviesList()
    movies   = myMovies.keys()
    nearest1 = findMatchingWord(movie, movies)
    nearest2 = findNearest(movie, movies, 3, 0.7)
    matches  = list(set(nearest2+nearest1))
    print ""
    if len(matches) > 0:
        print "Possible Matches for",movie
        for mmovie in matches:
            print mmovie
    else:
        print "No matches for",movie
    print ""
    
    
    
def showMissingMovies():
    outdir   = getMovieDir()
    savename = setFile(outdir, "officialMovies.yaml")
    movieDB  = get(savename)
    print "Found",len(movieDB),"years of official movies in",savename
    for year,ydata in movieDB.iteritems():
        print "\n====>",year
        for mtype,mdata in ydata.iteritems():
            print "    ",mtype
            for movie,mmatch in mdata.iteritems():
                if mmatch == None:
                    print "        ",movie
    