from pandas import DataFrame
from fsUtils import isDir, setDir
from fileUtils import getDirBasics, getBaseFilename
from listUtils import getFlatList
from searchUtils import findDirs, findAll, findNearest
from difflib import SequenceMatcher
from unicodedata import normalize
from os.path import join
from glob import glob
from timeUtils import clock, elapsed


def getAlbumTypes(dbKey=None, albumType="All", keys=False):    
    if keys is True:
        return [1, 2, 3, 4]

    if dbKey == "Discogs":
        allTypes  = ["Albums", "Singles & EPs", "Compilations", "Videos", "Miscellaneous"]
        primary   = ["Albums"]
        secondary = ["Compilations"]
        tertiary  = ["Singles & EPs"]
        fourth    = ["Videos", "Miscellaneous"] 
    elif dbKey == "AllMusic":
        allTypes  = ["Albums", "Single/EP", "Comp", "Video", "Other"]
        primary   = ["Albums"]
        secondary = ["Comp"]
        tertiary  = ["Single/EP"]
        fourth    = ["Video", "Other"]
    elif dbKey == "MusicBrainz":
        primary   = ["Album", "Album + Live", "Album + Soundtrack", "Album + Mixtape/Street", "Album + Remix", "Album + Audiobook", "Album + DJ-mix", "Album + Demo", "Album + Spokenword", "Album + Audio drama", "Album + Spokenword + Live", "Album + Soundtrack + Live", "Album + Remix + Mixtape/Street", "Album + Spokenword + Audiobook", "Album + Interview", "Album + Live + DJ-mix", "Album + Soundtrack + Remix", "Album + DJ-mix + Mixtape/Street", "Album + Interview + Live", "Album + Remix + DJ-mix", "Album + Live + Remix", "Album + Soundtrack + Audiobook", "Album + Interview + Demo", "Album + Soundtrack + Spokenword + Interview", "Album + Live + Demo", "Album + Soundtrack + Spokenword", "Album + Spokenword + Interview", "Album + Remix + Mixtape/Street + Demo", "Album + Demo + Audio drama", "Album + Soundtrack + Audiobook + Audio drama", "Album + Spokenword + Interview + Audiobook", "Album + Spokenword + Demo", "Album + Interview + Audiobook + Audio drama", "Album + Soundtrack + Audio drama", "Album + Soundtrack + Interview + Live", "Album + Audiobook + Audio drama", "Album + Audiobook + Live", "Album + Soundtrack + Demo"]
        secondary = ["Album + Compilation", "Album + Compilation + DJ-mix", "Compilation", "Album + Compilation + Live", "Album + Compilation + Soundtrack", "Album + Compilation + Remix", "Single + Compilation", "Album + Compilation + Mixtape/Street", "Album + Compilation + Live + DJ-mix", "Album + Compilation + Spokenword", "Album + Compilation + Demo", "Broadcast + Compilation", "Compilation + DJ-mix", "Album + Compilation + DJ-mix + Mixtape/Street", "Album + Compilation + Remix + DJ-mix", "Album + Compilation + Spokenword + Live", "Album + Compilation + Soundtrack + Remix", "Album + Compilation + Interview", "Compilation + Soundtrack", "Compilation + Live", "Broadcast + Compilation + Live", "Album + Compilation + Interview + Live", "Album + Compilation + Audio drama", "Album + Compilation + Audiobook", "Album + Compilation + Live + Demo", "Album + Compilation + Live + Remix", "Compilation + Live + DJ-mix", "Album + Compilation + Spokenword + Audiobook", "Broadcast + Compilation + Remix + DJ-mix", "Album + Compilation + Mixtape/Street + Demo", "Album + Compilation + Soundtrack + Interview", "Album + Compilation + Soundtrack + Spokenword + Interview + Audiobook + Remix", "Album + Compilation + Remix + Mixtape/Street", "Compilation + Remix", "Album + Compilation + Soundtrack + Demo", "Broadcast + Compilation + Audio drama"]
        tertiary  = ["Single", "EP", "EP + Live", "EP + Remix", "Single + Soundtrack", "Single + Live", "EP + Demo", "EP + Compilation", "EP + Soundtrack", "EP + Mixtape/Street", "Single + Demo", "Single + DJ-mix", "Single + Mixtape/Street", "EP + DJ-mix", "Single + Soundtrack + Remix", "Single + Audiobook", "EP + Compilation + Remix", "Single + Live + Remix", "EP + Live + Demo", "EP + Audio drama", "EP + Remix + Mixtape/Street", "Single + Audio drama", "Single + Soundtrack + Live", "EP + Soundtrack + Remix", "EP + Compilation + Live", "EP + Compilation + Mixtape/Street", "EP + Audiobook", "Single + Compilation + Remix", "Single + DJ-mix + Demo", "EP + Compilation + Remix + DJ-mix", "EP + Live + DJ-mix", "EP + Spokenword + Live", "Single + Remix + Mixtape/Street", "Single + Remix + Demo", "EP + Compilation + Demo", "Single + Mixtape/Street + Demo", "EP + Live + Remix", "Single + Spokenword", "Single + Interview", "EP + Compilation + Soundtrack", "EP + Interview"]
        fourth    = ["Unspecified type", "Other", "Single + Remix", "Other + Audiobook", "Other + Audio drama", "Other + Spokenword", "Live", "Remix", "Other + Compilation", "Broadcast", "Audiobook", "Other + Live", "Other + Demo", "Other + Interview", "Broadcast + Live", "Major series / box sets", "Sub Optimal Credits", "Soundtrack", "Broadcast + Audio drama", "Other + Mixtape/Street", "Currently known involved people:", "Demo", "The What The Fuck Serie:", "Mixtape/Street", "Other + DJ-mix", "A stab at the horrible Blue Note mess:", "Other + Soundtrack", "DJ-mix", "Broadcast + DJ-mix", "Spokenword", "Broadcast + Spokenword", "Broadcast + Audiobook", "Nonline discography:", "Other + Remix", "Other + Compilation + Live", "Other + Compilation + Audiobook", "Online discography:", "Former Official Homepage", "Current Members", "Don\'t add these albums here:", "Broadcast + Live + DJ-mix", "Other + Spokenword + Live", "Other + Spokenword + Audiobook", "Other + Spokenword + Audiobook + Audio drama", "Past Members", "Broadcast + Spokenword + Audio drama", "Audio drama", "Broadcast + Interview", "Other + Compilation + Spokenword", "Live + Demo", "Broadcast + Live + Audio drama", "Broadcast + Spokenword + Audiobook", "Other + Compilation + Demo", "Other + Compilation + Interview", "Broadcast + Demo", "Live + DJ-mix", "Other + Compilation + Live + DJ-mix", "DJ-mix + Mixtape/Street", "Other + Soundtrack + Mixtape/Street + Demo", "Zyklen/Reihen:", "Other + Compilation + DJ-mix", "Other + Audiobook + Audio drama", "Other + Compilation + Mixtape/Street", "Other + Remix + Mixtape/Street", "Other + Compilation + Interview + Live", "Broadcast + Soundtrack", "Other + Live + Demo", "Interview", "Jam Today (2)  1979 ~ 1980", "Other + Spokenword + DJ-mix + Mixtape/Street", "Other + Compilation + Remix", "Broadcast + Interview + Live"]        
        allTypes  = primary + secondary + tertiary + fourth
    elif dbKey == "AceBootlegs":
        allTypes  = ["Bootleg"]
        primary   = ["Bootleg"]
        secondary = []
        tertiary  = []
        fourth    = []
    elif dbKey == "RateYourMusic":     
        primary   = ["Album", "Live Album"]
        secondary = ['V/A Compilation', 'Compilation']
        tertiary  = ['Single', 'EP']
        fourth    = ['Bootleg / Unauthorized', 'Appears On', "Video"]        
        allTypes  = primary + secondary + tertiary + fourth
    elif dbKey == "LastFM":
        allTypes  = ["Albums"]
        primary   = ["Albums"]
        secondary = []
        tertiary  = []
        fourth    = []
    elif dbKey == "DatPiff":
        allTypes  = ["MixTape"]
        primary   = ["MixTape"]
        secondary = []
        tertiary  = []
        fourth    = []
    elif dbKey == "RockCorner":
        primary   = ["Albums"]
        secondary = []
        tertiary  = ["Songs"]
        fourth    = []     
        allTypes  = primary + secondary + tertiary + fourth
    elif dbKey == "CDandLP":
        primary   = ["Albums"]
        secondary = []
        tertiary  = []
        fourth    = []     
        allTypes  = primary + secondary + tertiary + fourth
    elif dbKey == "MusicStack":
        primary   = ["Albums"]
        secondary = []
        tertiary  = []
        fourth    = []     
        allTypes  = primary + secondary + tertiary + fourth
    elif dbKey == "MetalStorm":
        primary   = ["Albums"]
        secondary = []
        tertiary  = []
        fourth    = []
        allTypes  = primary + secondary + tertiary + fourth
    else:
        raise ValueError("Key is not known!")
        

    retval = {"All": allTypes, 1: primary, 2: secondary, 3: tertiary, 4: fourth}
    return retval[albumType]


