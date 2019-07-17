from fsUtils import setDir, isDir, mkDir, setFile, isFile, setSubFile
from fileUtils import getBasename
from searchUtils import findExt, findDirsPattern
from ioUtils import getFile

##############################################################################################################################
# music Base Class
##############################################################################################################################
class musicBase():
    def __init__(self, basedir=None, debug=True):
        if debug:
            print("#"*60)
            print("## My Music")
            print("#"*60)
            print("")
        
        dbdir="db"
        datadir="data"
        resultsdir="results"
        self.dbdir      = dbdir
        self.datadir    = datadir
        self.resultsdir = resultsdir
        
        self.musicdir   = "/Volumes/Music"
        if isDir(self.musicdir):
            if debug:
                print("\tMusic Directory [{0}] Is Available\n\tWorking Online".format(self.musicdir))
            self.online = True
        else:
            if debug:
                print("\tMusic Directory [{0}] Is Not Available\n\tWorking Offline".format(self.musicdir))
            self.online = False
            
        self.musicdirpattern = "iTunes"
        self.musicext=[".mp3", ".Mp3", ".MP3"]
        

        self.musicdirpaths = findDirsPattern(basedir=self.getMusicDir(), pattern=self.musicdirpattern)
        self.musicClasses  = [getBasename(x) for x in self.musicdirpaths]
        
        if basedir is None:
            from os import getcwd
            self.basedir = getcwd()
        else:
            self.basedir = basedir

        if debug:
            print("\tBase Dir:    {0}".format(self.getBaseDir()))
            print("\tDB Dir:      {0}".format(self.getDBDir()))
            print("\tResults Dir: {0}".format(self.getResultsDir()))

        
        
    #######################################################
    ## Directories
    #######################################################
    def setDBDir(self, dbdir):
        self.dbdir=dbdir

    def setDataDir(self, datadir):
        self.datadir=datadir

    def setResultsDir(self, resultsdir):
        self.resultsdir
        
                    
    def getBaseDir(self):
        return self.basedir
    
    def getMusicDir(self):
        return self.musicdir
    
    def getDBDir(self):
        dirname = setDir(self.getBaseDir(), self.dbdir)
        if not isDir(dirname): mkDir(dirname)
        return dirname

    def getDataDir(self):
        dirname = setDir(self.getBaseDir(), self.datadir)
        if not isDir(dirname): mkDir(dirname)
        return dirname

    def getResultsDir(self):
        dirname = setDir(self.getBaseDir(), self.resultsdir)
        if not isDir(dirname): mkDir(dirname)
        return dirname
    
    
        
    #######################################################
    ## Directories
    #######################################################
    def getMusicClasses(self):
        return self.musicClasses
    
    def getMusicDirPaths(self):
        return self.musicdirpaths
    

        
    #######################################################
    ## DB Files
    #######################################################
    def getMusicListFile(self, cls):
        flist = getFile(setFile(self.getDBDir(), "{0}.p".format(cls)))
        return flist
    
    def getMusicListFiles(self):        
        files = findExt(basedir=self.getDBDir(), ext="*.p")
        files = [x for x in files if sum([y in x for y in ["Tags.p", "Paths.p"]]) == 0]
        print("Found {0} List Files".format(len(files)))
        return files

    
    def getMusicTagDB(self, cls):
        tagDB = getFile(setFile(self.getDBDir(), "{0}-Tags.p".format(cls)))
        return tagDB
    
    def getMusicTagDBs(self):
        files = findExt(basedir=self.getDBDir(), ext="*-Tags.p")
        print("Found {0} DB Files".format(len(files)))
        return files
    
    
    def getMusicPathDB(self, cls):
        pathDB = getFile(setFile(self.getDBDir(), "{0}-Paths.p".format(cls)))
        return pathDB
    
    def getMusicPathDBs(self):
        files = findExt(basedir=self.getDBDir(), ext="*-Paths.p")
        print("Found {0} DB Files".format(len(files)))
        return files
    
    