import string
from fsUtils import isDir, setDir
from listUtils import getFlatList
from timeUtils import clock, elapsed
from unicodedata import normalize
from searchUtils import findDirs, findAll, findNearest
from fileUtils import getDirBasics, getBaseFilename
from glob import glob
from os.path import join
from pandas import DataFrame, Series
from collections import Counter



class myArtistAlbums:
    def __init__(self, artistName, primeDirs, debug=False):
        self.debug=debug
        self.artistName = artistName
        
        self.primeDirs = primeDirs
        
        self.dirvals   = {}
        
        self.unmatched = {}
        self.matched   = {}
        self.todo      = {}
        self.unknown   = {}
        self.random    = {}
        
        
        
        
    def getNum(self, albumType):
        num = sum(len(x) for x in albumType.values())
        return num
    

    def getNumVolumes(self):
        oaa = self.getOrganizedAlbums()
        volumes = {volume: sum([len(y) for y in x.values()]) for volume, x in oaa.items()}
        return volumes

    
    def setUnmatched(self, unmatched):
        self.unmatched = unmatched
    def getUnmatched(self):
        return self.unmatched
    def getNumUnmatched(self):
        return self.getNum(self.unmatched)
    

    def setMatched(self, matched):
        self.matched = matched
    def getMatched(self):
        return self.matched
    def getNumMatched(self):
        return self.getNum(self.matched)
    

    def setTodo(self, todo):
        self.todo = todo
    def getTodo(self):
        return self.todo
    def getNumTodo(self):
        return self.getNum(self.todo)


    def setUnknown(self, unknown):
        self.unknown = unknown
    def getUnknown(self):
        return self.unknown
    def getNumUnknown(self):
        return self.getNum(self.unknown)


    def setRandom(self, random):
        self.random = random
    def getRandom(self):
        return self.random
    def getNumRandom(self):
        return self.getNum(self.random)

        
    def organize(self):
        self.dirvals = {}
        for dirval,albums in self.unmatched.items():
            if self.dirvals.get(dirval) is None:
                self.dirvals[dirval] = {}
            self.dirvals[dirval]["Unmatched"] = albums
        
        for dirval,albums in self.matched.items():
            if self.dirvals.get(dirval) is None:
                self.dirvals[dirval] = {}
            self.dirvals[dirval]["Matched"] = albums
        
        for dirval,albums in self.todo.items():
            if self.dirvals.get(dirval) is None:
                self.dirvals[dirval] = {}
            self.dirvals[dirval]["Todo"] = albums
        
        for dirval,albums in self.unknown.items():
            if self.dirvals.get(dirval) is None:
                self.dirvals[dirval] = {}
            self.dirvals[dirval]["Unknown"] = albums
        
        for dirval,albums in self.random.items():
            if self.dirvals.get(dirval) is None:
                self.dirvals[dirval] = {}
            self.dirvals[dirval]["Random"] = albums
            
            
    def getOrganizedAlbums(self):
        self.organize()
        return self.dirvals
        

    def getDict(self):
        retval = {"Unmatched": self.getNumUnmatched(),
                  "Matched":   self.getNumMatched(),
                  "Todo":      self.getNumTodo(),
                  "Unknown":   self.getNumUnknown(),
                  "Random":    self.getNumRandom()}
        return retval
    
        
    def info(self):
        print("Artist Albums For {0}".format(self.artistName))
        print("  Unmatched: {0}".format(self.unmatched))
        print("  Matched:   {0}".format(self.matched))
        print("  Todo:      {0}".format(self.todo))
        print("  Unknown:   {0}".format(self.unknown))
        print("  Random:    {0}".format(self.random))

        