def getOrganizedDBArtistAlbums(vals, dbKey):
    retval = {}
    for key in getAlbumTypes(dbKey, keys=True):
        albumTypes = getAlbumTypes(dbKey, key)        
        retval[key] = []
        for albumType in albumTypes:
            if vals.get(albumType) is not None:
                retval[key] += vals[albumType].values()
    return retval




def getArtistAlbums(discdf, idx):
    if not isinstance(discdf, DataFrame):
        raise ValueError("Not a DataFrame")
    
    try:
        artistAlbumsData = discdf[discdf.index == idx]
        artistAlbums     = artistAlbumsData["Albums"].to_dict().get(idx)
    except:
        return {}
        
    return artistAlbums


def getArtistIDX(artistMapData, db, discdf, debug=False):
    if not isinstance(artistMapData, dict):
        raise ValueError("No Artist Map Data")
    if not isinstance(discdf, DataFrame):
        raise ValueError("Not a DataFrame")        
    if not isinstance(artistMapData, dict):
        raise ValueError("artistMapData is not a DB!")

    if debug:
        print("ArtistMapData: {0} and DB: {1}".format(artistMapData, db))
    
    try:
        aMapData = artistMapData.get(db)
    except:
        if debug:
            print("DataBase [{0}] does not exist in artist map data".format(db))
        return None

    try:
        idx = aMapData.get('ID')
    except:
        if debug:
            print("ID and DataBase [{0}] does not exist in artist map data".format(db))
        return None
    
    ## Check
    if idx not in list(discdf.index):
        raise ValueError("ID {0} for {1} is not in the Index of the main DataFrame!".format(idx, db))
    
    return idx

