from timeUtils import clock, elapsed
from musicBase import myMusicBase
from ioUtils import saveFile

class myMatchedMusic:
    def __init__(self, mdb, debug=False):
        self.debug = debug
        self.mdb   = mdb
        self.mmb   = myMusicBase()
        
        self.unknownArtists = {}
        self.artistAlbums   = {}
        
        self.matchedAlbums  = {}
        
        
    def setMusicBase(self, mmb):
        self.mmb = mmb
        
        
    def getAlbumStatus(self, force=False):
        self.artistAlbums = self.mmb.getArtistAlbums(force=force)
        

    def getArtistStatus(self):
        start, cmt = clock("Matching All Music Artists")

        ######################################################################
        #### Loop Over My Artists and Paths
        ######################################################################
        for primeDir in self.mmb.getPrimeDirectories():
            for artistName, artistPrimeDirs in self.mmb.getArtistPrimeDirMap(primeDir).items():
                if self.debug:
                    print("{0: <50}{1}".format(artistName,artistPrimeDirs))


                ######################################################################
                #### Get Database IDs
                ######################################################################
                isKnown = self.mdb.isKnown(artistName)
                if isKnown is False:
                    self.unknownArtists[artistName] = artistPrimeDirs
                    if self.debug:
                        print("\tUnknown (All)     --> {0}".format(artistName))
                        

        elapsed(start, cmt)
        print("Found {0} unknown artists".format(len(self.unknownArtists)))
        print("Found {0} total artists".format(len(self.artistAlbums)))

        
        
    def getUnknownArtists(self):
        return self.unknownArtists
    
    
    
    def getArtistNameMatchedDirs(self):
        self.artistMatchedDirs = {}
        for primeDir in self.mmb.getPrimeDirectories():
            self.artistMatchedDirs.update(self.mmb.getArtistPrimeDirMap(primeDir))
            

    def formatAlbum(self, albumName, albumType):
        if albumType == 3:
            retval = albumName.replace("(Single)", "")
            retval = retval.replace("(EP)", "")
            retval = retval.strip()
            return retval
        return albumName
    
    
    
    def matchMyMusicAlbumsByArtist(self, db, artistName, albumType=1, ratioCut=0.95, maxCut=0.1):

        matchedAlbums = {}
        

        ######################################################################
        #### Get Artist Album Data
        ######################################################################
        artistAlbumsData = self.mmb.getArtistAlbumsByArtist(artistName)
    
        if artistAlbumsData.getNumUnmatched() == 0:
            return matchedAlbums
            
            
        ######################################################################
        #### Loop Over Artist Name <-> Prime Map Items
        ######################################################################
        if self.mdb.isKnown(artistName) is True:
            myMusicData = self.mdb.getArtistData(artistName)
            try:
                artistID = myMusicData[db]["ID"]
            except:
                return matchedAlbums
        else:
            return matchedAlbums
            


        ######################################################################
        #### Get Database Albums
        ######################################################################
        artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistID)


        ######################################################################
        #### Loop over my albums
        ######################################################################
        for dirval, unMatchedAlbums in artistAlbumsData.getUnmatched().items():
            for myAlbumName in unMatchedAlbums:

                bestMatchVal = {"Ratio": ratioCut, "Dir": None, "Album": None}
                for mediaType, mediaTypeAlbums in artistDBAlbumsFromID.items():
                    if self.debug:
                        print("\tMy album: {0}".format(myAlbumName))
                    myFormattedAlbum = self.formatAlbum(myAlbumName, mediaType)

                    ma = matchAlbums(cutoff=ratioCut)
                    ma.match([myFormattedAlbum], mediaTypeAlbums)

                    if ma.maxval < ratioCut or ma.maxval > ratioCut+maxCut:
                        continue
                    if ma.maxval < bestMatchVal["Ratio"]:
                        continue

                    bestMatch = ma.getBestMatch(myFormattedAlbum)

                    bestMatchVal = {"Ratio": ma.maxval, "Dir": dirval, "Album": {"Name": bestMatch["Name"], "Code": bestMatch["Code"], "MediaType": mediaType}}
                    matchedAlbums[myAlbumName] = bestMatchVal
                    #print("{0: <30}{1: <15}{2: <30} --> {3}".format(artistName, db, myAlbumName, bestMatchVal["Album"]))
                    #bestMatchVal["Match"].show(debug=True)
                    
        return matchedAlbums

                
    
    def matchMyMusicAlbums(self, db, albumType=1, ratioCut=0.95, maxCut=0.1):
        self.matchedAlbums = {}

        start, cmt = clock("Checking for Albums Matches Against {0} DB".format(db))
        
        
        print("{0: <40}{1: <15}{2: <45} --> {3}".format("Artist", "Database", "Album Name", "Matched Album"))

        ######################################################################
        #### Get Map of Artists and Unmatched Albums
        ######################################################################
        artistNames = self.mmb.getArtists()
        #artistAlbums = self.mmb.getArtistAlbums()


        ######################################################################
        #### Loop Over Artist Name <-> Prime Map Items
        ######################################################################
        for artistName in artistNames:
            matchedAlbums = self.matchMyMusicAlbumsByArtist(db, artistName, albumType, ratioCut, maxCut)
            if len(matchedAlbums) > 0:
                if self.matchedAlbums.get(db) is None:
                    self.matchedAlbums[db] = {}
                self.matchedAlbums[db][artistName] = matchedAlbums
                for myAlbumName,bestMatchVal in matchedAlbums.items():
                    print("{0: <40}{1: <15}{2: <45} --> {3}".format(artistName, db, myAlbumName, bestMatchVal["Album"]))

            
        elapsed(start, cmt)

        saveFile(ifile="myMusicAlbumMatch.yaml", idata=self.matchedAlbums, debug=True)
        print("Found {0} music <-> discogs albums maps".format(len(self.matchedAlbums)))
        


    def getMatchedDirName(self, albumName, albumID, dbKey):
        if dbKey == "AllMusic":
            matchedDirName = " :: ".join([discConv(albumName), "[AM-{0}]".format(albumID)])
        elif dbKey == "MusicBrainz":
            matchedDirName = " :: ".join([discConv(albumName), "[MB-{0}]".format(albumID)])
        elif dbKey == "Discogs":
            matchedDirName = " :: ".join([discConv(albumName), "[DC-{0}]".format(albumID)])
        elif dbKey == "AceBootlegs":
            matchedDirName = " :: ".join([discConv(albumName), "[AB-{0}]".format(albumID)])
        elif dbKey == "RateYourMusic":
            matchedDirName = " :: ".join([discConv(albumName), "[RM-{0}]".format(albumID)])
        elif dbKey == "LastFM":
            matchedDirName = " :: ".join([discConv(albumName), "[LM-{0}]".format(albumID)])
        elif dbKey == "DatPiff":
            matchedDirName = " :: ".join([discConv(albumName), "[DP-{0}]".format(albumID)])
        elif dbKey == "RockCorner":
            matchedDirName = " :: ".join([discConv(albumName), "[RC-{0}]".format(albumID)])
        elif dbKey == "CDandLP":
            matchedDirName = " :: ".join([discConv(albumName), "[CL-{0}]".format(albumID)])
        elif dbKey == "MusicStack":
            matchedDirName = " :: ".join([discConv(albumName), "[MS-{0}]".format(albumID)])
        else:
            raise ValueError("dbKey {0} not recognized!".format(dbKey))
        
        return matchedDirName        


    def getUnMatchedDirName(self, matchedDirName, mediaDirType):
        vals = matchedDirName.split(" :: ")
        if len(vals) == 2:
            albumName  = vals[0]
            albumIDval = vals[1]
            try:
                albumID = int(albumIDval[(albumIDval.find("[")+3):albumIDval.rfind("]")])
            except:
                raise ValueError("Could not extract album ID from {0}".format(albumIDval))

            if sum([x in mediaDirType for x in ["Single", "EP"]]) > 0:
                albumName = "{0} (Single)".format(albumName)

            if sum([x in mediaDirType for x in ["Mix", "MixTape"]]) > 0:
                albumName = "{0} (MixTape)".format(albumName)

            return albumName
        else:
            raise ValueError("Could not extract album name from {0}".format(matchedDirName))
            
    
        
    def moveMyMatchedMusicAlbums(self, show=False):
        rename = True
        albumsToMove = getFile(ifile="myMusicAlbumMatch.yaml")
        print("Found {0} music <-> discogs albums maps".format(len(albumsToMove)))
        
        for db, dbValues in albumsToMove.items():
            if dbValues is None:
                continue
            for artistName, artistAlbums in dbValues.items():
                print("==>",artistName)
                for myAlbumName,albumVals in artistAlbums.items():
                    dirval   = albumVals["Dir"]
                    albumVal = albumVals["Album"]
                    ratio    = albumVals["Ratio"]
                    
                    dbAlbumName = albumVal["Name"]
                    dbAlbumCode = albumVal["Code"]
                    mediaType   = albumVal["MediaType"]


                    matchedDir = setDir(dirval, "Match")
                    mkDir(matchedDir)
                    
                    srcName = myAlbumName
                    srcDir  = setDir(dirval, srcName)
                    if not isDir(srcDir):
                        print("{0} does not exist".format(srcDir))
                        continue

                    mediaDir = setDir(matchedDir, discConv(mediaType))
                    mkDir(mediaDir)

                    if rename is True:
                        dstName = self.getMatchedDirName(discConv(dbAlbumName), dbAlbumCode, db)
                    else:
                        dstName = self.getMatchedDirName(myAlbumName, dbAlbumCode, db)

                    if show is True:
                        print('\t{0}'.format(mediaDir))
                        print("\t\t[{0}]".format(srcName))
                        print("\t\t[{0}]".format(dstName))
                        continue


                    dstDir  = setDir(mediaDir, dstName)
                    if isDir(dstDir):
                        print("{0} already exists".format(dstDir))
                        continue

                    print("\tMoving {0}  --->  {1}".format(srcDir, dstDir))
                    moveDir(srcDir, dstDir, debug=True)