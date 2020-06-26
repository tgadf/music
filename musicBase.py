import string
from fsUtils import isDir, setDir
from listUtils import getFlatList
from timeUtils import clock, elapsed
from unicodedata import normalize
from searchUtils import findDirs, findAll, findNearest
from fileUtils import getDirBasics, getBaseFilename
from glob import glob
from os.path import join
from os import walk
from pandas import DataFrame, Series
from collections import Counter
from primeDirectory import primeDirectory



###############################################################################################################################
#
# My Artist Album Type
#
###############################################################################################################################
class myArtistAlbumType:
    def __init__(self, debug=False):
        self.albums = {}
        self.fcounts = None
        
    def getNum(self):
        num = sum(len(x) for x in self.albums.values())
        return num
    
    def setFileCounts(self, fcounts):
        self.fcounts = fcounts

    def setAlbums(self, albums):
        self.albums = albums
        
    def getAlbums(self):
        return self.albums
    
    def getNumAlbums(self):
        return self.getNum()
    
    def getNumFiles(self):
        if self.fcounts is None:
            return 0
        else:
            num = sum([x for x in self.fcounts.values() if x is not None])
            return num
    

    
    
###############################################################################################################################
#
# My Artist Albums
#
###############################################################################################################################
class myArtistAlbumData:
    def __init__(self, debug=False):
        self.albums = []
        self.counts = None
        
