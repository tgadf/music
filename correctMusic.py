# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 14:07:18 2016

@author: tgadfort
"""

import json
import yaml
from collections import Counter
from os import walk, mkdir
from os.path import join, exists, splitext, basename, isdir, dirname, getsize
from difflib import get_close_matches
from shutil import copy, move
import sys
from mutagen.easyid3 import EasyID3
import urllib
from glob import glob
import pickle
import unicodedata as ud

def saveYaml(yfile, ydata):
    yaml.dump(ydata, open(yfile, "w"), default_flow_style=False, allow_unicode = True)

def getYaml(yfile):
    ydata = yaml.load(open(yfile))
    return ydata


def findNearest(item, ilist, num, cutoff):
    nearest = get_close_matches(item, ilist, n=num, cutoff=cutoff)
    return nearest


def findMatchingWord(item, ilist, num=None, cutoff=None):
    nearest = [x for x in ilist if x.find(item) != -1]
    return nearest


def form(val, size):
    while len(val) < size: val = val + " "
    return val


def getLocationData(itunesbase):
    locationfile = join(itunesbase, "TrimmedMusicLocations.json")
    print "Loading",locationfile
    locationdata = json.load(open(locationfile))
    print "Find",len(locationdata),"music data from",locationfile
    ldata = {}
    for k,v in locationdata.iteritems():
        ldata[v] = k
    
    return ldata


def getDiscogData(discogbase, itunesbase):
    discogfile = join(discogbase, "base-db", "artistMusicDB.json")
    if not exists(discogfile):
        discogfile = join(itunesbase, "base-db", "artistMusicDB.json")
    if not exists(discogfile):
        print "Could not find artistsMap.json anywhere...."
        raise()
    print "Loading",discogfile
    discog = json.load(open(discogfile))
    print "Find",len(discog),"music data from",discogfile

    dfile = {}
    for i,artist in enumerate(discog.keys()):
        if dfile.get(artist):
            print artist
        dfile[artist] = i
    return dfile


def getDiscogAndiTunes(discogbase, itunesbase):
    discog = getDiscogData(discogbase, itunesbase)
    
    itunesfile = join(itunesbase, "TrimmedMusic.json")
    print "Loading",itunesfile
    itunes = json.load(open(itunesfile))
    print "Find",len(itunes),"music data from",itunesfile
    
    return discog, itunes


def getFulliTunes(itunesbase):
    itunesfile = join(itunesbase, "FullMusic.json")
    print "Loading",itunesfile
    fullitunes = json.load(open(itunesfile))
    print "Find",len(fullitunes),"music data from",itunesfile
    
    return fullitunes


def checkCorrectionsFile(corrfile):
    try:
        corrections = getYaml(corrfile)
    except:
        print "Error with",corrfile
        raise()

    print "YAML is written correctly. Saving data to",corrfile
    saveYaml(corrfile, corrections)
        
        

def findCorrections(itunesbase, itunes, discog):
    corrfile = join(itunesbase, "corrections.yaml")
    scorrfile = join(itunesbase, "corrections.skip.yaml")
    ncorrfile = join(itunesbase, "corrections.new.yaml")
    pcorrfile = join(itunesbase, "corrections.pot.yaml")
    try:
        corrections = getYaml(corrfile)
        print "Found",len(corrections),"corrections from",corrfile
        skips = getYaml(scorrfile)
        print "Found",len(skips),"corrections from",scorrfile
        
    except:
        print "Could not open yaml file:",corrfile
        copy(corrfile, corrfile.replace(".yaml", ".tmp.yaml"))
        corrections = {}
        skips = {}
        
    print ""
    nmatch = {}
    pmatch = {}
    for i,artist in enumerate(sorted(itunes.keys())):

        if i % 1000 == 0:
            print i,'/',len(itunes),'\t',len(nmatch),'\t',len(pmatch)
            sys.stdout.flush()
            
        if skips.get(artist):
            continue
        
        if corrections.get(artist):
            corrval = corrections[artist]
        else:
            matches = findNearest(artist, discog.keys(), 1, 0.75)
            try: corrval = matches[0]
            except:
                matches = findNearest(artist, discog.keys(), 1, 0.7)
                if len(matches) > 0:
                    pmatch[artist] = matches[0]           
                continue
            
            #if len(corrections) > 100: break
        
            #fixdata[artist]["iTunes"] = findNearest(artist, itunes.keys(), 2, 0.95)
            #fixdata[artist]["iTunes"].remove(artist)
            if corrval:
                nmatch[artist] = corrval
                if artist != corrval or len(nmatch) % 50 == 0:
                    print i,'/',len(itunes),'\t',len(nmatch),'\t',len(pmatch),'\t',artist,'-->',corrval
                
                
    print "Saving",len(nmatch),"corrections",ncorrfile
    saveYaml(ncorrfile, nmatch)
    print "Saving",len(pmatch),"potential corrections",pcorrfile
    saveYaml(pcorrfile, pmatch)
    
    
def applyCorrections(corrfile):
    corrections = getYaml(corrfile)
    print "Found",len(corrections),"corrections from",corrfile
    
    for artist,artistdata in itunes.iteritems():
        if corrections.get(artist):
            corrval = corrections[artist]
            if corrval == artist:
                continue
            
            print "-->",artist
            for album,albumdata in artistdata.iteritems():
                err = albumdata["err"]
                if err: print "Error in album:",album
                for trkno,trkdata in albumdata["tracks"].iteritems():
                    tracks = []
                    if isinstance(trkdata,list):
                        for trk in trkdata:
                            tracks.append(trk["path"])
                    else:
                        tracks.append(trkdata["path"])
                        
                    for path in tracks:
                        path = urllib.url2pathname(urllib.unquote(str(path)))
                        path = path[7:]
                        if not exists(path):
                            print "Error! Can not find",path
                            raise()
                        
                        try:
                            audio = EasyID3(path)
                        except:
                            print "Error! Bad ID3 for",path
                            continue
    
                        try:
                            audio['artist'] = corrval
                        except:
                            print "Error! Writing artist correction to",path
                            continue
                        
                        audio.save()




########################################################################
########################################################################
########################################################################
########################################################################

def setCompilation(mp3, compVal):
    try:
        audio = EasyID3(mp3)
        audio['compilation'] = compVal
        audio.save()
        print "Setting compilation to",compVal,"for",mp3
        return True
    except:
        print "Could not setting compilation to",compVal,"for",mp3
    return False


def getCompilation(audio):
    compVal = None
    try:
        if audio.get('compilation'): compVal = audio['compilation'][0]
    except:
        compVal = None
    return compVal


def setArtist(mp3, artist):
    try:
        audio = EasyID3(mp3)
        audio['artist'] = artist
        audio.save()
        print "Setting artist",artist,"to",mp3
        return True
    except:
        print "Could not save artist",artist,"to",mp3
    return False


def getArtist(audio):
    artist = None
    try:
        if audio.get('artist'): artist = audio['artist'][0]
    except:
        artist = None
    return artist


def setAlbum(mp3, album):
    try:
        audio = EasyID3(mp3)
        audio['album'] = album
        audio.save()
        print "Setting album",album,"to",mp3
        return True
    except:
        print "Could not save album",album,"to",mp3
    return False


def getAlbum(audio):
    album = None
    try:
        if audio.get('album'): album = audio['album'][0]
    except:
        album = None
    return album
    
    
def getTrackNo(audio):
    tracknumber = None
    try:
        if audio.get('tracknumber'): tracknumber = audio['tracknumber'][0]
    except:
        tracknumber = None
    return tracknumber
    
    
def getInfo(mp3):    
    try:
        audio = EasyID3(mp3)
    except:
        return None, None, None, None, None
    artist      = getArtist(audio)
    album       = getAlbum(audio)
    trackno     = getTrackNo(audio)
    compilation = getCompilation(audio)
    try:
        other   = zip(audio.keys(), audio.values())
    except:
        other   = None
    return artist, album, trackno, compilation, other
        


def correctArtists(basedir, corrfile):
    sys.stdout.flush()
    corrections = getYaml(corrfile)
    
    files = glob(join(basedir, "Everything-*.json"))
    for ifile in files:
        fdata = json.load(open(ifile))
        print "Found",len(fdata),"files."
        ncorr = 0
        nmp3s = 0
        for i,fname in enumerate(fdata.keys()):
            nmp3s += 1
            info = fdata[fname]
            artist = info[0]
            #album  = info[1]

            if corrections.get(artist):
                corrval = corrections[artist]
                if corrval != artist:
                    if setArtist(fname, corrval) == False:
                        print "ERROR:::",artist,'  -->  ',corrval
                    else:
                        print i,'\t',artist,'  -->  ',corrval
                        info[0] = corrval
                        fdata[fname] = info
                        ncorr += 1


        print "Found",nmp3s,"mp3s from",ifile
        print "Corrected ",ncorr,"mp3s from",ifile
        print "Keeping",len(fdata),"mp3s from",ifile
        print ""
        json.dump(fdata, open(ifile, "w"))
        
        
def checkArtists(basedir, discog, corrfile):
    outfiles  = glob(join(basedir, "Artists-*.json"))
    artists   = {}
    for outfile in outfiles:
        db = json.load(open(outfile))
        for k in db.keys():
            artists[k] = 1
    artists = artists.keys()
        
    sys.stdout.flush()
    corrections = getYaml(corrfile)

    ncorr = {}
    discogs = sorted(discog.keys())
    print "Looping over",len(artists),"artists."
    NumCorr = 0
    NumDisc = 0
    for artist in artists:
        if corrections.get(artist):
            continue
        
        NumCorr += 1
        discval = None
        if discog.get(artist):
            continue
        else:
            NumDisc += 1
            matches = findNearest(artist, discogs, 1, 0.9)
            if len(matches) > 0: discval = matches[0]
            
        #matches = findNearest(artist, artists, 2, 0.9)
        #matches.remove(artist)
        if discval:
            try: print '{0: <30}'.format(artist),'\t',
            except: print artist,'\t\t',
            ncorr[artist] = discval
            try: print '{0: <30}'.format(discval)
            except: print discval
        else:
            if artist.find("&") == -1 and artist.find("feat.") == -1 and artist.find("Feat.") == -1 and artist.find("Ft.") == -1 and False:
                try: print '{0: <30}'.format(artist),'\t',
                except: print artist,'\t\t',
                print '-------'
            

    print "Found",NumCorr,"artists without a correction."
    print "Found",NumDisc,"artists not in discog list."
    ncorrfile = join(basedir, "corrections.new.yaml")
    print "Saving",len(ncorr),"corrections",ncorrfile
    saveYaml(ncorrfile, ncorr)


def cleanEverythingList(basedir, musicdir):
    outfiles  = glob(join(itunesbase, "Everything-*.json"))
    for outfile in outfiles:
        db = json.load(open(outfile))
        print "Found",len(db),"mp3s from",outfile
        mp3s = db.keys()
        for mp3 in mp3s:
            if not exists(mp3):
                del db[mp3]
        print "Keeping",len(db),"mp3s from",outfile
        json.dump(db, open(outfile, "w"))


def createEverythingList(basedir, musicdir):
    sys.stdout.flush()
    
    files = glob(join(basedir, "*.json"))
    for ifile in files:
        jname = splitext(basename(ifile))[0]
        ipath = join(musicdir, jname)
        if not isdir(ipath):
            print "Not a path",ipath
            continue
        fullpath = join(ipath, "iTunes Media", "Music")
        if not isdir(fullpath):
            print "Could not find iTunes Media/Music:",fullpath
            continue
        
        print "----->",fullpath
        db  = {}
        fdb = {}
        for directory, dirnames, filenames in walk(fullpath):
            for filename in filenames:
                fname = join(directory, filename)
                artist,album,trackno,compilation,other = getInfo(fname)
                if compilation: artist = "Compilation"
                if artist == None: continue
                if db.get(artist) == None:
                    db[artist] = {}
                if album == None: continue
                if db[artist].get(album) == None:
                    db[artist][album] = []
                db[artist][album].append(fname)
                fdb[fname] = [artist,album]
                if len(fdb) % 2500 == 0:
                    print "Files:",len(fdb),"\t\tArtists:",len(db)

        outfile  = join(basedir, "Everything-"+jname+".json")
        print "Saving",len(fdb),"artist files to",outfile
        sys.stdout.flush()
        json.dump(fdb, open(outfile, "w"))
            
        outfile  = join(basedir, "Artists-"+jname+".json")
        print "Saving",len(db),"artist files to",outfile
        sys.stdout.flush()
        json.dump(db, open(outfile, "w"))
            
    
    
def makeCamelCase(val):
    vals = val.split()
    if len(vals) > 1:
        nval = [x.title() if len(x) > 2 else x for x in vals]
        return " ".join(nval)
    return val
    
    
def getDiscogOrCorrectionFromValue(vals, discog, corrections):

    dvals = [x if discog.get(x) else None for x in vals]
    cvals = [x if corrections.get(x) else None for x in vals]

    retval = []    
    pvals  = []
    for i in range(len(vals)):
        rval = None
        if dvals[i]:   rval = dvals[i]
        elif cvals[i]: rval = cvals[i]

        retval.append(rval)

        pval = None
        if rval == None:
            matches = findNearest(vals[i], discog.keys(), 1, 0.9)
            if len(matches) > 0:
                pval = matches[0]
                print vals[i],'\t',pval
        
        pvals.append(pval)
            

    return vals, retval, pvals, all(retval)
    
def splitArtists(val, discog, corrections):
    featurings = [" Ft. ", " Featuring ", "/Feat ", "/FEAT ", " - Feat. ",
                  " - Feat ", " Feat. ", " w/ ", " Ft ", " Feat ", " ft "]
    for feature in featurings:
        vals = val.split(feature)
        if len(vals) > 1:
            corrs = getDiscogOrCorrectionFromValue(vals, discog, corrections)
            return corrs

    duets = ["Duet W/"]
    for duet in duets:
        vals = val.split(duet)
        if len(vals) > 1:
            corrs = getDiscogOrCorrectionFromValue(vals, discog, corrections)
            return corrs

    seperators = [" / ", "/", " & ", "; ", ", ", " - "]
    for seperator in seperators:
        vals = val.split(seperator)
        if len(vals) > 1:
            corrs = getDiscogOrCorrectionFromValue(vals, discog, corrections)
            return corrs
          
    vals = [val]
    corrs = getDiscogOrCorrectionFromValue(vals, discog, corrections)
    return corrs
    
    
def checkCamelCase(itunesbase, itunes, discog, corrfile):
    print "======================"
    print "| checkCamelCase()"
    print "======================"
    corrections = getYaml(corrfile)
    outfiles  = glob(join(itunesbase, "Everything-*.json"))
    artists   = Counter()
    for outfile in outfiles:
        db = json.load(open(outfile))
        for k,v in db.iteritems():
            artists[v[0]] += 1

    #print len(allartists)
    print len(discog)
    ncorr = {}

    togets=Counter()
    i = 0
    for item in artists.most_common():
        artist = item[0]
        counts = item[1]
        i += 1

    #for i,artist in enumerate(allartists):
        if discog.get(artist) != None or corrections.get(artist) != None:
            continue
        artist = makeCamelCase(artist)
        splitVals,corrVals,posCorrs,allFound = splitArtists(artist, discog, corrections)
        for j in range(len(corrVals)):
            if corrVals[j] == None:
                togets[splitVals[j]] += 1
            if posCorrs[j]:
                ncorr[splitVals[j]] = posCorrs[j]
                
        #print i,'\t',artist,'\t',counts
        #if not allFound:
        #    if splitVals: print ' ==>\t',allFound,'\t',splitVals,' ; ',posCorrs
        
    print ""
    print "================"
    for item in togets.most_common(100):
        print item[0]
    print "================"
        

    ncorrfile = join(itunesbase, "corrections.new.yaml")
    print "Saving",len(ncorr),"corrections",ncorrfile
    saveYaml(ncorrfile, ncorr)


def checkCompilationAlbums(itunesbase, itunes, discog, corrfile):
    print "\ncheckCompilationAlbums()\n"
    #corrections = getYaml(corrfile)

    unknowns  = ["Brooks & Dunn", "Lil Wayne & Juelz Santana", "Beam & Yanou", "BB King & Eric Clapton", "Billy Dixon And The Topics", "Bassey, Shirley", "Mr. Oizo & Gaspard Aug\u00e9", "2Pac & Notorious B.I.G.", "Master P, Afficial", "Abbot & Costello", "Billy Ray Cyrus, MileyCyrus", "Johnny Cash & June Carter", "Dolly Parton, Pam Tillis", "Belle & Sebastian feat. Norah Jones", "Dolly Parton, Willie Nelson", "Bill Haley & His Comets", "Aaron Neville & Celine Dion", "Beam And Yanou", "Barry, John Orchestra, The", "Dr. Dre & Snoop Doggy Dogg", "Barry White & Love Unlimited", "Dolly Parton, Porter Wagoner", "Frankie Valle And The Romans", "Frankie Valley And The Travelers", "Master P, Lil Jon", "Dolly Parton, Brad Paisley", "Chris Brown & Plies", "Lil Wayne & Juelz Santana Feat T.I.", "Full Blooded, The Hounds From Gert Town", "Jose Nunez & Octavina", "Dolly Parton, Alison Krauss, Ricky Skaggs, Mary Chapin Carpenter, Marty Stuart", "Master P, Silkk The Shocker, King George, Simply Dre", "KEAK THE SNEAK, E-40, JOE BEAST", "Master P, Curren$y", "Dolly Parton, Kenny Rogers", "Dolly Parton, Ricky van Shelton", "Cambatta Feat Hunt And Vic Damone", "J. Pich Ft. Young Jeezy And Ludacris", "Snoop Dogg Ft. Jay-Z And Ludacris", "Mobb Deep, Ice-T, Chuck D, Smooth B., Insane, RZA, Killah Priest, Shorty, DA Smart, Kam, Ice Cube", "Cosmos & Daft Punk", "Knight, Gladys", "Dispatch & OAR", "Jones, Tom", "Jones & Stephenson", "Chris Brown & Tank", "P. Diddy (feat. Usher, & Loon)", "Dolly Parton, Chet Atkins", "Dolly Parton, Linda Ronstadt, Emmylou Harris", "Chris Brown & Eva Simmons", "Dolly Parton, Osborne Brothers", "Dolly Parton, Rod Stewart", "Dolly Parton, Rodney Crowell, Lari White", "Jestofunk & Cinda", "Ludacris Ft. Twista And Rick Ross", "Master P, Silkk The Shocker, King George, C-Murder", "Kanye West ft. Ludacris & The Game", "Hal Miller And The Rays", "Juvenile, DMX, Jay-z, Ja Rule,", "Dolly Parton, Tammy Wynette, Loretta Lynn", "Kane, Able", "Master P, Ea-Ski, Rally Ral", "Norah Jones & Sasha Dobson", "Lil Wayne Feat Outkast & Snoop Dogg", "Master P, C-Murder, Lil Jon, Liberty", "Kid Rock and Sheryl Crow ", "Lil Wayne & Juelz Santana Feat Young Jeezy", "Chris Brown, Trey Songs & Game", "Kp And Envyi", "Dolly Parton, Collin Raye", "Ludacris Ft. Ciara And Pitbull", "C-Murder, Magic", "Chris Brown, Lil' Wayne & Swizz Beats", "Kid Rock, Limp Bizkit, Korn, Eminem", "Elton John & kd Lang", "Ludacris Ft. Rick Ross, Ciara, Twista, And Pitbull", "Hootie And The Blowfish", "Joe Jones And Ernie K. Doe", "J-Kwon vs. Lil' Kim & 50 Cent - ", "Master P, C-Murder, Fiend, Magic, Mr. Serv-On, Mia X, Big Ed, Silkk The Shocker, Mystikal", "Big Ed, Master P", "Norah Jones feat. Gillian Welch & David Rawlings", "Celine Dion & Aaron Neville", "Chris Brown & Lupe Fiesco", "Dolly Parton, Julio Iglesias", "Ludacris Ft. Ciara And Chris Brown", "Dolly Parton, Martina McBride", "Lil Wayne & Juelz Santana Feat Currency & Jay Bezel", "Master P, Vellqwan, Lil Romeo", "Magic, Mac", "Rollo & King", "Master P, C-Murder", "Kenny G, Michael Bolton, Sade", "Chris Brown & Sean Paul", "Dolly Parton, Mary Chapin Carpenter, Billy Ray Cyrus, Kathy Mattea, Pam Tillis ", "50 CENT, LLYOYD BANKS, BIG PUN", "Master P, Big Ed, King George, Silkk The Shocker, Lil Ric", "Gotti, Q.B., Pheno", "KLF & Tammy Wynette", "Drake Feat. Kanye West, Lil Wayne & Eminem"]
    unknowns += ["DJ VLAD", "Kanye West ft. DJ Khaled", "Dj Khaled Ft. Ludacris Snoop Dogg, Rick Ross, And T-Pain", "T-Pain (Ft. DJ Khaled Akon R. Kelly", "DJ Crack", "Eminem, Dj Vlad", "Notorious BIG, Busta Rhymes, Buju Banton, Dj Vlad"]

    unknowns = ["Compilation", "Missing Artist", "Unknown Artist", "artist", "To Do"]

    unknowns = ["Various Artists - RKO-Unique", "Elvis Costello-The Metropole Orchestra"]
    unknowns +=["Christmas"]

    unknowns  =["Barry Kleinbort", "Danko Manuel", "Merzbow - Gore Beyond Necropsy", "Dipset", "BLUES BROTHERS BAND"]
    unknowns +=["Frank Lini"]

    #unknowns = ["Stand - Up DK", "UT Pride of the Southland Marc", "Caruso"]
    
    unknowns = ["U2 Oakland Coliseum 110792 D1", "Western Hospitality 15"]

    unknowns = ["September 7th", "Duke Elington - Live at the Blue Note", "Beatsnblends"]
    unknowns+= ["Sing Along With Madeline", "Annie Cast", "English Patient ST", "Good Vs Ymcmb"]
    unknowns+= ["Waddie Mitchell"]
    
    unknowns = ["Beaver Creek", "Madeline"]
    
    unknowns = ["Ali_Vegas_&_L-Gee", "Greg Jacobs"]
    unknowns = ["Big Society Original Cast", "mixfiend.com", "Neil Young + Promise of the Real"]
    unknowns+= ["Ivan Pedersen Lecia J nsson"]

    unknowns = ["Cut", "Duct Tape Entertainment", "Original Motion Picture SoundTrack"]

    unknowns = ["Wu-Tang Family", "Suge White"]
    
    unknowns = ["Bill Erickson", "Foxfire", "Austin Powers The Spy Who Shagged Me", "Rob Luna"]
    
    unknowns = ["Another Hair Of The Dog"]
    unknowns += ["Chris Laurence-Elvis Costello-John Harle-Michael Tilson Thomas-Peter Erskine-The London Symphony Orchestra"]
    unknowns += ["The History of the English language", "U2 Oakland Coliseum 1997-6-18 D1", "David Zarefsky"]
    unknowns += ["Highstrung"]

    unknowns = ["Billy Joel (Richard Joo)", "Fare Thee Well: Celebrating 50 Years Of The Grateful Dead", "Va"]
    unknowns = ["Pearl Jam - 06-01-00 - Ireland", "Cambridge Singers directed by John Rutter"]
    unknowns+= ["J-Money"]
    
    unknowns = ["Rewiring Genesis", "Original Cast Recording", "Natural Born Killers"]

    unknowns = ["Various Country", "Chicago"]
    
    unknowns = ["various", "Eminem Vs. Lil' Wayne", "The Old Dan Tucker Band"]
    
    unknowns = ["Various / Trap-A-Holics", "Universiteskoret Lille MUKO", "Misc Compilations"]
    
    unknowns = ["Fare Thee Well: GD50", "Unrelated Segments &amp; Tidal Waves", "Jock Jams", "Logan de Gaulle vs. Pitbull"]
    
    unknowns = ["Tazzino", "bt", "Tone Tone", "Boo", "Avenue Q", "mnathanson2008-10-07cmc641", "N.E.R.D. (feat. Nelly Furtado)"]
    unknowns+= ["Community Audio", "More Abba Gold", "Battlecade Extreme Music Soundtrack", "Opera", "Philly Chase", "Fuse"]
    unknowns+= ["Academy Of St. Martin-In-The-Fields Under Neville Marriner"]
    
    unknowns = ["Prater Stadion Vienna Austria 7-16-92 (Fading Lights in Vienna 2.0)", "Cassidy", "Problem", "You", "Manu chao; Tonino Carotone"]
    unknowns+= ["Warren Haynes Featuring Railroad Earth", "Unk", "Down Boy Down", "Mo Beatz", "DFL", "The Lion King Cast", "u21983.06.01", "J-Hood"]

    unknowns = ["Rick Ross Gucci Mane Lil Wayne Drake Birdman", "Sd", "Cultus Sanguine", "Cyndi Lauper [www.musikaki.blogspot.com]", "Jimi Hendrix (w. Lonnie Youngblood)", "Heidi Grant Murphy - Aureole", "Trouble Is...", "Leon Russell-Willie Nelson", "World - Inferno Friendship Society", "Saunders - Garcia - Kahn - Vitt", "Sister Spit's Ramblin' Road Show", "SOUTH PARK MEXICAN", "Chainsaw", "Original Television Cast of the Wiz LIVE!", "U2CD1", "R09", "WAV ALBUMS"]
    
    unknowns = ["Pet Shop Boys Discography", "Various Artists - Birdman", "Raekwon Presents Ice Water", "94 East feat. Prince", "wz1982-10-22.Capitol", "Rick Ross Gucci Mane Lil Wayne Drake Birdman "]

    unknowns = ["The Tell-Tale Hearts", "S.B.O.E.", "Jackie-O Motherfucker", "1985-03-21 - Chicago", "M-I-2 SoundTrack", "1985-03-21", "John Cale-Lou Reed-Nico ?", "wz1996-01-16.Rack-n-Roll", "Anne Sofie Von Otter-Elvis Costello", "Sean Na-Na", "U2 Oakland Coliseum 1997-6-18 D2", "jim jones - dj crowd", "Anata Vs. Bethzaida", "N.P.G.", "John Cale-Lou Reed", "The Okra All-Stars", "Choir Of King's College - Cambridge", "Wilco-Billy Bragg", "The B. Lee Band", "Various Artists - EXWorks", "Flip-Side", "Frigg A-Go-Go", "My-Albums.com Backstreet Boys", "Extreme Noise Terror - Filthkick", "McNeely-Levin-Skinner Band", "Gil Evans - Miles Davis", "Dr. Tom Butt", "Niden Div. 187...", "L.A.P.D.", "Various Artists - Slewfoot", "ORF-Symphonie-Orchester", "C'Ville All-Stars", "Black Sabbath - Tony Martin", "Negru Voda - Third Eye", "Various Artists - Winter Harvest", "The Grown-Ups", "Andre Previn - Royal Philharmonic Orchestra", "M.I.J.", "ORF-Symphonie-Orcheste", "Allen Toussaint-Elvis Costello", "Full Monty-Soundtrack", "Dr. Frank", "Touchdown - Orthrelm", "Calvin Harris (Feat. Florence Welch)", "The Del-Gators", "Genesis P-Orridge With Splinter Test", "Gibson Bros.", "12 Lb. Test", "Gerrett G. Fagan", "Mug-Shot", "Cyber-Tec", "Emmylou Harris-Mark Knopfler", "Various Artists - Cleopatra Records", "St. Thomas", "Tech-9", "The De-Fenders", "wz1978-4-24.Live", "Svasti-ayanam", "Freni-Pavarotti-Ludwig", "Disciple A.D.", "Kap-G", "Kris Kristofferson-Willie Nelson", "Shady View Terrace - Lawrence Arms", "E. Coli", "Cadaver Inc.", "Ex-Fork", "Twista feat. Speedknot Mobstas", "LO-HI", "wz1976-06-20.Main", "Various Artists - American Music Partners", "Intro To Airlift - June Panic", "Dr. Dan", "Listen4ever.com", "Mrs. Hippie", "Witchman Vs. Jammin Unit", "Ost-David Bowie", "Flo-Rida ", "311-Omaha", "Blo.Torch", "Operation Ivy - Downfall - Rancid", "Calvin Harris (Feat. Ellie Goulding)", "Massive Attack vs. Mad Professor", "W.A. Mozart", "Rye Coalition - Karp", "Elliott Sharp - Carbon", "A.F.I.", "Neither-Neither World", "Dr.Alban vs Haddaway", "Calvin Harris (Feat. Ayah Marar)", "Cultus Sanguine vs. Seth", "www.homeofmusic.com", "K. Scott Ritcher", "Lonely Kings-Divit", "Unida - Dozer", "Dead Voices On Air Vs. Not Breathing", "764-HERO", "House of Pain vs. Micky Slim", "SR-71", "Calvin Harris (Feat. Kelis)", "Elvis Presley-The Sun Sessions", "Robert Miles feat. Nina Miranda", "Malcolm  Bruce - Kofi Baker Project", "Marc Et Claude feat Tony Hadle", "Calvin Harris (Feat. Example)", "Plus Ones - Travoltas", "Ex Number Five Vs. The Low End Theory", "Burnt By The Sun - Luddite Clone", "Snap! Feat. Niki Haris", "C'ville All-Stars", "Robert Miles feat. Kathy Sledge", "Metroschifter - Shipping News", "Snap! Feat. Summer", "Calvin Harris (Feat. Ne-Yo)", "House Of Pain - Legend (EP) ", "I.D.K.", "Integ 2000 - Fear Tomorrow", "B-52's", "Watershed-Hoarse", "A-Set", "Black Eyed Peas feat. Macy Gray", "Enrique Iglesias ft. Nadiya", "The Movielife - Ex Number Five", "Kanye West feat Daft Punk", "Teen Idols - Squirtgun", "Mr. Oizo & Gaspard Aug\u00e9", "Simon Wickham-Smith", "Snap! Feat. Rukmani", "Rick Ross-Rick Ross", "Jimi Hendrix ft. Jim Morrison", "Elvis Costello-The Dirty Dozen Brass Band", "Daft Punk vs. Prince", "K2 - AMK - Haters", "The Least You Can Do - Wake Up Call", "F.U.N", "N.I.N.A.", "Zach Forsberg-Lary", "Giant's Chair - Boys Life", "B.K.S", "Anna King (Duet w-Bobby Byrd)", "CoCo Lee - Yo-Yo Ma", "Madonna feat. Nicki Minaj", "Justin Timberlake featuring Jay-Z", "Beyonce Knowles Ft Jay-Z     y", "Juicy J-Katy Perry", "Pink Floyd - Is There Anybody", "SIMPLE MP3s - Westlife", "Flowchart - Her Space Holiday", "Miles Davis 11-01-69", "Puke-A-Rama", "BB King w- Albert Collins", "Flowchart - Smothered In Hugs", "Armand van Helden feat Duane H", "Rex - Songs: Ohia", "Molly McGuire - Iron Rite Mangle", "1983-03-24", "Artful Dodger - Re Rewind - http---come.to", "Pink Floyd - A Collection Of G", "BEN E. King", "Artful dodger ft. Craig David", "N.W.H.", "Shiner - Molly McGuire", "AlbumWrap - a", "Ludacris Ft. Mary J. Blige", "Lloyd ft. Lil Wayne", "Outkast feat. Cee-Lo", "The Mills Bros. Great Hits", "Hustler E.", "Justin Timberlake feat. Snoop Dogg", "Daft Punk vs. Daft Love", "Rod Stewart feat. Cee Lo Green", "Johnny Burnette-Rock 'N' Roll Trio", "Manie Fresh ft. jeezey", "Jagged Edge ft. Nelly", "Pigface-Chris Connelly", "Mint Condition-Phonte", "Chris Daughtry (Live-American Idol)", "Travie Mccoy Feat. Bruno Mars", "Cash-Perkin-Orbison-Lewis", "LMFAO feat. Natalia Kills", "Kinnda - K-=www.Impactmp3.net=-", "Janet Jackson feat. J. Cole", "Kanye West Feat. Dwele", "Janet Jackson feat. Missy Elliott", "Time-Life Music - The Rock'n'Roll Era", "Collective Soul-Elton John", "James Brown-Wilson Pickett", "Gloria Estefan-Chrissie Hynde", "Limp Bizkit-Limp Bizkit", "Fujioka Fujimaki - Nozomi Ohashi", "Rod Stewart feat. Michael Bubl\u00e9", "13 - Nancy Wilson", "50 Cent; Dr. Dre; Eminem", "SM-Trax", "http:--www.AudioUK.co.uk", "Various - Trap-A-Holics", "Daft Punk - Live", "D.A.D", "Kanye West feat John Mayer", "D.O.N.S", "C.B Milton", "Daft Punk vs. Michael Jackson", "C.J", "Justin Bieber ft. Ludacris", "Madonna vs. Daft Punk", "Lil' Buddy-Mint Condition", "Eve feat. Gwen Stefani", "Vengaboys - 05", "SuperMp3s.net - Anouk", "EFX Weapon Dance Mix of Art) -", "Sasha - Live", "Lil Wayne Feat P-Town Moe", "Badda Dan Dem feat Ward 21", "Eazy-E-Kokane", "J Star - Lil' Mokey", "Rod Stewart feat. Mary J. Blige", "Kid Rock f. Eminem", "Uk-WhiteLabel", "Ali Shaheed Muhammad-Mint Condition", "Daft Punk vs. Big Bang Theory", "Chris Brown feat. Soulja Boy", "Down By Law - Pseudo Heroes", "Jon Faddis-Kevin Mahogany", "D.J. Flapjack", "Chris Brown feat. T.Breezy", "L.O.X", "T.I ft Justin Timberlake", "Rudimental Feat. Ed Sheeran", "Seal Feat. Mikey Dread", "Chris Brown feat. Rich Girl", "Roots Rock Action Figures-RRAF", "O.R.M ( Only Real Music )", "Eminem - Freestyle (RARE) - Wa", "Anthony Hamilton-Mint Condition", "Mis-teeq (www.mp3sfinder.com)", "New Order-Ana Matronic", "Sheek Louch Feat. Green Lantern", "Fabolous ft. T-Pain", "Fatboy Slim-Armand Van Helden", "Enrique Iglesias ft. Pitbull", "Common feat. Macy Gray", "David Allan Coe/Lacy J. Dalton", "Fergie ft. Sean Kingston - httpil.com-forum", "Eddie St. James", "Pigface-Lab Report", "Taio Cruz Ft. Ludacris", "F.S.S. Stage Band", "Daft Punk vs. Chaka Khan", "Brian Eno-David Byrne", "The Saturdays Ft. Flo Rida ", "Eminem; Dr. Dre", "Rihanna f. Chris Brown", "Kelly Clarkson-Reba McEntire", "Clean Bandit Ft. Jess Glynne", "Madonna feat. Kanye West", "Mint Condition-Phife", "Diddy-Dirty Money", "John Legend Ft. Estelle", "BG. Ash Trey-Eazy-E-Mr.Roach Clip-Shaki", "Taio Cruz Ft. Travie McCoy", "Rod Stewart feat. Ella Fitzgerald", "Kanye West feat. Paul Wall", "Ludacris ft. T-Pain", "SIMPLEMP3s - Anastacia", "Reba Mcentire-Reba Mcentire", "Jordin Sparks Ft. Chris Brown", "Darude vs. Sander Van Doorn", "SlickF.B.", "50 Cent Ft. Justin Timberlake", "Carl Thomas - Lil' Mokey", "Madonna feat. Lil Wayne", "Justin Timberlake w- Jay-Z", "Alison Krauss-Robert Plant", "Lord G.", "Jock Jams - Black Box", "Gloria Estefan-Stevie Wonder", "Ludacris ft. Bobby Valentino- ", "DJEddieT.", "Fergie (feat. Will.I.Am)", "Tracy Nelson-Willie Nelson", "Rocko-Future-Rick Ross", "Rocky Top...Florida game", "Nick Cannon Feat. R. Kelly", "Nine Inch Nails-David Bowie", "Outkast feat. George Clinton", "www.VanStation.blogspot.com", "My-Albums.com - A1", "Fabolous - Lil' Mokey", "Black Menace-Mystikal", "Taio Cruz Feat. Ke$ha", "Kesha | www.RNBxBeatz.com", "Pan-Thy-Monium", "Shirley Collie-Willie Nelson", "Paul D. Rosenberg", "Johnny Cash - Dukes Of Hazzard", "Fiona Apple-Johnny Cash", "Chris Brown feat. La The Darkman", "Salt-n-Pepa", "Bon Jovi-Leann Rimes", "Mis-teeq", "No Doubt (www.mp3sfinder.com)", "X-Ecutioners", "Cee-Lo Green", "J. Frank Wilson", "Lupe Fiasco (feat. Jill Scott)", "SX-10", "jamie fox f- twista", "David Allan Coe/Evelyn C. Shapiro", "Madonna feat. Nas", "Willie Nelson-Leon Russell", "Kelly Clarkson Feat. Tamyra Gray", "J. Williams", "Live On 09-13-2000 -- Ac Dc 2000-09-13 Phoenix Arizona  Fm", "SIA vs. Booka Shade", "BG. Knocc Out-Eazy-E-Gansta Dresta", "Willie Nelson-Waylon Jennings", "The Beatles-The Beatles", "Nine Inch Nails - Things Falling Apart", "Twista feat. Dra Day", "Jay-Z Ft. Alicia Keys", "Dr. Dre; Eminem", "Madonna feat. M.I.A."]
    
    unknowns = ["Nashville Cast", "Work in progress", "Diverse kunstnere", "Tuna Universitaria De Granda", "The Intonations", "Scotty ATL", "Danmarks Radios Pigekor", "Pete Seeger with Studs Terkel"]
    
    unknowns = ["Peter Case With David Perales", "Eric Clapton with Mark Knopfler", "Emmylou Harris with The Band"]
    
    unknowns = ["Dolly Parton with Porter Wagoner", "History", "South Park"]
    
    unknowns = ["The Wild West", "George Bush", "Blue Ridge Mountain", "No Artist", "Kask", "02"]
    
    unknowns = ["Clash", "Grainger", "Hindemith"]
    
    unknowns = ["Zappa Fillmore", "No Artist Name", "Wally", "Javon Black"]
    unknowns+= ["Frank Jordan"]
    
    unknowns = ["Fair River Station", "Fontaine", "Its Nique", "1957 to 1967", "Cracker Duo", "U2 Oakland Coliseum 110792 D2"]
    
    unknowns = ["Ecstasy", "Kiley"]
    
    unknowns = ["Armin van Buuren presents", u"Unbekannter Künstler", "The Hunchback Of Notre Dame", "Moe Waveyy", "The Mambo Kings"]
    unknowns+= ["Maybaxh Hot", "Spacemonkeyz Versus Gorillaz"]
    
    unknowns = ["High School Musical", "Franklin"]
    
    unknowns = ["Gade", "Heritage", "Mitch Harrell", "Dorrough Music"]
    
    unknowns = ["Track Interpret"]

    outfiles  = glob(join(itunesbase, "Everything-*.json"))
    albums    = {}
    trkalbums = {}
    for outfile in outfiles:
        if outfile.find("Compilation") != -1: continue
        if outfile.find("Fix Artists") != -1: continue
        if outfile.find("Investigate") != -1: continue
        if outfile.find("Multiple Artists and DJs") != -1: continue
        db = json.load(open(outfile))
        for track,v in db.iteritems():
            album  = v[1]
            artist = v[0]
            #if album in copiedalbums: continue
            if artist not in unknowns: continue
            if not exists(track): continue
            #if album.find("") == -1: continue
            if albums.get(album) == None:
                albums[album] = Counter()
            albums[album][artist] += 1
            if trkalbums.get(album) == None:
                trkalbums[album] = {}
            trkalbums[album][track] = artist

    albumCntr = Counter()
    for album in albums.keys():
        albumCntr[album] = len(albums[album].keys())

    copies = []
    filesToCopy = {}
    for item in albumCntr.most_common():
        #if item[1] <= 5: continue
        print '\n\n',item[1],'\t',item[0],'\t'
        print "==>"
        for i,name in enumerate(sorted(trkalbums[item[0]].keys())):
            print "\t",basename(name),'\t',trkalbums[item[0]][name]
            #if i > 3: break
        copies.append(item[0])
        filesToCopy[item[0]] = trkalbums[item[0]].keys()
        
    print json.dumps(copies)
    json.dump(filesToCopy, open(join(itunesbase, "filesToCopy.json"), "w"))
    #setAndMoveCompilationAlbums(itunesbase, itunes, discog, corrfile)


def setAndMoveCompilationAlbums(itunesbase, itunes, discog, corrfile):
    outdir = "/Volumes/Music/iTunes Investigate/iTunes Media/Music"
    filesToCopy = json.load(open(join(itunesbase, "filesToCopy.json")))
    albums = filesToCopy.keys()

    for album in albums:
        albumdir = join(outdir, album)
        if not exists(albumdir):
            mkdir(albumdir)
        for mp3 in filesToCopy[album]:
            if not exists(mp3): continue
            artist,album,trackno,compilation,other = getInfo(mp3)
            if artist.find("/") != -1:
                artist = artist.replace("/", "-")
                setArtist(mp3, artist)
            artistdir = join(albumdir, artist)
            if not exists(artistdir):
                mkdir(artistdir)
            setCompilation(mp3, '1')
            dst = join(artistdir, basename(mp3))
            #print "move(",mp3,", ",dst,")"
            move(mp3, dst)


def setAndMoveInvestigateAlbums(itunesbase, itunes, discog, corrfile):
    outdir = "/Volumes/Music/iTunes Investigate/iTunes Media/Music"
    filesToCopy = json.load(open(join(itunesbase, "filesToCopy.json")))
    albums = filesToCopy.keys()
    

    for album in albums:
        albumdir = join(outdir, album)
        if not exists(albumdir):
            print albumdir
            mkdir(albumdir)
        for mp3 in filesToCopy[album]:
            if not exists(mp3): continue
    
            fdir      = dirname(mp3)
            albumDir  = basename(fdir)
            artistDir = basename(dirname(fdir))
            
            copydir = join(outdir, album)
            if not exists(copydir):
                mkdir(copydir)
                
            artistdir = join(copydir, artistDir)
            if not exists(artistdir):
                mkdir(artistdir)
                
            albumdir = join(artistdir, albumDir)            
            if not exists(albumdir):
                mkdir(albumdir)
            
            dst = join(albumdir, basename(mp3))
            move(mp3, dst)


def setAndMoveInvestigateArtists(itunesbase, itunes, discog, corrfile):
    outdir = "/Volumes/Music/iTunes Fix Artists/iTunes Media/Music"
    outdir = "/Volumes/Music/iTunes Multiple Artists and DJs/iTunes Media/Music"
    filesToCopy = json.load(open(join(itunesbase, "filesToCopy.json")))

    for dummy,mp3list in filesToCopy.iteritems():
        for mp3 in mp3list:
            #print exists(mp3),'\t',mp3
            if not exists(mp3): continue
            
            fdir      = dirname(mp3)
            albumDir  = basename(fdir)
            artistDir = basename(dirname(fdir))
            
            artistdir = join(outdir, artistDir)
            if not exists(artistdir):
                mkdir(artistdir)
                
            albumdir = join(artistdir, albumDir)
            if not exists(albumdir):
                mkdir(albumdir)
                        
            dst = join(albumdir, basename(mp3))
            move(mp3, dst)
    

def mergeWithDiscogs(itunesbase, itunes, discog, corrfile):
    outfiles      = glob(join(itunesbase, "Everything-*.json"))
    discogmapfile = join(itunesbase, "discogmap.yaml")
    artistDiscogMap = getYaml(discogmapfile)
    print "Found",len(artistDiscogMap),"artist <-> discog map entries."
    
    albums = json.load(open("/Volumes/Music/Discog/base-db/albumDB.json"))
    print "Found",len(albums),"discog albums."
    allAlbums = albums.keys()
    
    missingdiscog = Counter()
    missingdiscogdata = {}

    for outfile in outfiles:
        if outfile.find("Compilation") != -1: continue
        if outfile.find("Fix Artists") != -1: continue
        if outfile.find("Investigate") != -1: continue
        if outfile.find("Multiple Artists and DJs") != -1: continue
        print outfile
        db = json.load(open(outfile))
        for track,v in db.iteritems():            
            album  = v[1]
            artist = v[0]

            #if artist in ignores: continue
            #if artist in unknowns: continue

            #print artist,'\t',type(artist),'\t',
            #print ud.normalize('NFD', artist)
            uartist = ud.normalize('NFD', artist) #, artist.decode('utf-8'))
            #print uartist,'\t',type(discog.get(artist)),'\t',type(discog.get(uartist))

            uartist = artist
            if False:
                val = u'Céline Dion'
                print artistDiscogMap.get(val),'  (Uni)'
                val = ud.normalize('NFD', val)
                print val,'  (Norm)'
                print artistDiscogMap.get(val),'  (Norm)'
                val = "Céline Dion"
                print artistDiscogMap.get(val)
                print artistDiscogMap.get(u'Céline Dion')
                for k,v in artistDiscogMap.iteritems():
                    if k.find("Dion") != -1 or v.find("Dion") != -1:
                        print k,'\t->\t',v,'\t\t',type(k),'\t',type(v)
                f()

            discogentry = artistDiscogMap.get(uartist)
            if discogentry:
                if discog.get(discogentry) == None:
                    print artist
                    print discogentry
                    print "-->\t",findNearest(artist, discog.keys(), 20, 0.20)
                    print ''
                    f()
            else:
                if discog.get(uartist) == None:
                    missingdiscog[artist] += 1
                    if missingdiscogdata.get(artist) == None:
                        missingdiscogdata[artist] = {}
                    missingdiscogdata[artist][album] = 1
                else:
                    artistDiscogMap[artist] = artist


    print "Found",len(artistDiscogMap),"artist matches."
    print "Found",len(missingdiscog),"missing artist."

    djs = []                
    ands = []
    missing = {}
    j = 0
    kLevel = 2
    for item in missingdiscog.most_common(10000):
        artist = item[0]
        if artist.find("DJ ") != -1 or artist.find("Dj ") != -1:
            djs.append(artist)
            continue
        if artist.find(" & ") != -1 or artist.find(",") != -1 or artist.find(" And ") != -1 or artist.find(" and ") != -1:
            ands.append(artist)
            continue
        if artist.find(" feat ") != -1 or artist.find(" feat. ") != -1 or artist.find("-") != -1 or artist.find(".") != -1:
            ands.append(artist)
            continue
        if artist.find(" with ") != -1 or artist.find(" With ") != -1:
            ands.append(artist)
            continue
        #continue
        counts = item[1]
        missing[artist] = 1
        if kLevel == 1:
            if j > 50:
                break
        if kLevel == 0:
            continue
        

        if kLevel == 2:
            found = False
            for i,album in enumerate(sorted(missingdiscogdata[artist].keys())):
                if len(findNearest(album, allAlbums, 1, 0.95)) > 0:
                    found = True
                    break
            if found:
                print artist
                nearest2 = findMatchingWord(artist+" (", discog.keys())
                nearest3 = findMatchingWord("The "+artist, discog.keys())
                nearest  = list(set(nearest2 + nearest3))
                print "-->\t",", ".join(nearest)
                for i,album in enumerate(sorted(missingdiscogdata[artist].keys())):
                    print "\t",album,"\t\t",[albums[x] for x in findNearest(album, allAlbums, 1, 0.95)]
                print ''
                print ''
                j += 1
            continue
        
        #print counts,'\t',artist
        #continue
        #nearest1 = findNearest(artist, discog.keys(), 3, 0.50)
        nearest1 = []
        nearest2 = findMatchingWord(artist+" (", discog.keys())
        nearest3 = findMatchingWord("The "+artist, discog.keys())
        if len(nearest2) > 0:
            nearest = nearest2
        elif len(nearest3) > 0:
            nearest = nearest3
        else:
            nearest  = list(set(nearest1 + nearest2 + nearest3))
        if len(nearest) == 1:
            print artist
            print artist+": "+nearest[0]
            for i,album in enumerate(sorted(missingdiscogdata[artist].keys())):
                print "\t",album,"\t\t",albums.get(album)
                if i > 5: break
            print ''
            j += 1
        elif len(nearest) > 1:
            print artist
            print "-->\t",", ".join(nearest)
            for i,album in enumerate(sorted(missingdiscogdata[artist].keys())):
                print "\t",album,"\t\t",albums.get(album)
                if i > 5: break
            print ''            
            
            j += 1

    print "Saving",len(artistDiscogMap),"artist <-> discog map entries."
    saveYaml(discogmapfile, artistDiscogMap)

    savename = join(itunesbase, "missing.json")
    print "Saving",len(missing),"missing to",savename
    json.dump(missing, open(savename, "w"))

    print ""
    print "---- DJs ----"
    print json.dumps(djs)
    print "---- Ands ----"
    print json.dumps(ands)
    print ""


discogbase = "/Volumes/Music/Discog"
itunesbase = "/Users/tgadfort/Music/AllMyMusic"
discogbase = itunesbase
corrfile = join(itunesbase, "corrections.yaml")

musicdir = "/Volumes/Music"
discogbase = "/Volumes/Music/Discog"
#moveMusic(itunesbase, musicdir)

discog, itunes = getDiscogAndiTunes(discogbase, itunesbase)
itunesbase = "/Users/tgadfort/Music/MyMusic"

#checkCorrectionsFile(corrfile)
#checkCorrectionsFile(join(itunesbase, "discogmap.yaml"))


### Run this after I move files
#cleanEverythingList(itunesbase, musicdir)
#f()

#checkArtists(itunesbase, discog, corrfile)

#f()

#checkCamelCase(itunesbase, itunes, discog, corrfile)

newMoves = False
mergeDis = False
renameAr = False
create   = False

if True:
    newMoves = True
    mergeDis = True
    renameAr = True
else:
    mergeDis = True


if create:
    createEverythingList(itunesbase, musicdir)
    raise()

if renameAr:
    ## If there is an update to the correction yaml file run this
    correctArtists(itunesbase, corrfile)


if newMoves:
    checkCompilationAlbums(itunesbase, itunes, discog, corrfile)
    setAndMoveInvestigateArtists(itunesbase, itunes, discog, corrfile)
    cleanEverythingList(itunesbase, musicdir)

#setAndMoveCompilationAlbums(itunesbase, itunes, discog, corrfile)
#setAndMoveInvestigateAlbums(itunesbase, itunes, discog, corrfile)
#f()

if mergeDis:
    mergeWithDiscogs(itunesbase, itunes, discog, corrfile)

#findCorrections(itunesbase, itunes, discog)
#applyCorrections(corrfile)