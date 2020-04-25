from timeUtils import clock, elapsed
from musicBase import myMusicBase

class myMatchedMusic:
    def __init__(self, mdb, debug=False):
        self.debug = debug
        self.mdb   = mdb
        self.mmb   = myMusicBase()
        
        self.unknownArtists = {}
        

    def getMatchStatus(self):
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
                if self.mdb.isKnown(artistName) is False:
                    self.unknownArtists[artistName] = artistPrimeDirs
                    if self.debug:
                        print("\tUnknown (All)     --> {0}".format(artistName))

        elapsed(start, cmt)
        print("Found {0} unknown artists".format(len(self.unknownArtists)))
        
        
    def getUnknownArtists(self):
        return self.unknownArtists