# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 19:20:08 2017

@author: tgadfort
"""

import yaml
import json
import pickle
from os.path import basename, splitext

###############################################################################
#
# YAML
#
###############################################################################
def saveYaml(yfile, ydata):
    yaml.dump(ydata, open(yfile, "w"), default_flow_style=False, allow_unicode = True)

def getYaml(yfile):
    ydata = yaml.load(open(yfile))
    return ydata



###############################################################################
#
# JSON
#
###############################################################################
def saveJSON(jfile, jdata):
    json.dump(jdata, open(jfile, "w"))

def getJSON(jfile):
    jdata = json.load(open(jfile))
    return jdata



###############################################################################
#
# PICKLE
#
###############################################################################
def savePICKLE(pfile, pdata):
    pickle.dump(pdata, open(pfile, "w"))

def getPICKLE(pfile):
    pdata = pickle.load(open(pfile))
    return pdata
    


###############################################################################
#
# General
#
###############################################################################
def save(ifile, idata):
    if isinstance(idata, pickle):
        savePICKLE(pfile=ifile, pdata=idata)
    elif isinstance(idata, json):
        saveJSON(jfile=ifile, jdata=idata)
    elif isinstance(idata, yaml):
        saveYaml(yfile=ifile, ydata=idata)
    else:
        print "Did not recognize format[",type(idata),"]"
        raise()
                
def get(ifile):
    ext = splitext(basename(ifile))[1]
    if ext == ".p":
        return getPICKLE(pfile=ifile)
    elif ext == ".json":
        return getJSON(jfile=ifile)
    elif ext == ".yaml":
        return getYaml(yfile=ifile)
    else:
        print "Did not recognize extension[",ext,"]"
        raise()