def getArtistIDDBCounts(dbIDData):
    if isinstance(discogsIDData, DataFrame):
        return dbIDData.shape[0]
    return 0

def printArtistIDs(artistName, discogsArtistIDX, allmusicArtistIDX):
    print('\t{0: <40}{1: <15}{2: <15}'.format(artistName,str(discogsArtistIDX),str(allmusicArtistIDX)))

def printArtistIDDBResults(artistName, discogsIDData, allmusicIDData):
    print("\t{0: <40}{1: <15}{2: <15}".format("", 
                                              getArtistIDDBCounts(discogsIDData),
                                              getArtistIDDBCounts(allmusicIDData)))
    
def getMyMusicAlbums(dirval, returnNames=False):    
    discogMediaNames   = ['Albums', 'Singles & EPs', 'Compilations', 'Videos', 'Miscellaneous', 'Visual', 'DJ Mixes']
    allmusicMediaNames = ['Album']
    myMediaNames       = ['Random', 'Todo', 'Match', 'Title', 'Singles', 'Unknown', 'Bootleg', 'Mix']
    
    myMusicAlbums = [x for x in findDirs(dirval) if getDirBasics(x)[-1] not in discogMediaNames+allmusicMediaNames+myMediaNames]
    if returnNames is True:
        myMusicAlbums = [getDirBasics(x)[-1] for x in myMusicAlbums]
    return myMusicAlbums


def getMyMatchedMusicAlbums(dirval, byKey=False):  
    matchval = join(dirval, "Match", "*")
    matchedAlbums = []
    for dname in glob(matchval):
        
        matchedAlbums += [getDirBasics(x)[-1].split(" :: ")[0] for x in findDirs(dname)]
    return matchedAlbums


def getMyTodoMusicAlbums(dirval):
    todoAlbums = []
    for dval in ["Todo", "Album", "Title"]:
        todoval = join(dirval, dval)
        for dname in glob(todoval):
            todoAlbums += [getDirBasics(x)[-1] for x in findDirs(dname)]
    return todoAlbums


def getMyUnknownMusicAlbums(dirval):
    todoAlbums = []
    for dval in ['Unknown', 'Bootleg', 'Mix']:
        todoval = join(dirval, dval)
        for dname in glob(todoval):
            todoAlbums += [getDirBasics(x)[-1] for x in findDirs(dname)]
    return todoAlbums


def getMyRandomMusic(dirval):
    randomMusic = []
    for dval in ['Random']:
        todoval = join(dirval, dval)
        for dname in glob(todoval):
            randomMusic += [getBaseFilename(x) for x in findAll(dname)]
    return randomMusic


