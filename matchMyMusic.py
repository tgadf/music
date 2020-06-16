from timeUtils import clock, elapsed
from musicBase import myMusicBase
from matchAlbums import matchAlbums
from ioUtils import getFile, saveFile
from fsUtils import isDir, setDir, mkDir, moveDir
from matchMusicName import myMusicName


class matchMyMusic:
    def __init__(self, mdb, debug=False):
        self.debug = debug
        self.mdb   = mdb
        self.mmb   = myMusicBase()
        self.mmn   = myMusicName()
        
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
                    if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                        continue
                        
                    if self.debug:
                        print("\tMy album: {0}".format(myAlbumName))
                    myFormattedAlbum = self.mmn.formatAlbum(myAlbumName, mediaType)

                    ma = matchAlbums(cutoff=ratioCut)
                    ma.match([myFormattedAlbum], mediaTypeAlbums)

                    if ma.maxval < ratioCut or ma.maxval > ratioCut+maxCut:
                        continue
                    if ma.maxval < bestMatchVal["Ratio"]:
                        continue

                    bestMatch = ma.getBestMatch(myFormattedAlbum)

                    bestMatchVal = {"Ratio": ma.maxval, "Dir": dirval, 
                                    "Album": {"Name": bestMatch["Name"],
                                              "Code": bestMatch["Code"],
                                              "MediaType": mediaType}}
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

        saveFile(ifile=self.mmn.moveFilename, idata=self.matchedAlbums, debug=True)
        print("Found {0} music <-> discogs albums maps".format(len(self.matchedAlbums)))
        

