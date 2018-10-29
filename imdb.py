# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:23:11 2016

@author: tgadfort
"""

from os.path import join
import re
from Discog import fileio,match
from time import time
from glob import glob
from collections import Counter

        
sentence1 = "What is a CEO"
sentence2 = "What is a geisha?"
sentence3 = "What is ``R.E.M.``?"
sentence4 = "What's SCUBA?"


########################################################################
## Find String with Starts W, Ends W
########################################################################
def findSwEw(sw, ew, s, debug = False):
    retval  = None
    if sw != None:
        retval  = re.match(r''+sw+'.*.'+ew+'$', s)
    else:
        retval  = re.match(r''+''+'.*.'+ew+'$', s)
    
    if retval:
        match = retval.group()
        if sw:
            match = match.replace(sw, "")
        match = match.replace(ew, "")
        match = match.strip()
        if debug:
            print "=>",match
        return True,match
        
    if debug:
        print "=> NONE"
    return False,None
    
    
    
def getMovieData(i,line):
    retval = line.split("\t")
    test   = retval[0]
    retval = retval[1:]
    retval = [x for x in retval if len(x) > 0]
    if len(retval) == 0:
        print "No idea what to do with",line
        raise()
    ism    = re.match(r'\"(.+?)\"',test)
    key    = None
    isTV   = False
    if ism:
        isTV = True
        key = ism.groups()[0].strip()
        extra = test.replace("\""+key+"\"", "").strip()
        retval.insert(0, extra)
        year = retval[-1]
    else:
        key = test.strip()
        year = retval[0]
        
    
    repl = " ("+year+")"
    pos  = key.find(repl)
    if pos > -1:
        key = key.replace(repl, "").strip()
    else:
        for ext in ["I", "II", "III", "IV"]:
            repl = " ("+year+"/"+ext+")"
            pos  = key.find(repl)
            if pos > -1:
                rep = " ("+ext+")"
                key = key.replace(repl, rep).strip()
                break


    try:
        year = int(year)
    except:
        year = -1
    
        
    if key == None:
        print "No idea how to parse:",i,line
        
    
    return key,isTV,year,retval


def getData(data):
    i = 0
    vals = []
    while i < len(data):
        if len(data[i]) == 0: break
        vals.append(data[i].split('\t'))
        i += 1
    return vals,i+1


def forwardData(data, sw, ew, debug = False):
    if debug: print "forwardData()"
    if debug: print "  Data Size -->",len(data)

    i = 0    
    fVal = None
    while i < len(data):
        retval,match = findSwEw(sw, ew, data[i].strip())
        if retval:
            fVal = match
            data = data[i+3:]
            break
        i += 1
        if i > 1000:
            print "Something is wrong with the header here..."
            raise()

    if fVal == None:
        print "No name for data..."
        return None

    if debug:
        print "Found good",fVal,"data of size",len(data)
    return fVal,data


def parseData(base = "/Volumes/Seagate/imdb/", fVal = None, header = True, data = None):
    if fVal == None:
        print "No name for data in parseData()"
        return
    if data == None:
        print "No data for",fVal,"in parseData()"
        return
    Nf = 1
    if header:
        header = data[0].split()
        data   = data[2:]
    
    fdata  = {}
    Ni = 0
    i = 0
    t = time()
    while i < len(data) - 10:
        if i % 250000 == 0 and i > 0:
            tt = round(time() - t, 1)
            print i,' \t',round(i/len(data),2),'\t',tt,'sec. \t',round((i/1000)/tt,1),'kN/sec'
        if header:
            retval,lval = getData(data)
            data        = data[lval:]
            key         = retval[0][0]
            fdata[key]  = retval
        else:
            key,isTV,year,retval  = getMovieData(i,data[i])
            i += 1
            if key == None:
                continue
            
            if isTV:
                continue
            
            if fdata.get(year) == None:
                fdata[year] = {}
            fdata[year][key] = year
            if len(fdata) % 10000 == 0:
                print len(fdata),'\t',key,'\t',len(retval),'\t',Ni,'\t',len(data)


    savename = join(base, "results", fVal+".p")
    print "   --->",savename
    fileio.save(ifile=savename, idata=fdata)
    Nf += 1
    fdata = {}
    
    
def parseMovie(line):
    full    = line
    role    = None
    extra   = None
    episode = None
    year    = None
    mtype   = None
    comment = None
    
    m = re.search(r"\s\s\<([A-Za-z0-9_]+)\>", line)
    if m:
        extra = m.group(1)
        line  = line.replace(m.group(), "")
        line  = line.strip()
                
    m = re.search(r"\[([^{]+)\]", line)
    if m:
        role = m.group(1)
        line = line.replace(m.group(), "")
        line = line.strip()
        
        
    m = re.search(r"\{\{([^}]+)\}\}", line)
    if m:
        comment = m.group(1)
        line    = line.replace(m.group(), "")
        line    = line.strip()
        
    pos = line.find(" (voice)")
    if pos > -1:
        comment = "Voice"
        line  = line.replace(" (voice)", "")
        line  = line.strip()

    pos = line.find(" (unconfirmed)")
    if pos > -1:
        comment = "Unconfirmed"
        line  = line.replace(" (unconfirmed)", "")
        line  = line.strip()
        
    pos = line.find(" (uncredited)")
    if pos > -1:
        comment = "Uncredited"
        line  = line.replace(" (uncredited)", "")
        line  = line.strip()
        
    pos = line.find(" (archive footage)")
    if pos > -1:
        comment = "Archive Footage"
        line  = line.replace(" (archive footage)", "")
        line  = line.strip()

    pos = line.find(" (also archive footage)")
    if pos > -1:
        comment = "Archive Footage"
        line  = line.replace(" (also archive footage)", "")
        line  = line.strip()
        
        
    m = re.search(r"\s\{([^}]+)\}", line)
    if m:
        episode = m.group(1)
        line    = line.replace(m.group(), "")
        line    = line.strip()

    pos = line.find(" (V)")
    if pos > -1:
        mtype = "V"
        line  = line.replace(" (V)", "")
        line  = line.strip()
        
    pos = line.find(" (TV)")
    if pos > -1:
        mtype = "TV"
        line  = line.replace(" (TV)", "")
        line  = line.strip()
        
    pos = line.find(" (VG)")
    if pos > -1:
        mtype = "VG"
        line  = line.replace(" (VG)", "")
        line  = line.strip()


    movie = line
    TV = False
    if len(movie) > 2:
        if movie[0] == '"':
            TV = True
    pattern = re.compile(r"\s\((\d{4})\)")
    vals = pattern.findall(movie)
    if len(vals) > 0: 
        year  = int(vals[0])
        repl = " ("+str(year)+")"
        movie = movie.replace(repl, "")
    
    pattern = re.compile(r"\s\((\d{4})/I\)")
    vals = pattern.findall(movie)
    if len(vals) > 0: 
        year  = int(vals[0])
        repl = " ("+str(year)+"/I)"
        movie = movie.replace(repl, " (I)")
    
    pattern = re.compile(r"\s\((\d{4})/II\)")
    vals = pattern.findall(movie)
    if len(vals) > 0: 
        year  = int(vals[0])
        repl = " ("+str(year)+"/II)"
        movie = movie.replace(repl, " (II)")
    
    pattern = re.compile(r"\s\((\d{4})/III\)")
    vals = pattern.findall(movie)
    if len(vals) > 0: 
        year  = int(vals[0])
        repl = " ("+str(year)+"/III)"
        movie = movie.replace(repl, " (III)")
    
    pattern = re.compile(r"\s\((\d{4})/IV\)")
    vals = pattern.findall(movie)
    if len(vals) > 0: 
        year  = int(vals[0])
        repl = " ("+str(year)+"/IV)"
        movie = movie.replace(repl, " (IV)")

    if year == None:
        if movie.find(" (????)") != -1:
            year = -1
            movie = movie.replace(" (????)", "")

    if year == None:    
        if not TV:
            #print "Not sure how to parse this line:",full
            #print "-->",movie
            comment = "BAD YEAR"
    

    retval={"Role": role, "Extra": extra, "Episode": episode,
            "Comment": comment,
            "Year": year, "Type": mtype, "TV": TV, "Movie": movie}
            
    if not TV and False:
        print full
        print retval
        raise()
    return retval
    
    
def getPeopleKey(name):
    m   = re.search(r"\s\(([^}]+)\)", name)
    ext = None
    if m:
        ext = m.group()
        name = name.replace(ext, "").strip()
        
    vals = name.split(', ')
    if len(vals) == 3:
        last  = vals[2]
        first = ", ".join(vals[:2])
        key = " ".join([first, last])
        if ext: key += ext
        return key
    elif len(vals) == 2:
        last  = vals[1]
        first = vals[0]
        key = " ".join([first, last])
        if ext: key += ext
        return key
    elif len(vals) == 1:
        if ext: name += ext
        return name
    else:
        print 'name -->',name
        print 'ext  -->',ext
        raise()
    
    
def parsePeopleData(base, f):    
    i = 0
    for line in f:
        line = line.replace("\n", "")
        retval,match = findSwEw("THE", "LIST", line.strip())
        if retval:
            fVal = match
            break
    
    i = 0
    for line in f:
        if i == 3: break
        i += 1

    i = 0
    Nf = 1
    fdata = {}
    name = None
    for line in f:
        line = line.replace("\n", "")
        vals = [x for x in line.split('\t') if len(x) > 0]
        i += 1
        if i % 200000 == 0:
            print i,'\t',name,'\t',vals
        if len(vals) == 2:
            name  = getPeopleKey(vals[0])
            movie = parseMovie(vals[1])
            fdata[name] = []
            if not movie["TV"]:
                fdata[name].append(movie)
        elif len(vals) == 1:
            if fdata.get(name) == None:
                fdata[name] = []
            movie = parseMovie(vals[0])
            if not movie["TV"]:
                fdata[name].append(movie)
        elif len(vals) == 0:
            if line.count('-') > 20:
                break
        if len(fdata) % 200000 == 0 and len(fdata) > 0:
            savename = join(base, "results", fVal+"-"+str(Nf)+".p")
            print "   --->",savename
            fileio.save(ifile=savename, idata=fdata)
            Nf += 1
            fdata = {}
                
    savename = join(base, "results", fVal+"-"+str(Nf)+".p")
    print "   --->",savename
    fileio.save(ifile=savename, idata=fdata)
    Nf += 1
    fdata = {}


    
def parseMovies(base = "/Volumes/Seagate/imdb/", name = "movies"):
    filename = join(base, name+".list")    
    data = fileio.getText(filename)
    fVal,data = forwardData(data, None, "LIST", debug = True)
    parseData(base, fVal = fVal, header = False, data = data)
    

def parsePeople(base = "/Volumes/Seagate/imdb/", name = "actors"):
    filename = join(base, name+".list")
    print "Getting people"
    f = fileio.getFile(filename)
    parsePeopleData(base, f)
    
    

def mergeMovies(base = "/Volumes/Seagate/imdb/"):
    movies = {}
    cntr   = Counter()
    for ifile in glob(join(base, "results", "MOVIES-*.p")):
        print ifile
        print cntr
        data    = fileio.getPICKLE(ifile)
        movs    = data.keys()
        for movie in movs:
            m = re.findall(r'\(([^()]+)\)', movie)
            try:
                year = int(m[-1])
            except:
                year = -1
            cntr[year] += 1
            if movies.get(year) == None:
                movies[year] =  {}
            movies[year][movie] = year
    savename = join(base, "results", "MOVIES.p")
    fileio.save(savename, movies)
    

def skimPeople(base = "/Volumes/Seagate/imdb/"):
    actors    = fileio.get(join(base, "results", "Actors.yaml"))
    
    actorfile = join(base, "results", "ACTORS.p")
    actordata = fileio.get(actorfile, debug=True)
    allActors = actordata.keys()
    actorfile = join(base, "results", "ACTORSnames.p")
    fileio.save(actorfile, allActors, debug=True)
    
    data = {}
    N = 0
    for actor in actors:
        if isinstance(actor, str):
            actor = unicode(actor, 'utf-8')
        results = actordata.get(actor)
        if results:
            data[actor] = results
            N += len(results)
            print "\tFound",actor,'w/',len(results),"\t",N
        else:
            nearest = match.findNearest(actor, allActors, 10, 0.5)
            print "\t",actor,'\t--->\t Could not find him.\t',nearest
    actorfile = join(base, "results", "ACTORSslim.p")
    print "N -->",N
    fileio.save(actorfile, data, debug = True)

    #actresses = fileio.get(join(base, "results", "Actresses.yaml"))


def slimPeople(base = "/Volumes/Seagate/imdb/", name = "ACTORS"):
    savename = join(base, "results", "MOVIES.p")
    print "Loading",savename
    movies = fileio.get(savename)

    fulldata = {}
    t = time()
    for ifile in glob(join(base, "results", name+"-*.p")):
        print "Loading",ifile
        data = fileio.getPICKLE(ifile)
        print "  --> Found",len(data)
        for i,person in enumerate(data.keys()):
            pmovies = data[person]
            person = getPeopleKey(person)

            if i % 50000 == 0 and i > 0:
                tt = round(time() - t, 1)
                #N  = len(fulldata)
                if tt > 0:
                    print i,'\t',len(fulldata),'\t',tt,'sec. \t',round((i/1000)/tt,1),'kN/sec'
                        
            for movie in pmovies:
                if movie["TV"]: continue
                if movie["Type"]: continue

                year = movie["Year"]
                film = movie["Movie"]

                val  = [year,film]
                if movies.get(year):
                    if movies[year].get(film) == None:
                        continue
                        if movie["Comment"]: continue
                        nearest = match.findNearest(movie["Movie"], movies[year].keys(), 1, 0.9)
                        if len(nearest) == 0: continue
                        val[1] = nearest[0]
                else:
                    continue

                if fulldata.get(person) == None:
                    fulldata[person] = []
                fulldata[person].append(val)


    savename = join(base, "results", name+".p")
    fileio.save(savename, fulldata)

                    
    

def getKnownMovies(outdir = "/Users/tgadfort/Movies"):
    savename = join(outdir, "officialMovies.yaml")
    movieDB = fileio.get(savename)
    print "Found",len(movieDB),"years of official movies in",savename
    return movieDB