class myArtistAlbums(primeDirectory):
    def __init__(self, artistName, count=False, debug=False):
        super().__init__()
        self.artistName       = artistName        
        self.count            = count
        self.debug            = debug
        
        self.directoryMapping = {}
        self.directoryMapping["BoxSet"]  = ["BoxSet"]
        self.directoryMapping["Bootleg"] = ["Bootleg"]
        self.directoryMapping["Mix"]     = ["Mix"]
        self.directoryMapping["Media"]   = ["Media"]
        self.directoryMapping["Unknown"] = ['Unknown']
        self.directoryMapping["Random"]  = ['Random']
        self.directoryMapping["Todo"]    = ["Todo", "Album", "Title"]
        self.directoryMapping["Match"]   = ["Match"]
        
        ## This one is special
        self.directoryMapping["UnMatched"] = []
        
        self.albumTypeData = {}
        self.myMusicDirs   = []
        for albumType in self.directoryMapping.keys():
            self.albumTypeData[albumType] = myArtistAlbumType()
            self.myMusicDirs += self.directoryMapping[albumType]
            
            

    ################################################################################################
    # Produce Dictionary of Results
    ###############################################################################################
    def getDict(self):
        if self.count is True:
            retval = {k: [v.getNumAlbums(),v.getNumFiles()] for k,v in self.albumTypeData.items()}
        else:
            retval = {k: v.getNumAlbums() for k,v in self.albumTypeData.items()}            
        return retval
                
        
    ################################################################################################
    # Album Setter
    ################################################################################################
    def setAlbumData(self, albumType, albumTypeResults):
        if self.albumTypeData.get(albumType) is None:
            raise ValueError("Trying to set albumType [{0}], but it's not allowed!".format(dirval))
        albums = {dirval: dirResults.albums for dirval,dirResults in albumTypeResults.items()}
        self.albumTypeData[albumType].setAlbums(albums)
        if self.count is True:
            counts = {dirval: dirResults.counts for dirval,dirResults in albumTypeResults.items()}
            self.albumTypeData[albumType].setFileCounts(counts)
        else:
            self.albumTypeData[albumType].setFileCounts(None)
            
        
    def updateFileCount(self, musicdata, dname):
        if self.count is True:
            for root, dirs, files in walk(dname):
                if musicdata.counts is None:
                    musicdata.counts = 0
                musicdata.counts += len(files)
            
            
    ################################################################################################
    # Unmatched
    ################################################################################################
    def getMyUnmatchedAlbums(self, dirval, returnNames=False):    
        musicdata = myArtistAlbumData()
        musicdata.albums = [x for x in findDirs(dirval) if getDirBasics(x)[-1] not in self.myMusicDirs]
        for dname in musicdata.albums:
            self.updateFileCount(musicdata, dname)
        if returnNames is True:
            musicdata.albums = [getDirBasics(x)[-1] for x in musicdata.albums]
        return musicdata


    ################################################################################################
    # Matched
    ################################################################################################
    def getMyMatchedMusicAlbums(self, dirval):
        musicdata = myArtistAlbumData()
        for matchDir in self.directoryMapping["Match"]:
            matchval = join(dirval, matchDir, "*")
            for dname in glob(matchval):
                musicdata.albums += [getDirBasics(x)[-1].split(" :: ")[0] for x in findDirs(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Todo
    ################################################################################################
    def getMyTodoMusicAlbums(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Todo"]:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                musicdata.albums += [getDirBasics(x)[-1] for x in findDirs(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Unknown
    ################################################################################################
    def getMyUnknownMusicAlbums(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Unknown"]:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                musicdata.albums += [getDirBasics(x)[-1] for x in findDirs(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Random
    ################################################################################################
    def getMyRandomMusic(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Random"]:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                musicdata.albums += [getBaseFilename(x) for x in findAll(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Mix
    ################################################################################################
    def getMyMixMusic(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Mix"]:
            mixval = join(dirval, dval)
            for dname in glob(mixval):
                musicdata.albums += [getBaseFilename(x) for x in findAll(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Media
    ################################################################################################
    def getMyMediaMusic(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Media"]:
            mediaval = join(dirval, dval)
            for dname in glob(mediaval):
                musicdata.albums += [getBaseFilename(x) for x in findAll(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # Bootleg
    ################################################################################################
    def getMyBootlegMusic(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["Bootleg"]:
            bootlegval = join(dirval, dval)
            for dname in glob(bootlegval):
                musicdata.albums += [getBaseFilename(x) for x in findAll(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata


    ################################################################################################
    # BotXset
    ################################################################################################
    def getMyBoxSetMusic(self, dirval):
        musicdata = myArtistAlbumData()
        for dval in self.directoryMapping["BoxSet"]:
            boxsetval = join(dirval, dval)
            for dname in glob(boxsetval):
                musicdata.albums += [getBaseFilename(x) for x in findAll(dname)]
                self.updateFileCount(musicdata, dname)
        return musicdata
    
        

    
###############################################################################################################################
#
# My Music Base
#
###############################################################################################################################
class myMusicBase(primeDirectory):
    def __init__(self, debug=False):
        super().__init__()
        self.debug     = debug
            
        self.musicDirs = ["/Volumes/Piggy/Music/Matched"]
        self.musicDirs = [x for x in self.musicDirs if isDir(x)]
        print("My Music Base: {0}".format(self.musicDirs))
        
        ### My Music Directory Names
        self.artistFileCount   = {}
        self.artistAlbums      = {}
        self.artistPrimeDirMap = {}

    
    def getMatchedDirs(self):
        return self.musicDirs

    def getVolumeName(self, baseDir):
        vals = getDirBasics(baseDir)
        return vals[2] 


    
    ###################################################################################################
    # Return Data
    ###################################################################################################
    def getArtists(self):
        return list(self.artistAlbums.keys())
        
    def getArtistAlbums(self):
        return self.artistAlbums
    
    def getUnMatchedAlbumsByArtist(self, artistName):
        return self.getArtistAlbumTypesByArtist(artistName, "UnMatched")
    
    def getArtistAlbumTypesByArtist(self, artistName, albumType):
        artistData = self.getArtistAlbumsByArtist(artistName)
        if artistData.get(albumType):
            albums = artistData[albumType].albums.values()
            return getFlatList(albums)
        return None

    def getArtistAlbumsByArtist(self, artistName):
        artistData = self.artistAlbums.get(artistName)
        if artistData is not None:
            return artistData.albumTypeData
        return {}

    def getDictByArtist(self, artistName):
        mma = self.getArtistAlbumsByArtist(artistName)
        if mma is not None:
            return mma.getDict()
        return {}
    
    def getDataFrame(self):
        tmp    = {artistName: artistData.getDict() for artistName, artistData in self.getArtistAlbums().items()}
        df     = DataFrame(tmp).T
        df["Files"] = self.artistFileCount.values()
        dirval = Series(df.index).apply(self.getPrimeDirectory)
        dirval.index = df.index
        df["Prime"] = dirval
        return df
    
    def getDF(self):
        return self.getDataFrame()
    
    
    
    
    ###################################################################################################
    # Loop over Prime Directories
    ###################################################################################################
    def getMatchedPrimeAlbumDirs(self, primeDir, matchedDirs):
        dirvals     = getFlatList([findDirs(setDir(matchedDir, primeDir)) for matchedDir in matchedDirs])
        artistNames = [normalize('NFC', getDirBasics(dirval)[-1]) for dirval in dirvals]
        return list(zip(artistNames, dirvals))
    
    
    def getArtistPrimeDirMap(self, primeDir, force=True):
        if force is False:
            return self.artistPrimeDirMap
        
        matchedPrimeAlbumDirs = self.getMatchedPrimeAlbumDirs(primeDir, self.getMatchedDirs())
        self.artistPrimeDirMap = {}
        for (artistName,dirval) in matchedPrimeAlbumDirs:
            if self.artistPrimeDirMap.get(artistName) is None:
                self.artistPrimeDirMap[artistName] = []
            self.artistPrimeDirMap[artistName].append(dirval)
        self.artistPrimeDirMap = {k: self.artistPrimeDirMap[k] for k in sorted(self.artistPrimeDirMap)}
        return self.artistPrimeDirMap
    
    
    ###################################################################################################
    # Find Artist Albums and Organize
    ###################################################################################################    
    def findArtistAlbums(self, count=False):
        start, cmt = clock("Finding All Artist Albums")
        
        self.artistAlbums    = {}
        self.artistFileCount = {}
        for primeDir in self.getPrimeDirectories():
            if self.debug:
                startPrime, cmtPrime = clock("=====> {0}".format(primeDir))
            artistPrimeDirItems = self.getArtistPrimeDirMap(primeDir)
            for artistName, artistPrimeDirs in artistPrimeDirItems.items():
                maa = myArtistAlbums(artistName=artistName, count=count)


                ######################################################################
                #### Get My Matched Albums
                ######################################################################
                albums = {dirval: maa.getMyMatchedMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Match", albums)


                ######################################################################
                #### Get My UnMatched Albums
                ######################################################################
                albums = {dirval: maa.getMyUnmatchedAlbums(dirval, returnNames=True) for dirval in artistPrimeDirs}
                maa.setAlbumData("UnMatched", albums)


                ######################################################################
                #### Get My Unknown Albums
                ######################################################################
                albums = {dirval: maa.getMyUnknownMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Unknown", albums)


                ######################################################################
                #### Get My Todo Albums
                ######################################################################
                albums = {dirval: maa.getMyTodoMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Todo", albums)


                ######################################################################
                #### Get My Random Music
                ######################################################################
                albums = {dirval: maa.getMyRandomMusic(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Random", albums)


                ######################################################################
                #### Get My Mix Music
                ######################################################################
                albums = {dirval: maa.getMyMixMusic(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Mix", albums)


                ######################################################################
                #### Get My Media Music
                ######################################################################
                albums = {dirval: maa.getMyMediaMusic(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Media", albums)


                ######################################################################
                #### Get My Bootleg Music
                ######################################################################
                albums = {dirval: maa.getMyBootlegMusic(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("Bootleg", albums)


                ######################################################################
                #### Get My BoxSet Music
                ######################################################################
                albums = {dirval: maa.getMyBoxSetMusic(dirval) for dirval in artistPrimeDirs}
                maa.setAlbumData("BoxSet", albums)
                
                
                ######################################################################
                #### Save Artist Albums
                ######################################################################
                self.artistAlbums[artistName]    = maa
                self.artistFileCount[artistName] = None
                if count is True:
                    self.artistFileCount[artistName] = 0
                    for artistPrimeDir in artistPrimeDirs:
                        for root, dirs, files in walk(artistPrimeDir):
                            self.artistFileCount[artistName] += len(files)
                
            #break # (call this if you only want to do the A directories 
            if self.debug:
                elapsed(startPrime, cmtPrime)
                print("")
                
        elapsed(start, cmt)