def getOrganizedArtistAlbums(vals, dbKey):
    if vals is None or not isinstance(vals, dict):
        return {}
    retval = {}
    for key in [1,2,3,4]:
        albumTypes = getAlbumTypes(dbKey, key)        
        retval[key] = []
        for albumType in albumTypes:
            if vals.get(albumType) is not None:
                retval[key] += vals[albumType].values()
    return retval


def getFlattenedArtistAlbums(vals):
    if vals is None:
        return []
    if isinstance(vals, dict):
        albums = []
        for k,v in vals.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    albums.append(v2)
            elif isinstance(v, list):
                for v2 in v:
                    albums.append(v2)
            else:
                raise ValueError("Need either a dict or list in getFlattenedArtistAlbums()")
        return list(set(albums))
    if isinstance(vals, list):
        albums = []
        for v in vals():
            if isinstance(v, list):
                for v2 in v:
                    albums.append(v2)
            else:
                raise ValueError("Need a list in getFlattenedArtistAlbums()")
        return list(set(albums))
    return []


def findPossibleArtistIDs(artistName, artistNameToID, artists, num=2, cutoff=0.7):
    possibleIDs    = artistNameToID.get(artistName)
    if possibleIDs is None:
        possibleIDs = set()
    else:
        possibleIDs = set(possibleIDs)
    newArtistNames = findNearest(artistName, artists, num, cutoff)
    for newArtist in newArtistNames:
        newPossibleIDs = artistNameToID.get(newArtist)
        possibleIDs = possibleIDs.union(set(newPossibleIDs))    
    possibleIDs  = list(possibleIDs)
    return possibleIDs


def getMultiMatchedDirs():
    baseDirs = ["/Volumes/Music/Multi/Matched", "/Volumes/Music/Jazz/Matched"]
    baseDirs = ["/Volumes/Music/Jazz/Matched"]
    return baseDirs


def getMatchedDirs():
    baseDirs = [x for x in ["/Volumes/Music/Matched", "/Volumes/Biggy/Matched"] if isDir(x)] #, "/Volumes/Music/Not In Discogs/Matched"]
    return baseDirs


def getVolumeName(baseDir):
    vals = getDirBasics(baseDir)
    return vals[2]


def getMatchedDir():
    baseDir = "/Users/tgadfort/matched"
    return baseDir



def getPrimeDirectory(artistName):
    start = artistName[0]

    import string
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
        
def getPrimeDirectories():    
    import string
    retvals  = [x for x in string.ascii_uppercase]
    retvals += ["Num", "Xtra", "The"]
    retvals  = sorted(retvals)
    return retvals


def getArtistNameDirvalsMap(artistName):
    primeDir   = getPrimeDirectory(artistName)
    dirvals    = []
    for matchedDir in getMatchedDirs():
        primeDirVal = setDir(matchedDir, primeDir)
        possibleDir = setDir(primeDirVal, normalize('NFC', artistName), forceExist=False)
        if isDir(possibleDir):
            dirvals.append(possibleDir)
    return dirvals


def getMatchedPrimeAlbumDirs(primeDir, matchedDirs):
    dirvals     = getFlatList([findDirs(setDir(matchedDir, primeDir)) for matchedDir in matchedDirs])
    artistNames = [normalize('NFC', getDirBasics(dirval)[-1]) for dirval in dirvals]
    return list(zip(artistNames, dirvals))


def getArtistPrimeDirMap(primeDir):
    matchedPrimeAlbumDirs = getMatchedPrimeAlbumDirs(primeDir, getMatchedDirs())
    artistPrimeDirMap     = {}
    for (artistName,dirval) in matchedPrimeAlbumDirs:
        if artistPrimeDirMap.get(artistName) is None:
            artistPrimeDirMap[artistName] = []
        artistPrimeDirMap[artistName].append(dirval)
    artistPrimeDirMap = {k: artistPrimeDirMap[k] for k in sorted(artistPrimeDirMap)}
        
    return artistPrimeDirMap


def getMultiArtistPrimeDirMap(primeDir):
    matchedPrimeAlbumDirs = getMatchedPrimeAlbumDirs(primeDir, getMultiMatchedDirs())
    artistPrimeDirMap = {}
    for (artistName,dirval) in list(zip(artistNames, dirvals)):
        if artistPrimeDirMap.get(artistName) is None:
            artistPrimeDirMap[artistName] = []
        artistPrimeDirMap[artistName].append(dirval)
    artistPrimeDirMap = {k: artistPrimeDirMap[k] for k in sorted(artistPrimeDirMap)}
        
    return artistPrimeDirMap