class myMusicBase:
    def __init__(self, debug=False):
        self.debug     = debug
        #self.musicDirs = ["/Volumes/Music/Matched", "/Volumes/Biggy/Matched"]
        self.musicDirs = ["/Volumes/Piggy/Music/Matched"]
        self.musicDirs = [x for x in self.musicDirs if isDir(x)]
        
        
        ### My Music Directory Names
        self.unknownDirs = ['Unknown', 'Bootleg', 'Mix', 'BoxSet', 'Media']
        self.randomDirs  = ['Random']
        self.todoDirs    = ["Todo", "Album", "Title"]
        self.matchDir    = "Match"
        self.myMusicDirs = list(set(self.unknownDirs + self.randomDirs + self.todoDirs + [self.matchDir]))

        self.artistAlbums = {}
        self.artistPrimeDirMap = {}
        
        self.matchedDirs = self.getMatchedDirs()
        print("My Music Base: {0}".format(self.musicDirs))

    
    def getMatchedDirs(self):
        return self.musicDirs
    

    def getPrimeDirectory(self, artistName):
        start = artistName[0]

        if start in string.ascii_uppercase:
            if artistName.startswith("The "):
                return "The"
            return start
        if start in string.ascii_lowercase:
            return "Xtra"
        elif start in string.digits:
            return "Num"
        else:
            return "Xtra"
            raise ValueError("Could not determine Prime Directory for Artist {0}".format(artistName))

            
    def getPrimeDirectories(self):    
        retvals  = [x for x in string.ascii_uppercase]
        retvals += ["Num", "Xtra", "The"]
        retvals  = sorted(retvals)
        return retvals


    def getVolumeName(self, baseDir):
        vals = getDirBasics(baseDir)
        return vals[2]
    
    

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
    # My Music Directories
    ###################################################################################################    
    def getMyUnmatchedAlbums(self, dirval, returnNames=False):    
        myMusicAlbums = [x for x in findDirs(dirval) if getDirBasics(x)[-1] not in self.myMusicDirs]
        if returnNames is True:
            myMusicUnmatched = [getDirBasics(x)[-1] for x in myMusicAlbums]
        return myMusicUnmatched


    def getMyMatchedMusicAlbums(self, dirval, byKey=False):  
        matchval = join(dirval, self.matchDir, "*")
        matchedAlbums = []
        for dname in glob(matchval):
            matchedAlbums += [getDirBasics(x)[-1].split(" :: ")[0] for x in findDirs(dname)]
        return matchedAlbums


    def getMyTodoMusicAlbums(self, dirval):
        todoAlbums = []
        for dval in self.todoDirs:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                todoAlbums += [getDirBasics(x)[-1] for x in findDirs(dname)]
        return todoAlbums


    def getMyUnknownMusicAlbums(self, dirval):
        todoAlbums = []
        for dval in self.unknownDirs:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                todoAlbums += [getDirBasics(x)[-1] for x in findDirs(dname)]
        return todoAlbums


    def getMyRandomMusic(self, dirval):
        randomMusic = []
        for dval in self.randomDirs:
            todoval = join(dirval, dval)
            for dname in glob(todoval):
                randomMusic += [getBaseFilename(x) for x in findAll(dname)]
        return randomMusic


    
    def getArtists(self):
        return list(self.artistAlbums.keys())
    
    
    def getArtistAlbums(self):
        return self.artistAlbums


    def getArtistAlbumsByArtist(self, artistName):
        return self.artistAlbums.get(artistName)
        

    def getDictByArtist(self, artistName):
        mma = self.getArtistAlbumsByArtist(artistName)
        if mma is not None:
            return mma.getDict()
        return {}
    
    
    def getDataFrame(self):
        tmp    = {artistName: artistData.getDict() for artistName, artistData in self.getArtistAlbums().items()}
        df     = DataFrame(tmp).T
        dirval = Series(df.index).apply(self.getPrimeDirectory)
        dirval.index = df.index
        df["Prime"] = dirval
        return df
    def getDF(self):
        return self.getDataFrame()


    
    def findArtistAlbums(self):
        start, cmt = clock("Finding All Artist Albums")
        
        self.artistAlbums = {}
        for primeDir in self.getPrimeDirectories():
            if self.debug:
                startPrime, cmtPrime = clock("=====> {0}".format(primeDir))
            artistPrimeDirItems = self.getArtistPrimeDirMap(primeDir)
            for artistName, artistPrimeDirs in artistPrimeDirItems.items():
                maa = myArtistAlbums(artistName, artistPrimeDirs)

                ######################################################################
                #### Get My Music Albums
                ######################################################################
                myUnmatchedAlbums = {dirval: self.getMyUnmatchedAlbums(dirval, returnNames=True) for dirval in artistPrimeDirs}
                maa.setUnmatched(myUnmatchedAlbums)


                ######################################################################
                #### Get My Matched Albums
                ######################################################################
                myMatchedAlbums = {dirval: self.getMyMatchedMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setMatched(myMatchedAlbums)


                ######################################################################
                #### Get My Unknown Albums
                ######################################################################
                myUnknownAlbums = {dirval: self.getMyUnknownMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setUnknown(myUnknownAlbums)


                ######################################################################
                #### Get My Todo Albums
                ######################################################################
                myTodoAlbums = {dirval: self.getMyTodoMusicAlbums(dirval) for dirval in artistPrimeDirs}
                maa.setTodo(myTodoAlbums)


                ######################################################################
                #### Get My Random Music
                ######################################################################
                myRandomMusic = {dirval: self.getMyRandomMusic(dirval) for dirval in artistPrimeDirs}
                maa.setRandom(myRandomMusic)
                
                
                self.artistAlbums[artistName] = maa
                
            if self.debug:
                elapsed(startPrime, cmtPrime)
                print("")
                
        elapsed(start, cmt)
        
        
    def show(self):
        minMyAlbums   = 2
        minTodoAlbums = 5
        downloadCut   = 5

        ranks = {"Matches": Counter(), "Albums": Counter()}

        print("{0: <35}| {1: <10}| {2: <10}| {3: <10}| {4: <10}| {5: <10}| {6: <10}| {7: <12}| {8: <12}|".format("Artist", "Volumes", "Matches", "# Albums", "Todo", "Unknown", "Random", "No Match", "Many Albums"))
        print("{0: <35}| {1: <10}| {2: <10}| {3: <10}| {4: <10}| {5: <10}| {6: <10}| {7: <12}| {8: <12}|".format("------", "-------", "-------", "--------", "----", "-------", "------", "--------", "-----------"))

        for artistName, artistData in self.mmb.getArtistAlbums().items():
            
            ### Artist Name
            print("{0: <35}".format(artistName), end="")

            ### Volumes
            oaa     = artistData.getOrganizedAlbums()
            volumes = {volume: sum([len(y) for y in x.values()]) for volume, x in oaa.items()}
            print("| {0: <10}".format(self.printAlbums(volumes.values())), end="")

            ### Matched Albums
            numMatched = artistData.getNumMatched()
            print("| {0: <10}".format(numMatched), end="")

            ### Unmatched Albums
            numUnmatched = artistData.getNumUnmatched()
            print("| {0: <10}".format(numUnmatched), end="")

            ### Todo Albums
            numTodo = artistData.getNumTodo()
            print("| {0: <10}".format(numTodo), end="")

            ### Unknown Albums
            numUnknown = artistData.getNumUnknown()
            print("| {0: <10}".format(numUnknown), end="")

            ### Random Albums
            numRandom = artistData.getNumRandom()
            print("| {0: <10}".format(numRandom), end="")

            
            ### Check For No Match
            noMatchText = "{0}..".format(artistName[:9])
            if numMatched > 0:
                noMatchText = ""
            print("| {0: <12}".format(noMatchText), end="")

            
            ### Check For Many Albums
            manyAlbumsText = "{0}..".format(artistName[:9])
            if numUnmatched < 3:
                manyAlbumsText = ""
            print("| {0: <12}".format(manyAlbumsText), end="")

            ### Return
            print("|")