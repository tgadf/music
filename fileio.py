# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 19:20:08 2017

@author: tgadfort
g"""

import yaml
from yaml import CLoader as Loader, CDumper as Dumper # from yaml-cpp
import json
import ujson
import pickle
import csv
import sklearn.externals.joblib as joblib
from pandas import read_csv

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fileinfo import getExt
from fsio import isFile


###############################################################################
#
# Joblib
#
###############################################################################
def saveJoblib(jlfile, jldata, compress = True, debug = False):
    if debug:
        print "Saving items using joblib to",jlfile

    joblib.dump(value=jldata, filename=jlfile, compress=compress)

def getJoblib(jlfile, debug = False):
    if not isFile(jlfile):
        raise ValueError(jlfile,"does not exist")
    if debug:
        print "Loading items using joblib from", jlfile
    jldata = joblib.load(jlfile)
    return jldata


###############################################################################
#
# CSV
#
###############################################################################
def saveCSV(yfile, ydata, debug = False):
    if debug:
        print "Saving",len(ydata),"items to",yfile

    with open(yfile, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in ydata:
            writer.writerow(line)            
    if debug:
        print "Saved results to",yfile

def getCSV(cfile, delimiter=",", debug = False, strip = False):
    if not isFile(cfile):
        raise ValueError(cfile,"does not exist")
    if debug:
        print "Loading items from", cfile
    cdata = csv.DictReader(open(cfile), delimiter=delimiter)
    if debug:
        print "Loaded",len(cdata),"items from",cfile
    return cdata




###############################################################################
#
# CSV to Pandas
#
###############################################################################
def saveCSVtoPandas(yfile, ydata, debug = False):
    if debug:
        print "Saving",len(ydata),"items to",yfile

    with open(yfile, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in ydata:
            writer.writerow(line)            
    if debug:
        print "Saved results to",yfile



def readCSVtoPandas(cfile, debug = False):
    if not isFile(cfile):
        raise ValueError(cfile,"does not exist")
    if debug:
        print "Loading items from", cfile,"to pandas"
    pddata = read_csv(cfile, low_memory=False)
    dim = ' x '.join([str(x) for x in pddata.shape])
    if debug:
        print "Read data with size {0}".format(dim)
    return pddata



###############################################################################
#
# YAML
#
###############################################################################
def saveYaml(yfile, ydata, debug = False):
    if debug:
        print "Saving",len(ydata),"items to",yfile
    yaml.dump(ydata, open(yfile, "w"), default_flow_style=False, allow_unicode = True, Dumper=Dumper)
    if debug:
        print "Saved results to",yfile

def getYaml(yfile, debug = False):
    if not isFile(yfile):
        raise ValueError(yfile,"does not exist")
    if debug:
        print "Loading items from",yfile
    ydata = yaml.load(open(yfile), Loader=Loader)
    #ydata = yaml.load(open(yfile))
    if debug:
        print "Loaded",len(ydata),"items from",yfile
    return ydata

def fixYaml(yfile, debug = True):
    ydata = yaml.load(open(yfile))
    saveYaml(yfile, ydata, debug)



###############################################################################
#
# JSON
#
###############################################################################
def saveJSON(jfile, jdata, debug = False):
    if debug:
        print "Saving",len(jdata),"items to",jfile
    ujson.dump(jdata, open(jfile, "w"))
    if debug:
        print "Saved results to",jfile

def getJSON(jfile, debug = False):
    if not isFile(jfile):
        raise ValueError(jfile,"does not exist")
    if debug:
        print "Loading items from",jfile
    jdata = ujson.load(open(jfile))
    if debug:
        print "Loaded",len(jdata),"items from",jfile
    return jdata

def fixJSON(jfile, debug = True):
    jdata = json.load(open(jfile))
    saveJSON(jfile, jdata, debug)



###############################################################################
#
# PICKLE
#
###############################################################################
def savePickle(pfile, pdata, debug = False):
    if debug:
        print "Saving",len(pdata),"items to",pfile
    pickle.dump(pdata, open(pfile, "w"))
    if debug:
        print "Saved results to",pfile

def getPickle(pfile, debug = False):
    if not isFile(pfile):
        raise ValueError(pfile,"does not exist")
    if debug:
        print "Loading items from",pfile
    pdata = pickle.load(open(pfile))
    if debug:
        print "Loaded",len(pdata),"items from",pfile
    return pdata
    
    
    
###############################################################################
#
# Plain Text
#
###############################################################################
def getText(tfile, debug = False):
    if not isFile(tfile):
        print tfile,"does not exist"
        return None

    data = open(tfile).readlines()
    data = [x.strip("\n") for x in data]
    data = [x.strip("\r") for x in data]
    return data
    

def getFile(tfile, debug = False):
    if not isFile(tfile, debug = False):
        print tfile,"does not exist"
        return None

    data = open(tfile)
    return data


def saveText(tfile, tdata, debug = False):
    f = open(tfile, "w")
    if isinstance(tdata, list):
        f.write("\n".join(tdata))
    elif isinstance(tdata, str):
        f.write(unicode(tdata, 'utf-8'))
    else:
        f.write(tdata)
    f.close()
        
    

###############################################################################
#
# General (get/save)
#
###############################################################################
def save(ifile, idata, debug = False):
    if idata == None:
        raise ValueError("No data in fileio.save()")
     
    # Test writeable
    # os.access('/path/to/folder', os.W_OK)
        
    ext = getExt(ifile)
    print "  Save() -->",ifile
    print "     ext -->",ext
    if ext == ".p":
        savePickle(pfile=ifile, pdata=idata, debug=debug)
    elif ext == ".json":
        saveJSON(jfile=ifile, jdata=idata, debug=debug)
    elif ext == ".yaml":
        saveYaml(yfile=ifile, ydata=idata, debug=debug)
    elif ext == ".dat" or ext == ".txt" or ext == ".data":
        saveText(tfile=ifile, tdata=idata, debug=debug)        
    elif ext == ".csv":
        saveCSV(cfile=ifile, cdata=idata, debug=debug)        
    else:
        raise ValueError("Did not recognize extension[",ext,"]")
      
          
def get(ifile, debug = False):
    if not isFile(ifile):
        raise ValueError("Get file",ifile,"does not exist")

    ext = getExt(ifile)
    if ext == ".p":
        return getPickle(pfile=ifile, debug=debug)
    elif ext == ".json":
        return getJSON(jfile=ifile, debug=debug)
    elif ext == ".yaml":
        return getYaml(yfile=ifile, debug=debug)
    elif ext == ".dat" or ext == ".txt" or ext == ".data":
        return getText(tfile=ifile, debug=debug)        
    elif ext == ".csv":
        return getCSV(cfile=ifile, debug=debug)
    else:
        raise ValueError("Did not recognize extension[",ext,"]")
                