def getArtistNameMatchedDirs():
    retval = {}
    
    ######################################################################
    #### Loop Over Prime Directories
    ######################################################################
    for primeDir in getPrimeDirectories():
        artistPrimeDirMap = getArtistPrimeDirMap(primeDir)

        ######################################################################
        #### Loop Over Artist Name <-> Prime Map Items
        ######################################################################
        retval.update(artistPrimeDirMap)
        
    return retval


def getMyArtistNames():
    artistNames = []
    for primeDir in getPrimeDirectories():
        artistPrimeDirMap = getArtistPrimeDirMap(primeDir)
        artistNames += artistPrimeDirMap.keys()
    print("Found {0} Artists In My Matched Directories".format(len(artistNames)))
    return artistNames


def getMatchedStatusForMyArtists(mdb, onlyUnknown=False):
    start, cmt = clock("Matching All Music Artists")

    fullyUnknownArtistNames     = {}
    partiallyUnknownArtistNames = {}


    ######################################################################
    #### Loop Over My Artists and Paths
    ######################################################################
    artistNameMatchedDirs = getArtistNameMatchedDirs()
    for artistName, artistPrimeDirs in artistNameMatchedDirs.items():


        ######################################################################
        #### Get Database IDs
        ######################################################################
        if mdb.isKnown(artistName) is False:
            fullyUnknownArtistNames[artistName] = artistPrimeDirs
            print("\tUnknown (All)     --> {0}".format(artistName))
            continue
        else:
            if onlyUnknown is True:
                continue
            artistData = mdb.getArtistData(artistName)
            partiallyUnknownArtistNames[artistName] = {}
            for db,dbdata in artistData.items():
                if dbdata is None:
                    partiallyUnknownArtistNames[artistName][db] = artistPrimeDirs
                    print("\tUnknown (Partial [{1: <30}]) --> {0}".format(artistName, db))

    elapsed(start, cmt)
    
    retval = {"FullyUnknown": fullyUnknownArtistNames, "PartiallyUnknown": partiallyUnknownArtistNames}
    return retval



def analyzePartiallyUnknownArtists(matchedResults):
    start, cmt = clock("Finding Possible New Matches")

    num = 2
    cutoff = 0.50


    discogMediaNames   = ['Albums', 'Singles & EPs', 'Compilations', 'Videos', 'Miscellaneous', 'Visual', 'DJ Mixes']
    allmusicMediaNames = ['Album']
    myMediaNames       = ['Random', 'Todo', 'Match', 'Title', 'Singles']

    additions = {}

    print("{0: <40}{1}".format("Artist", "# of Albums"))
    for i,(artistName, unknownVals) in enumerate(matchedResults["PartiallyUnknown"].items()):
        print("{0: <40}".format(artistName))
        for dbKey in dbKeys:
            key = dbKey['Key']
            if key != "AceBootlegs":
                continue
            if unknownVals.get(key) is not None:
                dirvals = unknownVals[key]
                print("{0: <40}{1}".format(artistName, key))

                myMusicAlbums = []
                for dirval in dirvals:
                    myMusicAlbums += getMyMusicAlbums(dirval, returnNames=True) + getMyMatchedMusicAlbums(dirval) + getMyUnknownMusicAlbums(dirval)
                if len(myMusicAlbums) == 0:
                    continue
                print("{0: <40}There are {1} my albums".format(artistName,len(myMusicAlbums)))


                ## Find Possible IDs
                possibleIDs = findPossibleArtistIDs(artistName, artistNameToID[key], artists[key], num, cutoff)
                print("     Possible IDs ===>",len(possibleIDs))
                maxRat = None
                for possibleID in possibleIDs:
                    print("\t{0: <15}".format(possibleID), end="")
                    artistAlbums = getRowData(artistAlbumsDB[key], rownames=possibleID)['Albums']
                    artistAlbums = getFlattenedArtistAlbums(artistAlbums)          
                    print("\t{0: <10}".format(len(artistAlbums)), end="")


                    ## Find overlapping albums
                    retval = getBestAlbumsMatch(artistAlbums, myMusicAlbums, cutoff=cutoff, debug=False)                
                    print("\t",round(retval,2), end="")
                    if retval > cutoff:
                        if maxRat is None:
                            maxRat = retval
                        if retval < maxRat:
                            print("")
                            continue
                        maxRat = retval
                        if additions.get(artistName) is None:
                            additions[artistName] = {}
                        additions[artistName][key] = {"Score": retval, "Value": {'ID': possibleID, 'Name': None}}

                        print("\t{0: <15} is a match!".format(possibleID))
                    else:
                        print("")

    print("")
    print("Found {0} new matches".format(len(additions)))
    elapsed(start, cmt)
    
    return additions